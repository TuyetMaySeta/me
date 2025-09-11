from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from src.config.config import settings
from src.present.request.auth import LoginRequest, Token, ChangePasswordRequest
from src.core.services.user_service import UserService


class AuthController:
    """Authentication controller - handles auth requests and responses"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    def login(self, login_request: LoginRequest) -> Token:
        """Authenticate user and return access token"""
        user = self.user_service.authenticate_user(login_request.email, login_request.password)
        
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    def change_password(self, user_id: int, password_request: ChangePasswordRequest) -> dict:
        """Change user password"""
        self.user_service.change_password(
            user_id, 
            password_request.old_password, 
            password_request.new_password
        )
        
        return {"message": "Password changed successfully"}
