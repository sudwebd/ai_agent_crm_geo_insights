from utils.google_authentication import oauth_2_authentication_flow
from tqdm import tqdm
from keys.keys import *
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
        self.logger = logger
        self.gc = gspread.authorize(oauth_2_authentication_flow())
        logger.info("FetchCustomerData initialized")

    def fetch(self):
        try:
            sheet = self.gc.open(SHEET_NAME).sheet1
            data = pd.DataFrame(sheet.get_all_records())
            self.logger.info(f"Fetched {len(data)} records")
            return data
        except gspread.exceptions.APIError as e:
            self.logger.error(f"Google Sheets API error: {e}")
            if "insufficient authentication scopes" in str(e):
                self.logger.error("Please delete TOKENS file and re-authenticate")
            raise

class ProcessCustomerData:
    def __init__(self, logger):
        self.logger = logger
        self.fetcher = FetchCustomerData(logger)
        
    def _clean_address(self, address):
        return ' '.join(re.sub(r'[^a-zA-Z0-9\s,]', '', address).split())

    def _validate_data(self, df):
        try:
            # Convert data types
            df['Quantity Purchased'] = pd.to_numeric(df['Quantity Purchased'], errors='coerce').fillna(0).astype(int)
            df['Total Purchase Value (USD)'] = pd.to_numeric(df['Total Purchase Value (USD)'], errors='coerce').fillna(0.0)
            df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], errors='coerce')
            
            # Create and clean full address
            df['Full Address'] = df['Address'] + ', ' + df['City'] + ', ' + df['State'] + ', ' + df['Country']
            df['Full Address'] = df['Full Address'].apply(self._clean_address)
            
            # Remove rows with missing addresses
            df.dropna(subset=['Full Address'], inplace=True)
            
            self.logger.info(f"Validation complete. {len(df)} records remaining")
            return df
            
        except Exception as e:
            self.logger.error(f"Data validation error: {e}")
            raise

    def _geocode_address(self, address, retries=MAX_MAP_API_RETRIES):
        params = {'address': address, 'key': MAPS_API_KEY}
        
        try:
            time.sleep(0.1)  # Rate limiting
            response = requests.get(MAPS_BASE_URL, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'OK':
                    location = data['results'][0]['geometry']['location']
                    return location['lat'], location['lng']
                
            if retries > 0:
                self.logger.debug(f"Retrying geocoding: {address}")
                return self._geocode_address(address, retries - 1)
                
            self.logger.error(f"Geocoding failed for: {address}")
            return None, None
            
        except Exception as e:
            self.logger.error(f"Geocoding error: {e}")
            return None, None

    def _add_coordinates(self, df):
        df['lat'] = None
        df['lon'] = None
        
        for idx, row in tqdm(df.iterrows(), total=len(df)):
            lat, lon = self._geocode_address(row['Full Address'])
            df.loc[idx, ['lat', 'lon']] = [lat, lon]
            
        return df

    def get_data(self):
        df = self.fetcher.fetch()
        df = self._validate_data(df)
        return self._add_coordinates(df)
