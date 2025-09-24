import logging
from typing import Any, Dict, Optional

import requests
from fastapi import Request

from src.common.exception.exceptions import UnauthorizedException
from src.core.enums import EmployeeStatusEnum, SessionProviderEnum
from src.core.services.jwt_service import JWTService
from src.core.utils.extract_header_info import extract_device_info, extract_ip_address
from src.core.utils.password_utils import verify_password
from src.repository.employee_repository import EmployeeRepository
from src.repository.session_repository import SessionRepository
from src.sdk.microsoft.client import microsoft_client

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service handling login, token verification, etc."""

    def __init__(
        self,
        employee_repository: EmployeeRepository,
        session_repository: SessionRepository,
        jwt_service: JWTService,
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

        # Try to find by ID if it's numeric, otherwise by email
        try:
            # If it's a number, try to find by ID
            if employee_id.isdigit():
                employee = self.employee_repository.get_employee_by_id(int(employee_id))
        except Exception:
            raise UnauthorizedException("Invalid credentials", "INVALID_CREDENTIALS")

        # 2. Check employee status
        if employee.status != EmployeeStatusEnum.ACTIVE:
            logger.warning(f"Inactive employee login attempt: {employee.id}")
            raise UnauthorizedException("Account is inactive", "ACCOUNT_INACTIVE")

        # 3. Verify password
        if not employee.hashed_password:
            logger.warning(f"No password set for employee: {employee.id}")
            raise UnauthorizedException("Account setup incomplete", "NO_PASSWORD")

        if not verify_password(password, employee.hashed_password):
            logger.warning(f"Invalid password for employee: {employee.id}")
            raise UnauthorizedException("Invalid credentials", "INVALID_CREDENTIALS")

        token = self._generate_token_pair(
            {"employee_id": employee.id, "email": employee.email}
        )

        # Extract request info
        device_info = extract_device_info(request) if request else None
        ip_address = extract_ip_address(request) if request else None
        user_agent = request.headers.get("user-agent") if request else None

        session = self.session_repository.create_session(
            employee_id=employee.id,
            session_token=token.get("access_token"),
            expires_at=token.get("access_expires_at"),
            provider=SessionProviderEnum.LOCAL,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info(f"Successful login for employee: {employee.id}")

        # 6. Return response
        return {
            "access_token": token.get("access_token"),
            "refresh_token": token.get("refresh_token"),
            "expires_at": token.get("access_expires_at"),  # in seconds
            "employee": {
                "id": employee.id,
                "email": employee.email,
                "full_name": employee.full_name,
                "current_position": employee.current_position,
            },
            "session_id": str(session.id),
        }

    def renew_token(
        self, refresh_token: str, request: Optional[Request] = None
    ) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        """

        try:
            payload = self.jwt_service.verify_token(refresh_token, "refresh")

            employee_id = payload.get("employee_id")
            if not employee_id:
                raise UnauthorizedException(
                    "Invalid refresh token", "INVALID_REFRESH_TOKEN 1"
                )

            employee = self.employee_repository.get_employee_by_id(employee_id)
            if not employee or employee.status != EmployeeStatusEnum.ACTIVE:
                raise UnauthorizedException(
                    "Invalid refresh token", "INVALID_REFRESH_TOKEN 2"
                )

        except Exception:
            logger.warning("Invalid refresh token")
            raise UnauthorizedException(
                "Invalid refresh token", "INVALID_REFRESH_TOKEN 3"
            )

        logger.info(f"Access token refreshed for employee: {employee.id}")

        access_token = self.jwt_service.generate_token(
            "access", {"employee_id": employee.id, "email": employee.email}
        )

        session = self.session_repository.create_session(
            employee_id=employee.id,
            session_token=access_token.get("token"),
            expires_at=access_token.get("expire_time"),
            provider=SessionProviderEnum.LOCAL,
            device_info=extract_device_info(request) if request else None,
            ip_address=extract_ip_address(request) if request else None,
            user_agent=request.headers.get("user-agent") if request else None,
        )

        logger.info(f"Successful login for employee: {employee.id}")

        return {
            "access_token": access_token.get("token"),
            "expires_in": access_token.get("expire_time"),  # in seconds
            "session_id": str(session.id),
        }

    def get_oauth_url(self) -> str:

        state = self.jwt_service.generate_token("state", {"some": "data"}).get("token")
        return self.microsoft_client.get_oauth_url(state)

    def handle_oauth_callback(self, code: str, state: str) -> dict:
        """Exchange authorization code for access token"""

        try:

            user_info = self.microsoft_client.verifyToken(code, state)
            user_mail = user_info.get("user_info", {}).get("mail") or user_info.get(
                "user_info", {}
            ).get("userPrincipalName")

            # Check if user exists in our database
            employee = self.employee_repository.get_employee_by_email(user_mail)
            if not employee:
                logger.warning(f"User with email {user_mail} not found in database")
                return {"error": "User not found in our system"}

            return {"success": True, "employee": employee}
        except requests.RequestException as e:
            logger.error(
                f"Token exchange failed: {e}, response={getattr(e.response, 'text', None)}"
            )
            return {"error": "Token exchange failed"}

    def _generate_token_pair(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate access and refresh tokens for an employee
        """
        access_token = self.jwt_service.generate_token("access", payload)

        refresh_token = self.jwt_service.generate_token("refresh", payload)

        return {
            "access_token": access_token.get("token"),
            "refresh_token": refresh_token.get("token"),
            "access_expires_at": access_token.get("expire_time"),
            "refresh_expires_at": refresh_token.get("expire_time"),
        }
