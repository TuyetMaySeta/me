# src/present/dto/auth/auth_response_dto.py
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class LoginResponseDTO(BaseModel):
    """Login response with tokens and user info"""

    access_token: str
    refresh_token: str
    expires_at: datetime
    employee: Dict[str, Any]
    session_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "refresh_token_here",
                "expires_in": 86400,
                "employee": {
                    "id": 1,
                    "email": "employee@company.com",
                    "full_name": "Employee Name",
                    "current_position": "Developer",
                },
                "session_id": 1,
            }
        }


class RefreshTokenResponseDTO(BaseModel):
    """Refresh token response"""

    access_token: str
    expires_in: datetime
    session_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "expires_in": 86400,
                "session_id": 100,
            }
        }


class TokenVerificationDTO(BaseModel):
    """Token verification result"""

    valid: bool
    employee_id: Optional[int] = None
    email: Optional[str] = None
    session_id: Optional[int] = None
    expires_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "employee_id": 1,
                "email": "employee@company.com",
                "session_id": 1,
                "expires_at": "2025-09-23T00:54:20Z",
            }
        }


class TokenInfoResponseDTO(BaseModel):
    """Token information response"""

    authenticated: bool
    token_found: bool
    token_valid: Optional[bool] = None
    employee_id: Optional[int] = None
    email: Optional[str] = None
    session_id: Optional[int] = None
    token_info: Optional[Dict[str, Any]] = None
    message: str
    action: str
    login_endpoint: Optional[str] = None
    error: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "authenticated": True,
                "token_found": True,
                "token_valid": True,
                "employee_id": 1,
                "email": "employee@company.com",
                "session_id": 1,
                "token_info": {
                    "employee_id": 1,
                    "email": "employee@company.com",
                    "issued_at": "2025-09-22T00:54:20Z",
                    "expires_at": "2025-09-23T00:54:20Z",
                    "is_expired": False,
                    "seconds_until_expiry": 86400,
                    "token_type": "access",
                    "jti": "token_id",
                },
                "message": "Token is valid",
                "action": "Continue",
            }
        }
