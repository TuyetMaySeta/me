from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class AuthenticationConfig(BaseSettings):
    """
    Authentication and Security Configuration Settings
    """
    
    model_config = {
        "extra": "ignore",  # Ignore extra fields from .env
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }
    
    # JWT Settings
    jwt_secret_key: str = Field(
        default="your-super-secret-jwt-key-change-in-production",
        description="Strong secret key for JWT token signing",
        min_length=32
    )
    
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    
    access_token_expire_minutes: int = Field(
        default=1440,  # 24 hours
        description="Access token expiry time in minutes",
        ge=1,
        le=10080  # Max 1 week
    )
    
    refresh_token_expire_days: int = Field(
        default=30,
        description="Refresh token expiry time in days",
        ge=1,
        le=365  # Max 1 year
    )
    
    # Session Settings
    session_expire_days: int = Field(
        default=30,
        description="Session expiry time in days",
        ge=1,
        le=365
    )
    
    remember_me_extend_days: int = Field(
        default=30,
        description="Additional days to extend session when remember_me is true",
        ge=1,
        le=365
    )
    
    # Cookie Settings
    cookie_secure: bool = Field(
        default=True,
        description="Set Secure flag on cookies (HTTPS only)"
    )
    
    cookie_samesite: str = Field(
        default="strict",
        description="SameSite cookie attribute for CSRF protection"
    )
    
    cookie_httponly: bool = Field(
        default=True,
        description="Set HttpOnly flag on cookies (XSS protection)"
    )
    
    cookie_domain: Optional[str] = Field(
        default=None,
        description="Cookie domain (None for current domain only)"
    )
    
    # Security Settings
    password_min_length: int = Field(
        default=8,
        description="Minimum password length requirement",
        ge=4,
        le=128
    )
    
    password_max_length: int = Field(
        default=128,
        description="Maximum password length to prevent DoS",
        ge=8,
        le=256
    )
    
    # Environment-based Configuration
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"
    
    def get_cookie_secure(self) -> bool:
        """Get cookie secure setting based on environment"""
        if self.is_development:
            return False  # Allow HTTP in development
        return self.cookie_secure
    
    def get_jwt_secret_key(self) -> str:
        """Get JWT secret key with environment override"""
        env_secret = os.getenv("JWT_SECRET_KEY")
        if env_secret:
            return env_secret
        
        if self.is_production and self.jwt_secret_key == "your-super-secret-jwt-key-change-in-production":
            raise ValueError("JWT_SECRET_KEY must be set in production environment")
        
        return self.jwt_secret_key
    
    def get_session_expire_seconds(self) -> int:
        """Get session expiry in seconds"""
        return self.session_expire_days * 24 * 60 * 60
    
    def get_access_token_expire_seconds(self) -> int:
        """Get access token expiry in seconds"""
        return self.access_token_expire_minutes * 60
    
    def get_remember_me_expire_days(self) -> int:
        """Get total expiry days when remember_me is enabled"""
        return self.session_expire_days + self.remember_me_extend_days
    



# Create global configuration instance
auth_config = AuthenticationConfig()


# Configuration validation
def validate_auth_config():
    """
    Validate authentication configuration settings
    
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate JWT secret key strength
    secret_key = auth_config.get_jwt_secret_key()
    if len(secret_key) < 32:
        raise ValueError("JWT secret key must be at least 32 characters long")
    
    # Validate algorithm
    if auth_config.jwt_algorithm not in ["HS256", "HS384", "HS512"]:
        raise ValueError("JWT algorithm must be one of: HS256, HS384, HS512")
    
    # Validate SameSite setting
    if auth_config.cookie_samesite not in ["strict", "lax", "none"]:
        raise ValueError("Cookie SameSite must be one of: strict, lax, none")
    
    # Validate expiry times
    if auth_config.access_token_expire_minutes > auth_config.session_expire_days * 24 * 60:
        raise ValueError("Access token expiry cannot be longer than session expiry")
    
    # Production security checks
    if auth_config.is_production:
        if not auth_config.get_cookie_secure():
            raise ValueError("Cookies must be secure in production")
        
        if auth_config.cookie_samesite == "none":
            raise ValueError("SameSite=None not recommended in production")


# Helper functions for common configuration access
def get_jwt_settings() -> dict:
    """Get JWT configuration as dictionary"""
    return {
        "secret_key": auth_config.get_jwt_secret_key(),
        "algorithm": auth_config.jwt_algorithm,
        "access_token_expire_minutes": auth_config.access_token_expire_minutes,
        "refresh_token_expire_days": auth_config.refresh_token_expire_days
    }


def get_cookie_settings() -> dict:
    """Get cookie configuration as dictionary"""
    return {
        "secure": auth_config.get_cookie_secure(),
        "samesite": auth_config.cookie_samesite,
        "httponly": auth_config.cookie_httponly,
        "domain": auth_config.cookie_domain
    }


def get_session_settings() -> dict:
    """Get session configuration as dictionary"""
    return {
        "expire_days": auth_config.session_expire_days,
        "remember_me_extend_days": auth_config.remember_me_extend_days,
        "expire_seconds": auth_config.get_session_expire_seconds()
    }


