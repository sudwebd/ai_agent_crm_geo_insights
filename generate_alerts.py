import base64
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from utils.google_authentication import oauth_2_authentication_flow

RECIPIENT_EMAIL = "sambharya88@gmail.com"

class AlertGenerator:
    def __init__(self, logger_instance: logging.Logger):
        self.logger = logger_instance

    def gmail_alert(self, body_html: str) -> None:
        try:
            self.logger.info("Starting gmail alert process.")
            gmail_service = self._authenticate_gmail()
            message = self._create_email_message(body_html)
            
            gmail_service.users().messages().send(
                userId="me", 
                body={"raw": message}
            ).execute()
            
            self.logger.info("Email sent successfully.")
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            raise

    def _create_email_message(self, body_html: str) -> str:
        message = MIMEMultipart()
        message["to"] = RECIPIENT_EMAIL
        message["subject"] = "AI Customer Data Insights Alert"
        message.attach(MIMEText(body_html, "html"))
        
        return base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode("utf-8")

    def _authenticate_gmail(self) -> build:
        return build("gmail", "v1", credentials=oauth_2_authentication_flow())
