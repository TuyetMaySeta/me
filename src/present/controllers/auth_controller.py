

import logging
from typing import Dict, Any
from fastapi import Request, Response

from src.core.services.auth_service import AuthService
from src.present.dto.auth.auth_dto import (
    LoginRequestDTO, 
    LoginResponseDTO,
    RefreshTokenRequestDTO,
    RefreshTokenResponseDTO
)
from src.config.config import settings

logger = logging.getLogger(__name__)

class AuthController:
    """Authentication controller handling HTTP requests"""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def login(self, 
              login_request: LoginRequestDTO, 
              request: Request,
              response: Response) -> LoginResponseDTO:
        """Handle employee login"""
        logger.info(f"Login request for: {login_request.employee_id}")
        
        try:
            # Authenticate employee
            auth_result = self.auth_service.login(
                employee_id=login_request.employee_id,
                password=login_request.password,
                remember_me=login_request.remember_me,
                request=request
            )
            
            # Set secure HTTP-only cookies
            self._set_auth_cookies(response, auth_result, login_request.remember_me)
            
            return LoginResponseDTO(**auth_result)
            
        except Exception as e:
            logger.error(f"Login failed for {login_request.employee_id}: {str(e)}")
            raise

    def refresh_token(self, 
                     refresh_request: RefreshTokenRequestDTO) -> RefreshTokenResponseDTO:
        """Handle access token refresh"""
        logger.info("Token refresh request")
        
        try:
            result = self.auth_service.refresh_access_token(
                refresh_request.refresh_token
            )
            
            return RefreshTokenResponseDTO(**result)
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify access token"""
        return self.auth_service.verify_token(token)

    def _set_auth_cookies(self, 
                         response: Response, 
                         auth_result: Dict[str, Any], 
                         remember_me: bool):
        """Set secure HTTP-only cookies for tokens"""
        
        # Access token cookie (shorter expiry)
        response.set_cookie(
            key="access_token",
            value=auth_result["access_token"],
            max_age=settings.access_token_expire_minutes * 60,
            httponly=True,
            secure=True,  # HTTPS only in production
            samesite="lax"
        )
        
        # Refresh token cookie (longer expiry if remember_me)
        refresh_max_age = (
            settings.refresh_token_expire_days * 24 * 60 * 60 
            if remember_me 
            else 24 * 60 * 60  # 1 day default
        )
        
        response.set_cookie(
            key="refresh_token",
            value=auth_result["refresh_token"],
            max_age=refresh_max_age,
            httponly=True,
            secure=True,
            samesite="lax"
        )
