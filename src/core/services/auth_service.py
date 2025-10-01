import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt
from fastapi import Request

from src.common.exception.exceptions import (
    InternalServerException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
    InternalServerException
)
from src.utils.password_utils import hash_password,is_valid_password
from src.config.config import settings
from src.core.enums.employee import EmployeeStatusEnum, SessionProviderEnum
from src.core.enums.verification import VerificationTypeEnum
from src.core.models.employee_session import EmployeeSession
from src.core.models.verification_code import VerificationCode
from src.core.services.jwt_service import JWTService
from src.core.services.verification_service import mail_service
from src.repository.employee_repository import EmployeeRepository
from src.repository.session_repository import SessionRepository
from src.repository.verification_repository import VerificationRepository
from src.sdk.microsoft.client import MicrosoftClient
from src.utils.extract_header_info import extract_device_info, extract_ip_address
from src.utils.password_utils import hash_password, is_valid_password

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service handling login, token verification, etc."""

    def __init__(
        self,
        employee_repository: EmployeeRepository,
        session_repository: SessionRepository,
        jwt_service: JWTService,
        microsoft_client: MicrosoftClient,
        verification_repository: VerificationRepository,
    ):
        self.employee_repository = employee_repository
        self.session_repository = session_repository
        self.jwt_service = jwt_service
        self.microsoft_client = microsoft_client
        self.verification_repository = verification_repository
        self.otp_expire_minutes = settings.otp_expire_minutes


    def login(
        self, employee_id: str, password: str, request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """
        Authenticate employee and create session
        """
        logger.info(f"Login attempt for employee: {employee_id}")

        employee = self.employee_repository.get_employee_by_id(employee_id)
        if not employee or employee.status != EmployeeStatusEnum.ACTIVE:
            logger.warning(
                f"Inactive or missing employee login attempt: "
                f"{getattr(employee, 'id', None)}"
            )
            raise UnauthorizedException(
                "Account is inactive or not found", "ACCOUNT_INACTIVE"
            )
        if not employee.hashed_password:
            logger.warning(f"No password set for employee: {employee.id}")
            raise UnauthorizedException("Account setup incomplete", "NO_PASSWORD")
        if not is_valid_password(password, employee.hashed_password):
            logger.warning(f"Invalid password for employee: {employee.id}")
            raise UnauthorizedException("Invalid credentials", "INVALID_CREDENTIALS")

        return self._create_login_session(employee, SessionProviderEnum.LOCAL, request)

    def renew_token(
        self, refresh_token: str, request: Optional[Request] = None
    ) -> Dict[str, Any]:
        payload = self.jwt_service.verify_token(refresh_token, "refresh")
        employee_email = payload.get("email")

        session = self.session_repository.get_active_session(refresh_token)
        if session is None:
            raise UnauthorizedException("Invalid or expired session", "INVALID_SESSION")

        access_token_payload = {
            "employee_id": session.employee_id,
            "email": employee_email,
            "session_id": session.id,
        }

        access_token = self.jwt_service.generate_token("access", access_token_payload)
        return {
            "access_token": access_token.get("token"),
            "expires_in": access_token.get("expire_time"),
        }

    def get_oauth_url(self) -> str:
        state = self.jwt_service.generate_token("state", {"some": "data"}).get("token")
        return self.microsoft_client.get_oauth_url(state)

    def handle_oauth_callback(self, code: str, state: str, request: Request) -> dict:
        user_info = self.microsoft_client.verifyToken(code, state)
        user_mail = user_info.get("user_info", {}).get("mail") or user_info.get(
            "user_info", {}
        ).get("userPrincipalName")

        employee = self.employee_repository.get_employee_by_email(user_mail)
        if not employee:
            raise NotFoundException("Employee not found", "EMPLOYEE_NOT_FOUND")

        result = self._create_login_session(
            employee, SessionProviderEnum.MICROSOFT, request
        )
        return result

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = self.jwt_service.verify_token(token, "access")
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token expired", "TOKEN_EXPIRED")
        except jwt.InvalidTokenError as e:
            raise UnauthorizedException(f"Invalid token: {str(e)}", "INVALID_TOKEN")
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise UnauthorizedException("Authentication failed", "AUTH_ERROR")

    def logout(self, request: Request) -> dict:
        access_token = request.headers.get("Authorization")
        if not access_token or not access_token.startswith("Bearer "):
            raise UnauthorizedException("Missing or invalid token", "INVALID_TOKEN")
        payload = self.jwt_service.verify_token(access_token, "access")
        session_id = payload.get("session_id")
        session = self.session_repository.get_active_session_by_id(session_id)
        if not session:
            raise UnauthorizedException("Invalid or expired session", "INVALID_SESSION")
        self.session_repository.revoke_session(session_id)
        return {"message": "Logged out successfully"}

    async def verify_old_password_and_send_otp(
        self, employee_id: int, old_password: str
    ) -> Dict[str, Any]:
        try:
            # Verify old password
            employee = self.employee_repository.get_employee_by_id(employee_id)
            if not employee:
                raise NotFoundException(
                    f"Employee with ID'{employee_id}' is not found",
                    "EMPLOYEE_NOT_FOUND",
                )

            is_valid = is_valid_password(old_password, employee.hashed_password)
            if not is_valid:
                return {
                    "valid": False,
                    "message": "Password is incorrect",
                    "otp_sent": False,
                    "expires_in_seconds": 0,
                }
            # If password valid, send OTP
            # Check if there is an active OTP before
            active_otp = self.verification_repository.get_active_otp(
                employee_id, VerificationTypeEnum.CHANGE_PASSWORD
            )
            if active_otp:
                raise ValidationException(
                    "Please wait before requesting a new OTP", "OTP_RATE_LIMIT"
                )

            # Generate OTP
            otp_code = self._generate_otp()

            # Expire OTP
            expires_at = self._get_otp_expiry_time()

            expires_at = self._get_otp_expiry_time()

            verification = VerificationCode(
                employee_id=employee_id,
                organization_id=1,
                code=otp_code,
                type=VerificationTypeEnum.CHANGE_PASSWORD,
                expires_at=expires_at,
            )
            self.verification_repository.create_verification(verification)
            logger.info(f"OTP created for employee {employee_id}")

            # Send email
            employee = self.employee_repository.get_employee_by_id(employee_id)
            if not employee:
                raise NotFoundException(
                    f"Employee with ID '{employee_id}' not found", "EMPLOYEE_NOT_FOUND"
                )
            
            await mail_service.send_otp_email(
                recipient_email=employee.email,
                otp_code=otp_code,
                full_name=employee.full_name
            )
            return {
                "valid": True,
                "message": "Password is correct.OTP sent to your email",
                "otp_sent": True,
                "expires_in_seconds": 300,
            }

        except Exception as e:
            logger.error(
                f"Error verifying password for employee {employee_id}: {str(e)}"
            )
            raise e

    def verify_otp(
        self, employee_id: int, otp_code: str, verification_type: VerificationTypeEnum
    ) -> bool:
        """Verify OTP code"""
        verification = self.verification_repository.get_valid_otp(
            employee_id, otp_code, verification_type
        )
        if not verification:
            raise ValidationException("Invalid or expired OTP code", "INVALID_OTP")
        # Mark as user
        self.verification_repository.mark_as_used(verification.id)
        logger.info(f"OTP verified successfully for employee {employee_id}")

        return True
    
    async def change_password( self, employee_id: int, otp_code:str, new_password: str, confirm_password: str) -> Dict[str,Any]:
        try:
            #Valisate password match
            if new_password != confirm_password:
                raise ValidationException(
                    "Passwords do not match",
                    "PASSWORD_MISMATCH"
                )
            # VERIFY OTP
            is_otp_valid = self.verify_otp(employee_id, otp_code, VerificationTypeEnum.CHANGE_PASSWORD)

            if not is_otp_valid:
                raise ValidationException(
                    "Invalid or expired OTP",
                    "INVALID_OTP"
                )
            # get employee
            employee = self.employee_repository.get_employee_by_id(employee_id)
            if not employee:
                raise NotFoundException(
                    f"Employee with ID '{employee_id}' not found",
                    "EMPLOYEE_NOT_FOUND "
                )
            # Check new password is same old password
            if is_valid_password(new_password,employee.hashed_password):
                raise ValidationException(
                    "Newpassword cannot be the same as old password",
                    "SAME_PASSWORD"
                )
            #Hash and update
            new_hashed_password = hash_password(new_password)
            self.employee_repository.update_employee_password(employee_id,new_hashed_password)
            
            
            self.session_repository.revoke_all_employee_sessions(employee_id)

            logger.info(f"Password changed successfully for employee {employee_id}")

            return {
                "success": True,
                "message": "Password changed successfully. Please login again",
                "employee_id" : employee_id
            }
        except ValidationException:
            raise
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error changing password for employee {employee_id}: {str(e)}")
            raise InternalServerException(
                "Failed to change password",
                "PASSWORD_CHANGE_ERROR"
            )


    def _generate_otp(self) -> str:
        """Generate 6 digits"""
        return str(secrets.randbelow(1000000)).zfill(6)
    
    def _get_otp_expiry_time(self) -> datetime:
        """Calculate OTP expiration time from current time"""
        return datetime.now(timezone.utc) + timedelta(
            minutes=self.otp_expire_minutes
        )

    def _create_login_session(
        self, employee, provider: SessionProviderEnum, request: Optional[Request] = None
    ) -> Dict[str, Any]:
        token_payload = {"employee_id": employee.id, "email": employee.email}
        refresh_token = self.jwt_service.generate_token("refresh", token_payload)

        new_session = EmployeeSession(
            employee_id=employee.id,
            session_token=refresh_token.get("token"),
            expires_at=refresh_token.get("expire_time"),
            provider=provider,
            device_info=extract_device_info(request) if request else None,
            ip_address=extract_ip_address(request) if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )
        session = self.session_repository.create_session(new_session)

        access_token_payload = {**token_payload, "session_id": session.id}

        access_token = self.jwt_service.generate_token("access", access_token_payload)

        return {
            "access_token": access_token.get("token"),
            "refresh_token": refresh_token.get("token"),
            "expires_at": refresh_token.get("expire_time"),
            "session_id": session.id,
            "employee": {
                "id": employee.id,
                "email": employee.email,
                "full_name": employee.full_name,
            },
        }
