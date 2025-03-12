import logging
import json
import os
import base64

from generate_llm_insights import generate_llm_insights
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS = "keys/credentials.json"
TOKENS = "keys/token.json"
RECIPIENT_EMAIL = "sambharya88@gmail.com"

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class generate_alerts():
    def gmail_alert(self, body_html: str):
        logger.info("Starting gmail alert process.")
        gmail = self._authenticate_gmail()
        message = MIMEMultipart()
        message["to"] = RECIPIENT_EMAIL
        message["subject"] = "AI Customer Data Insights Alert"
        message.attach(MIMEText(body_html, "html"))
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        logger.debug("Sending email via Gmail API.")
        gmail.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        logger.info("Email sent successfully.")

    def _authenticate_gmail(self):
        from google.oauth2.credentials import Credentials
        creds = None

        if os.path.exists(TOKENS):
            logger.debug("Token file found, loading credentials from token file.")
            creds = Credentials.from_authorized_user_file(TOKENS, SCOPES)
        else:
            logger.debug("Token file not found.")

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.debug("Refreshing expired credentials.")
                    creds.refresh(Request())
                except RefreshError:
                    logger.info("Refreshing credentials failed, deleting token and retrying.")
                    os.remove(TOKENS)
                    return self._authenticate_gmail()
            else:
                logger.debug("Initiating new credentials flow.")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
                creds = flow.run_local_server(port=0)
            logger.debug("Saving new credentials to token file.")
            with open(TOKENS, "w") as token:
                token.write(creds.to_json())
        return build("gmail", "v1", credentials=creds)
