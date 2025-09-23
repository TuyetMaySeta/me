from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class LoginRequestDTO(BaseModel):
    """Login request with employee ID and password"""
    employee_id: str = Field(..., description="Employee ID or email")
    password: str = Field(..., min_length=1, description="Employee password")
    remember_me: Optional[bool] = Field(False, description="Remember me for extended session")
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "password": "12345",
                "remember_me": False
            }
        }

class LoginResponseDTO(BaseModel):
    """Login response with tokens and user info"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds until access token expires
    employee: dict
    session_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "refresh_token_here",
                "token_type": "Bearer",
                "expires_in": 86400,
                "employee": {
                    "id": 1,
                    "email": "employee@company.com",
                    "full_name": "Employee Name",
                    "current_position": "Developer"
                },
                "session_id": "session_123"
            }
        }

class RefreshTokenRequestDTO(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")

class RefreshTokenResponseDTO(BaseModel):
    """Refresh token response"""
    access_token: str
    expires_in: int
    token_type: str = "Bearer"

class TokenVerificationDTO(BaseModel):
    """Token verification result"""
    valid: bool
    employee_id: Optional[int] = None
    email: Optional[str] = None
    session_id: Optional[str] = None
    expires_at: Optional[datetime] = None
