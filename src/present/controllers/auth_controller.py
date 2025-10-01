import logging
from typing import Any, Dict, List, Optional, Tuple

from fastapi import HTTPException, Request, Response, status
from typing import Optional, Dict, Any, List, Tuple
from src.common.exception.exceptions import (
    ConflictException,
    NotFoundException,
    ValidationException,
)
from src.core.enums.verification import VerificationTypeEnum
from src.core.services.auth_service import AuthService
from src.present.dto.auth.auth_request_dto import (
    ChangePasswordDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    VerifyOTPRequestDTO,
    VerifyOldPasswordDTO,
    ChangePasswordDTO
)
from src.present.dto.auth.auth_response_dto import (
    LoginResponseDTO,
    RefreshTokenResponseDTO,
    VerifyOTPResponse,
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

            result = self.auth_service.verify_old_password_and_send_otp(
                employee_id, verify_data.old_password
            )

            return result
        except NotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ValidationException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error verifying password: {str(e)}",
            )

    def verify_otp(self, request: VerifyOTPRequestDTO) -> VerifyOTPResponse:
        """Verify OTP code"""

        is_valid = self.auth_service.verify_otp(
            employee_id=request.employee_id,
            otp_code=request.otp_code,
            verification_type=VerificationTypeEnum.CHANGE_PASSWORD,
        )

        return VerifyOTPResponse(
            valid=is_valid,
            message="OTP verified successfully" if is_valid else "Invalid OTP",
        )
    
    async def change_password(
        self, 
        change_data: ChangePasswordDTO
    ) -> Dict[str, Any]:
        """Change password with OTP verification"""
        try:
            result = await self.auth_service.change_password(
                employee_id=change_data.employee_id,
                otp_code=change_data.otp_code,
                new_password=change_data.new_password,
                confirm_password=change_data.confirm_password
            )
            return result
            
        except ValidationException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error in change_password controller: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error changing password: {str(e)}"
            )
