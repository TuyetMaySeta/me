from pydantic_settings import BaseSettings


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
    api_prefix: str = "/ems/api/v1"  # API endpoints prefix

    # Logging Configuration
    log_level: str = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # IAM Service Configuration
    iam_service_url: str = "http://localhost:8001"
    iam_username: str = "ems_service"
    iam_password: str = "ems_service_password"
    iam_timeout: int = 30

     # JWT Configuration
    jwt_secret_key: str = "Fj8w!2dks@1Lq8rKx9pVz6mNwQeYtHs"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    refresh_token_expire_days: int = 30

    # --- Session Configuration ---
    session_expire_days: int = 30
    max_sessions_per_user: int = 5

    # --- Security Settings ---
    password_min_length: int = 8
    password_max_length: int = 128
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    # --- Cookie Settings ---
    cookie_secure: bool = True  # Set False for local dev
    cookie_samesite: str = "strict"
    cookie_httponly: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()
