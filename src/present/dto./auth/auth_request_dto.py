from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic import field_validator
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
    """ "Verify old password and send OTP"""

    old_password: str = Field(..., min_length=6, description="Old password")

    class Config:
        json_chema_extra = {"example": {"old_password": "Seta123@"}}


class VerifyOTPRequestDTO(BaseModel):
    employee_id: int = Field(..., gt=0, description="Employee ID")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")

    class Config:
        json_schema_extra = {"example": {"employee_id": 1, "otp_code": "123456"}}

class ChangePasswordDTO(BaseModel):
    """Change password request"""
    employee_id: int = Field(..., gt=0, description="Employee ID")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")
    new_password: str = Field(..., min_length=6, description="New password (min 6 characters)")
    confirm_password: str = Field(..., min_length=6, description="Confirm new password")
    
    @field_validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": 1,
                "otp_code": "123456",
                "new_password": "NewPassword123@",
                "confirm_password": "NewPassword123@"
            }
        }
