from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://username:password@localhost:5432/ems_db"
    
    # Application Settings
    app_name: str = "EMS FastAPI Server"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    root_path: str = "/ems"  # Prefix for ingress
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()