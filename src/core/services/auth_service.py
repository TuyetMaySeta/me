import logging
from typing import Any, Dict, Optional

import jwt
import requests
from fastapi import Request

from src.common.exception.exceptions import NotFoundException, UnauthorizedException
from src.core.enums.employee import EmployeeStatusEnum, SessionProviderEnum
from src.core.models.employee_session import EmployeeSession
from src.core.services.jwt_service import JWTService
from src.repository.employee_repository import EmployeeRepository
from src.repository.session_repository import SessionRepository
from src.sdk.microsoft.client import MicrosoftClient
from src.utils.extract_header_info import extract_device_info, extract_ip_address
from src.utils.password_utils import is_valid_password

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service handling login, token verification, etc."""

    def __init__(
        self,
        employee_repository: EmployeeRepository,
        session_repository: SessionRepository,
        jwt_service: JWTService,
        microsoft_client: MicrosoftClient,
    ):
        self.employee_repository = employee_repository
        self.session_repository = session_repository
        self.jwt_service = jwt_service
        self.microsoft_client = microsoft_client

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
            "access_expires_at": access_token.get("expire_time"),
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
    
    def verify_old_password(self, employee_id: int, old_password: str) -> bool:
        try:
            employee = self.employee_repository.get_employee_by_id(employee_id)
            if not employee:
                raise NotFoundException(
                    f"Employee with ID'{employee_id}' is not found",
                    "EMPLOYEE_NOT_FOUND"
                )
            # Verify
            from src.utils.password_utils import is_valid_password
            is_valid = is_valid_password(old_password, employee.hashed_password)
            
            return is_valid
        except Exception as e:
            logger.error(f"Error verifying password for employee {employee_id}: {str(e)}")
        raise

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
    

    
