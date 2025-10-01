from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://username:password@localhost:5432/ems_db"

    # Application Settings
    app_name: str = "EMS FastAPI Server"
    app_version: str = "1.0.0"
    debug: bool = True

    # Security
    secret_key: str = Field(..., alias="TOKEN_SECRET")
    algorithm: str = "HS256"
    access_expire_minutes: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_expire_minutes: int = Field(..., alias="REFRESH_TOKEN_EXPIRE_MINUTES")
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    api_prefix: str = "/ems/api/v1"  # API endpoints prefix

    # Microsoft Configuration
    client_id: str = "your-client-id-here"
    client_secret: str = "your-client-secret-here"
    redirect_uri: str = "your-redirect-uri-here"
    tenant: str = "your-tenant-here"

    # Microsoft Graph API Configuration (Email)
    azure_tenant_id: str
    azure_client_id: str 
    azure_client_secret: str 
    mail_from: str 

    # Google API Configuration
    google_api_key_1: str = "your-google-api-key-here"
    google_api_key_2: str = "your-google-api-key-here"
    google_api_key_3: str = "your-google-api-key-here"
    google_api_key_4: str = "your-google-api-key-here"
    google_api_key_5: str = "your-google-api-key-here"

    # OTP Configuration
    otp_expire_minutes: int = 5

    # mail configuraation
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    mail_tls: bool = True
    mail_ssl: bool = False
    use_credentials: bool = True

    # Logging Configuration
    log_level: str = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()
