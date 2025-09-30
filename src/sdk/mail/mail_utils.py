import logging
from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Template

from src.config.config import settings

logger = logging.getLogger(__name__)


class MailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.mail_username,
            MAIL_PASSWORD=settings.mail_password,
            MAIL_FROM=settings.mail_from,
            MAIL_PORT=settings.mail_port,
            MAIL_SERVER=settings.mail_server,
            MAIL_STARTTLS=settings.mail_tls,
            MAIL_SSL_TLS=settings.mail_ssl,
            USE_CREDENTIALS=settings.use_credentials,
        )
        self.fm = FastMail(self.conf)
        self.template_dir = Path(__file__).parent / "templates"

    async def send_otp_email(self, recipient_email: str, otp_code: str, full_name: str):
        """Send OTP email"""
        template_path = self.template_dir / "otp_email.html"
        
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)
        html_body = template.render(name=full_name, otp_code=otp_code)

        message = MessageSchema(
            subject="Your OTP Code - SETA International",
            recipients=[recipient_email],
            body=html_body,
            subtype="html",
        )

        await self.fm.send_message(message)
        logger.info(f"OTP email sent to {recipient_email}")


mail_service = MailService()
