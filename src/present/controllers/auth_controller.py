import logging
from typing import Any, Dict

from fastapi import Request, Response

from src.core.services.auth_service import AuthService
from src.present.dto.auth.auth_request_dto import (
    LoginRequestDTO,
    RefreshTokenRequestDTO,
)
from src.present.dto.auth.auth_response_dto import (
    LoginResponseDTO,
    RefreshTokenResponseDTO,
)

logger = logging.getLogger(__name__)


class AuthController:
    """Authentication controller handling HTTP requests"""

    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def login(
        self, login_request: LoginRequestDTO, request: Request, response: Response
    ) -> LoginResponseDTO:
        """Handle employee login"""
        logger.info(f"Login request for: {login_request.employee_id}")

        try:
            # Authenticate employee
            auth_result = self.auth_service.login(
                employee_id=login_request.employee_id,
                password=login_request.password,
                request=request,
            )

            return LoginResponseDTO(**auth_result)

        except Exception as e:
            logger.error(f"Login failed for {login_request.employee_id}: {str(e)}")
            raise

    def renew_token(
        self, refresh_request: RefreshTokenRequestDTO
    ) -> RefreshTokenResponseDTO:
        """Handle access token refresh"""
        logger.info("Token refresh request")

        try:
            result = self.auth_service.renew_token(refresh_request.refresh_token)

            return RefreshTokenResponseDTO(**result)

        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise

    def get_auth_url(self) -> str:
        return self.auth_service.get_oauth_url()

    def handle_callback(self, code: str, state: str) -> dict:
        return self.auth_service.handle_oauth_callback(code, state)
