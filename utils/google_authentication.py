from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
import os
import logging
from utils.constants import CREDENTIALS, TOKENS, SCOPES

def oauth_2_authentication_flow():
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
                return oauth_2_authentication_flow()
        else:
            logging.debug("No valid credentials available. Initiating OAuth flow.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKENS, "w") as token:
            token.write(creds.to_json())
            logging.debug("Saved new credentials to tokens file")
    return creds
