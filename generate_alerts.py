import logging
import json
import os
import base64

from generate_llm_insights import generate_llm_insights
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils.google_authentication import *

RECIPIENT_EMAIL = "sambharya88@gmail.com"

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class generate_alerts():
    def __init__(self, logger):
        self.logger = logger

    def gmail_alert(self, body_html: str):
        self.logger.info("Starting gmail alert process.")
        gmail = self._authenticate_gmail()
        message = MIMEMultipart()
        message["to"] = RECIPIENT_EMAIL
        message["subject"] = "AI Customer Data Insights Alert"
        message.attach(MIMEText(body_html, "html"))
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        self.logger.debug("Sending email via Gmail API.")
        gmail.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        self.logger.info("Email sent successfully.")

    def _authenticate_gmail(self):
        return build("gmail", "v1", credentials=oauth_2_authentication_flow())
