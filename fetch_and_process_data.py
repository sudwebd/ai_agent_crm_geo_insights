from utils.google_authentication import *
from tqdm import tqdm
from keys.keys import MAPS_API_KEY
import gspread
import pandas as pd
import re
import time
import requests

SHEET_NAME = "Customer Data"
MAPS_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
MAX_MAP_API_RETRIES = 5

class FetchCustomerData:
    def __init__(self, logger):
        logger.info("Initializing FetchCustomerData instance")
        self.logger = logger
        self.gc = self._authenticate()
        
    def _authenticate(self):        
        return gspread.authorize(oauth_2_authentication_flow())

    def fetch_customer_data(self):
        self.logger.info("Fetching customer data from Google Sheets")
        try:
            sheet = self.gc.open(SHEET_NAME).sheet1
            data = sheet.get_all_records()
        except gspread.exceptions.APIError as e:
            self.logger.error("Error fetching data from Google Sheets: %s", e)
            if "insufficient authentication scopes" in str(e):
                self.logger.error("Insufficient authentication scopes. Delete the TOKENS file and re-authenticate.")
            raise
        df = pd.DataFrame(data)
        self.logger.info("Fetched %d records", len(df))
        return df

class ProcessCustomerData:
    def __init__(self, logger):
        self.logger = logger
        self.logger.info("Initializing ProcessCustomerData instance")
        self.cust_data_cl = FetchCustomerData(logger)

    def _clean_address(self, address):  
        cleaned_address = re.sub(r'[^a-zA-Z0-9\s,]', '', address)
        cleaned_address = re.sub(r'\s+', ' ', cleaned_address).strip()
        return cleaned_address

    def _validate_data(self):
        self.logger.debug("Validating and cleaning data")
        self.logger.debug("Data before validation: %s", self.df.head())
        self.logger.debug("Available columns: %s", self.df.columns)
        self.logger.debug("Data types before conversion: %s", self.df.dtypes)
        self.logger.debug("Number of rows before validation: %d", len(self.df))

        df = self.df

        # Validate Quantity Purchased
        try:
            self.logger.debug("Converting 'Quantity Purchased' to numeric.")
            df['Quantity Purchased'] = pd.to_numeric(df['Quantity Purchased'], errors='coerce').fillna(0).astype(int)
        except Exception as e:
            self.logger.error("Error converting 'Quantity Purchased': %s", str(e))
            raise

        # Validate Total Purchase Value
        try:
            self.logger.debug("Converting 'Total Purchase Value (USD)' to numeric.")
            df['Total Purchase Value (USD)'] = pd.to_numeric(df['Total Purchase Value (USD)'], errors='coerce').fillna(0.0).astype(float)
        except Exception as e:
            self.logger.error("Error converting 'Total Purchase Value (USD)': %s", str(e))
            raise

        # Validate Purchase Date
        try:
            self.logger.debug("Converting 'Purchase Date' to datetime.")
            df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], errors='coerce')
        except Exception as e:
            self.logger.error("Error converting 'Purchase Date': %s", str(e))
            raise

        # Construct Full Address
        try:
            self.logger.debug("Constructing 'Full Address'.")
            df['Full Address'] = df['Address'] + ', ' + df['City'] + ', ' + df['State'] + ', ' + df['Country']
        except KeyError as e:
            self.logger.error("Missing column for Full Address: %s", str(e))
            raise
        except Exception as e:
            self.logger.error("Error constructing 'Full Address': %s", str(e))
            raise

        # Clean Full Address
        try:
            self.logger.debug("Cleaning 'Full Address'.")
            df['Full Address'] = df['Full Address'].apply(self._clean_address)
        except Exception as e:
            self.logger.error("Error cleaning 'Full Address': %s", str(e))
            raise

        # Drop Rows with Missing Full Address
        try:
            self.logger.debug("Dropping rows with missing 'Full Address'.")
            df.dropna(subset=['Full Address'], inplace=True)
        except Exception as e:
            self.logger.error("Error dropping rows with missing 'Full Address': %s", str(e))
            raise

        # Final Log after Validation
        self.df = df
        self.logger.info("Data validation complete. %d records remaining", len(df))
        self.logger.debug("Data after validation: %s", self.df.head())

    def _geocode_address(self, address, retries=MAX_MAP_API_RETRIES):
        self.logger.debug("Geocoding address: %s", address)
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
                self.logger.debug("Geocoded address successfully: %s", address)
                return location['lat'], location['lng']
            else:
                self.logger.warning("Geocoding response not OK for address: %s, status: %s", address, data['status'])
        else:
            self.logger.error("HTTP error during geocoding for address: %s, status code: %s", address, response.status_code)
        
        if retries > 0:
            self.logger.debug("Retrying geocoding for address: %s. Retries left: %d", address, retries)
            return self._geocode_address(address, retries - 1)
        
        self.logger.error("Failed to geocode address after retries: %s", address)
        return None, None

    def _geocode_data(self):
        self.logger.debug("Starting geocoding of addresses")
        df = self.df
        df['lat'] = None
        df['lon'] = None
        for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
            address = row['Full Address']
            lat, lon = self._geocode_address(address)
            if lat is None or lon is None:
                self.logger.error("Failed to geocode address, Maps API not working: %s", address)
            df.loc[idx, 'lat'] = lat
            df.loc[idx, 'lon'] = lon
        self.logger.debug("Geocoding completed")
        return df

    def get_data(self):
        self.logger.info("Getting and processing customer data")
        self.df = self.cust_data_cl.fetch_customer_data()
        self._validate_data()
        processed_df = self._geocode_data()
        processed_df = self.df
        self.logger.debug("Data processing complete")
        return processed_df
