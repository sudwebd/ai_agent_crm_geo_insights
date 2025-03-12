import logging
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from tqdm import tqdm
from keys.keys import MAPS_API_KEY
import pandas as pd
import re
import os
import time
import requests

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

CREDENTIALS = "keys/credentials.json"
TOKENS = "keys/tokens.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive"]

SHEET_NAME = "Customer Data"
MAPS_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
MAX_MAP_API_RETRIES = 5

class FetchCustomerData:
    def __init__(self):
        logging.info("Initializing FetchCustomerData instance")
        self.gc = self._authenticate()
        
    def _authenticate(self):
        creds = None
        if os.path.exists(TOKENS):
            logging.debug("Loading credentials from tokens file")
            creds = Credentials.from_authorized_user_file(TOKENS, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logging.debug("Refreshing expired credentials")
                    creds.refresh(Request())
                except RefreshError:
                    logging.error("Error refreshing credentials. Removing tokens file and re-authenticating.")
                    os.remove(TOKENS)
                    return self._authenticate()
            else:
                logging.debug("No valid credentials available. Initiating OAuth flow.")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(TOKENS, "w") as token:
                token.write(creds.to_json())
                logging.debug("Saved new credentials to tokens file")
        
        return gspread.authorize(creds)

    def fetch_customer_data(self):
        logging.info("Fetching customer data from Google Sheets")
        try:
            sheet = self.gc.open(SHEET_NAME).sheet1
            data = sheet.get_all_records()
        except gspread.exceptions.APIError as e:
            logging.error("Error fetching data from Google Sheets: %s", e)
            if "insufficient authentication scopes" in str(e):
                logging.error("Insufficient authentication scopes. Delete the TOKENS file and re-authenticate.")
            raise
        df = pd.DataFrame(data)
        logging.info("Fetched %d records", len(df))
        return df

class ProcessCustomerData:
    def __init__(self):
        logging.info("Initializing ProcessCustomerData instance")
        self.cust_data_cl = FetchCustomerData()

    def _clean_address(self, address):  
        cleaned_address = re.sub(r'[^a-zA-Z0-9\s,]', '', address)
        cleaned_address = re.sub(r'\s+', ' ', cleaned_address).strip()
        return cleaned_address

    def _validate_data(self):
        logging.debug("Validating and cleaning data")
        logging.debug("Data before validation: %s", self.df.head())
        logging.debug("Available columns: %s", self.df.columns)
        logging.debug("Data types before conversion: %s", self.df.dtypes)
        logging.debug("Number of rows before validation: %d", len(self.df))

        df = self.df

        # Validate Quantity Purchased
        try:
            logging.debug("Converting 'Quantity Purchased' to numeric.")
            df['Quantity Purchased'] = pd.to_numeric(df['Quantity Purchased'], errors='coerce').fillna(0).astype(int)
        except Exception as e:
            logging.error("Error converting 'Quantity Purchased': %s", str(e))
            raise

        # Validate Total Purchase Value
        try:
            logging.debug("Converting 'Total Purchase Value (USD)' to numeric.")
            df['Total Purchase Value (USD)'] = pd.to_numeric(df['Total Purchase Value (USD)'], errors='coerce').fillna(0.0).astype(float)
        except Exception as e:
            logging.error("Error converting 'Total Purchase Value (USD)': %s", str(e))
            raise

        # Validate Purchase Date
        try:
            logging.debug("Converting 'Purchase Date' to datetime.")
            df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], errors='coerce')
        except Exception as e:
            logging.error("Error converting 'Purchase Date': %s", str(e))
            raise

        # Construct Full Address
        try:
            logging.debug("Constructing 'Full Address'.")
            df['Full Address'] = df['Address'] + ', ' + df['City'] + ', ' + df['State'] + ', ' + df['Country']
        except KeyError as e:
            logging.error("Missing column for Full Address: %s", str(e))
            raise
        except Exception as e:
            logging.error("Error constructing 'Full Address': %s", str(e))
            raise

        # Clean Full Address
        try:
            logging.debug("Cleaning 'Full Address'.")
            df['Full Address'] = df['Full Address'].apply(self._clean_address)
        except Exception as e:
            logging.error("Error cleaning 'Full Address': %s", str(e))
            raise

        # Drop Rows with Missing Full Address
        try:
            logging.debug("Dropping rows with missing 'Full Address'.")
            df.dropna(subset=['Full Address'], inplace=True)
        except Exception as e:
            logging.error("Error dropping rows with missing 'Full Address': %s", str(e))
            raise

        # Final Log after Validation
        self.df = df
        logging.info("Data validation complete. %d records remaining", len(df))
        logging.debug("Data after validation: %s", self.df.head())

    def _geocode_address(self, address, retries=MAX_MAP_API_RETRIES):
        logging.debug("Geocoding address: %s", address)
        time.sleep(0.1)
        params = {
            'address': address,
            'key': MAPS_API_KEY
        }
        response = requests.get(MAPS_BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                location = data['results'][0]['geometry']['location']
                logging.debug("Geocoded address successfully: %s", address)
                return location['lat'], location['lng']
            else:
                logging.warning("Geocoding response not OK for address: %s, status: %s", address, data['status'])
        else:
            logging.error("HTTP error during geocoding for address: %s, status code: %s", address, response.status_code)
        
        if retries > 0:
            logging.debug("Retrying geocoding for address: %s. Retries left: %d", address, retries)
            return self._geocode_address(address, retries - 1)
        
        logging.error("Failed to geocode address after retries: %s", address)
        return None, None

    def _geocode_data(self):
        logging.debug("Starting geocoding of addresses")
        df = self.df
        df['lat'] = None
        df['lon'] = None
        for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
            address = row['Full Address']
            lat, lon = self._geocode_address(address)
            if lat is None or lon is None:
                logging.error("Failed to geocode address, Maps API not working: %s", address)
            df.loc[idx, 'lat'] = lat
            df.loc[idx, 'lon'] = lon
        logging.debug("Geocoding completed")
        return df

    def get_data(self):
        logging.info("Getting and processing customer data")
        self.df = self.cust_data_cl.fetch_customer_data()
        self._validate_data()
        processed_df = self._geocode_data()
        logging.debug("Data processing complete")
        return processed_df
