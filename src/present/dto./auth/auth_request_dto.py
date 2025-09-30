# src/present/dto/auth/auth_request_dto.py
from typing import Optional

from pydantic import BaseModel, Field,EmailStr

class LoginRequestDTO(BaseModel):
    """Login request with employee ID and password"""

    employee_id: int = Field(..., description="Employee ID")
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

class VerifyOldPasswordDTO(BaseModel):
    """"Verify old password"""
    old_password: str = Field(...,min_length =6, description = "Seta123@")
    class Config:
        json_chema_extra = {"example": {"old_password": "Seta123@"}}

class CreatOTP(BaseModel):
    email: EmailStr = Field(..., description ="a@example.com")
    class Config:
        json_chema_extra = {"example": {"email": "example@gmail.com"}}
class VerifyOTP(CreatOTP):
    otp_code: int = Field(..., ge=100000, le=999999, description="OTP code 6 chữ số")

