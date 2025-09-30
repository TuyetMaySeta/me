import logging

from fastapi import Request, Response
from src.common.exception.exceptions import (
    ConflictException,
    NotFoundException,
)
from fastapi import HTTPException,status

from src.core.services.auth_service import AuthService
from src.present.dto.auth.auth_request_dto import (
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    VerifyOldPasswordDTO
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
        result = self.auth_service.renew_token(refresh_request.refresh_token)
        return RefreshTokenResponseDTO(**result)

    def get_auth_url(self) -> str:
        return self.auth_service.get_oauth_url()

    def handle_callback(self, code: str, state: str, request: Request) -> dict:
        return self.auth_service.handle_oauth_callback(code, state, request)

    def logout(self, request: Request) -> dict:
        return self.auth_service.logout(request)
    def verify_old_password(self, employee_id: int, verify_data: VerifyOldPasswordDTO):
        try:
            is_valid = self.auth_service.verify_old_password(
                employee_id,
                verify_data.old_password
            )

            return {
                "valid": is_valid,
                "message":"Password is correct" if is_valid else "Password is incorrect"
            }
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error verifying password: {str(e)}"
            )
        
