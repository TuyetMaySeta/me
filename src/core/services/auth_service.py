import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import Request
from src.repository.session_repository import SessionRepository
from src.repository.employee_repository import EmployeeRepository
from src.core.utils.password_utils import verify_password
from src.core.services.jwt_service import JWTService
from src.core.enums import SessionProviderEnum, EmployeeStatusEnum
from src.common.exception.exceptions import (
    ValidationException, 
    UnauthorizedException, 
    NotFoundException
)
from src.config.config import settings

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service handling login, token verification, etc."""
    
    def __init__(self, 
                 employee_repository: EmployeeRepository,
                 session_repository: SessionRepository):
        self.employee_repository = employee_repository
        self.session_repository = session_repository
        self.jwt_service = JWTService()

    def login(self, 
              employee_id: str, 
              password: str, 
              remember_me: bool = False,
              request: Optional[Request] = None) -> Dict[str, Any]:
        """
        Authenticate employee and create session
        """
        logger.info(f"Login attempt for employee: {employee_id}")
        
        # 1. Find employee by ID or email
        employee = None
        if "@" in employee_id:
            employee = self.employee_repository.get_employee_by_email(employee_id)
        else:
            # Try to find by ID if it's numeric, otherwise by email
            try:
                # If it's a number, try to find by ID
                if employee_id.isdigit():
                    employee = self.employee_repository.get_employee_by_id(int(employee_id))
                else:
                    # Otherwise search by email
                    employee = self.employee_repository.get_employee_by_email(employee_id)
            except Exception:
                employee = self.employee_repository.get_employee_by_email(employee_id)
        
        if not employee:
            logger.warning(f"Employee not found: {employee_id}")
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
        
        # 4. Generate tokens
        access_token = self.jwt_service.generate_access_token(
            employee.id, 
            employee.email
        )
        refresh_token = self.jwt_service.generate_refresh_token()
        
        # 5. Create session
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days if remember_me else 1
        )
        
        # Extract request info
        device_info = self._extract_device_info(request) if request else None
        ip_address = self._extract_ip_address(request) if request else None
        user_agent = request.headers.get("user-agent") if request else None
        
        session = self.session_repository.create_session(
            employee_id=employee.id,
            session_token=refresh_token,
            expires_at=expires_at,
            provider=SessionProviderEnum.LOCAL,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(f"Successful login for employee: {employee.id}")
        
        # 6. Return response
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "employee": {
                "id": employee.id,
                "email": employee.email,
                "full_name": employee.full_name,
                "current_position": employee.current_position,
                "is_password_default": employee.is_password_default
            },
            "session_id": str(session.id)
        }

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify access token and check session status
        """
        try:
            # 1. Verify JWT token
            payload = self.jwt_service.verify_access_token(token)
            employee_id = payload.get("employee_id")
            
            if not employee_id:
                raise ValidationException("Invalid token payload", "INVALID_TOKEN")
            
            # 2. Get employee
            employee = self.employee_repository.get_employee_by_id(employee_id)
            if not employee:
                raise UnauthorizedException("Employee not found", "EMPLOYEE_NOT_FOUND")
            
            # 3. Check employee status
            if employee.status != EmployeeStatusEnum.ACTIVE:
                raise UnauthorizedException("Account is inactive", "ACCOUNT_INACTIVE")
            
            return {
                "valid": True,
                "employee_id": employee.id,
                "email": employee.email,
                "expires_at": datetime.fromtimestamp(payload["exp"], timezone.utc)
            }
            
        except (ValidationException, UnauthorizedException):
            raise
        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            raise UnauthorizedException("Token verification failed", "TOKEN_ERROR")

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        """
        logger.info("Access token refresh attempt")
        
        # 1. Find and validate session
        session = self.session_repository.get_active_session(refresh_token)
        if not session:
            logger.warning("Invalid or expired refresh token")
            raise UnauthorizedException("Invalid refresh token", "INVALID_REFRESH_TOKEN")
        
        # 2. Get employee
        employee = self.employee_repository.get_employee_by_id(session.employee_id)
        if not employee:
            logger.warning(f"Employee not found for session: {session.employee_id}")
            raise UnauthorizedException("Employee not found", "EMPLOYEE_NOT_FOUND")
        
        # 3. Check employee status
        if employee.status != EmployeeStatusEnum.ACTIVE:
            # Revoke session for inactive employee
            self.session_repository.revoke_session(refresh_token)
            raise UnauthorizedException("Account is inactive", "ACCOUNT_INACTIVE")
        
        # 4. Generate new access token
        access_token = self.jwt_service.generate_access_token(
            employee.id,
            employee.email
        )
        
        logger.info(f"Access token refreshed for employee: {employee.id}")
        
        return {
            "access_token": access_token,
            "expires_in": settings.access_token_expire_minutes * 60,
            "token_type": "Bearer"
        }

    def revoke_session(self, refresh_token: str) -> bool:
        """Revoke a specific session"""
        return self.session_repository.revoke_session(refresh_token)

    def revoke_all_sessions(self, employee_id: int) -> int:
        """Revoke all sessions for an employee"""
        return self.session_repository.revoke_all_employee_sessions(employee_id)

    def _extract_device_info(self, request: Request) -> Optional[str]:
        """Extract device information from request"""
        try:
            user_agent = request.headers.get("user-agent", "")
            # Simple device detection
            if "Mobile" in user_agent:
                return "Mobile"
            elif "Tablet" in user_agent:
                return "Tablet"
            else:
                return "Desktop"
        except Exception:
            return None

    def _extract_ip_address(self, request: Request) -> Optional[str]:
        """Extract IP address from request"""
        try:
            # Check for forwarded IP first
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            
            # Check for real IP
            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                return real_ip
            
            # Fall back to client IP
            return request.client.host if request.client else None
        except Exception:
            return None