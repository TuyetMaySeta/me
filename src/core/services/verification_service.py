

import logging
from pathlib import Path
from typing import Optional
import msal
import requests
from jinja2 import Template

from src.config.config import settings

logger = logging.getLogger(__name__)


class MailService:
    def __init__(self):
        self.client_id = settings.azure_client_id
        self.client_secret = settings.azure_client_secret
        self.tenant_id = settings.azure_tenant_id
        self.sender = settings.mail_from

        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]

        # Create MSAL app
        self.app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )
        self.template_dir = Path(__file__).resolve().parents[2] / "templates"
        
        logger.info("Microsoft Graph Mail Service initialized.")

    def _get_access_token(self) -> Optional[str]:
        """Acquire access token from Microsoft Identity platform"""
        try:
            result = self.app.acquire_token_for_client(scopes=self.scope)
            if "access_token" in result:
                return result["access_token"]
            else:
                error = result.get("error","Unknown error")
                error_desc = result.get("error_description","No description")
                logger.error(f"Error acquiring token: {error} - {error_desc}")
                return None
        except Exception as e:
            logger.error(f"Exception while acquiring token: {e}")
            return None

    async def send_otp_email(self, recipient_email: str, otp_code: str, full_name: str):
        """Send OTP email"""
        try:
            #Get access token
            token = self._get_access_token()
            if not token:
                logger.error("Failed to acquire access token.")
                return
            template_path = self.template_dir / "otp_email.html"

            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            template = Template(template_content)
            html_body = template.render(name=full_name, otp_code=otp_code)

            #Microsoft Graph API endpoint
            url = f"https://graph.microsoft.com/v1.0/users/{self.sender}/sendMail"
            email_msg = {
                "message": {
                    "subject": "Your OTP Code - SETA International",
                    "body": {
                        "contentType": "HTML",
                        "content": html_body
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": recipient_email}}
                    ]
                },
                "saveToSentItems": "true"
            }

            # send email
            response = requests.post(
                url,
                headers ={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json = email_msg
            )
             # Check response
            if response.status_code == 202:
                logger.info(f"OTP email sent successfully to {recipient_email}")
            else:
                logger.error(
                    f" Failed to send email. Status: {response.status_code}, "
                    f"Response: {response.text}"
                )
                raise Exception(f"Email sending failed: {response.text}")
                
        except Exception as e:
            logger.error(f"Error sending OTP email: {str(e)}")
            raise


# Global instance
mail_service = MailService()
