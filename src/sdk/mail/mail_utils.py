import logging
from typing import List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from src.config.config import settings

logger = logging.getLogger(__name__)

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_tls,
    MAIL_SSL_TLS=settings.mail_ssl,
    USE_CREDENTIALS=settings.use_credentials,
)


async def send_otp_email(recipient_email: str, otp_code: str, full_name: str):
    """Send OTP email"""
    subject = "Your OTP Code for Password Change"
    
    message_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OTP Verification</title>
    </head>
    <body>
        <div style="width:100%;font-family: monospace;">
            <h1>Hello, {full_name}</h1>
            <p>You have requested to change your password. Please use the OTP code below to verify:</p>
            <div style="background-color:#f4f4f4;padding:20px;text-align:center;margin:20px 0;">
                <h2 style="color:#1f8feb;font-size:32px;letter-spacing:5px;">{otp_code}</h2>
            </div>
            <p><strong>This OTP will expire in 1 minute.</strong></p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>For security reasons, never share this OTP with anyone.</p>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[recipient_email],
        body=message_body,
        subtype="html",
    )

    fm = FastMail(conf)
    await fm.send_message(message)
    logger.info(f"OTP email sent to {recipient_email}")
