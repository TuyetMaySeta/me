# src/present/dto/auth/auth_request_dto.py
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequestDTO(BaseModel):
    """Login request with employee ID and password"""

    employee_id: str = Field(..., description="Employee ID or email")
    password: str = Field(..., min_length=1, description="Employee password")
    remember_me: Optional[bool] = Field(
        False, description="Remember me for extended session"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "password": "12345",
                "remember_me": False,
            }
        }


class RefreshTokenRequestDTO(BaseModel):
    """Refresh token request"""

    refresh_token: str = Field(..., description="Refresh token")

    class Config:
        json_schema_extra = {"example": {"refresh_token": "refresh_token_here"}}
