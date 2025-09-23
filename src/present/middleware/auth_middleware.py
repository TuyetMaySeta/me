from fastapi import Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from typing import Optional, Callable
from functools import wraps
import re
from src.core.services.jwt_service import JWTService
from src.repository.session_repository import SessionRepository
from src.repository.employee_repository import EmployeeRepository
from src.common.exception.exceptions import ValidationException, AuthenticationException


# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Authentication middleware for JWT token validation"""
    
    def __init__(
        self,
        session_repository: SessionRepository,
        employee_repository: EmployeeRepository
    ):
        """
        Initialize authentication middleware
        """
        self.session_repository = session_repository
        self.employee_repository = employee_repository
        self.jwt_service = JWTService()
    
    async def authenticate_request(self, request: Request) -> Optional[dict]:
        """
        Extract and validate JWT token from request
        """
        try:
            # Extract JWT token from Authorization header or cookie
            access_token = self._extract_access_token(request)
            
            if not access_token:
                return None
            
            # Verify JWT using jwt_service
            token_payload = self.jwt_service.verify_access_token(access_token)
            
            if not token_payload:
                return None
            
            # Extract employee info from token
            employee_id = token_payload.get('employee_id')
            employee_email = token_payload.get('email')
            
            if not employee_id or not employee_email:
                return None
            
            # Verify employee still exists and is active
            if not self.employee_repository.verify_employee_exists_and_active(employee_id):
                return None
            
            # Get employee data for context
            employee = self.employee_repository.get_employee_by_id(employee_id)
            if not employee:
                return None
            
            # Add employee information to request context
            employee_info = {
                'id': employee.id,
                'email': employee.email,
                'full_name': employee.full_name,
                'current_position': employee.current_position,
                'status': employee.status
            }
            
            return employee_info
            
        except ValidationException:
            # Token validation failed
            return None
        except AuthenticationException:
            # Authentication failed
            return None
        except Exception:
            # Unexpected error - fail securely
            return None
    
    def _extract_access_token(self, request: Request) -> Optional[str]:
        """
        Extract access token from Authorization header or cookie
        """
        # Try Authorization header first
        authorization = request.headers.get('Authorization')
        if authorization:
            # Check Bearer token format
            bearer_match = re.match(r'^Bearer\s+(.+)$', authorization, re.IGNORECASE)
            if bearer_match:
                return bearer_match.group(1).strip()
        
        # Fallback to access_token cookie
        access_token = request.cookies.get('access_token')
        if access_token:
            return access_token.strip()
        
        return None
    
    async def verify_session_active(self, request: Request) -> bool:
        """
        Verify associated session is still active
        Optional additional security check
        
        """
        try:
            # Get refresh token from cookie
            refresh_token = request.cookies.get('refresh_token')
            if not refresh_token:
                return True  # No session to verify, rely on JWT validation only
            
            # Check if session is still active
            session = self.session_repository.get_active_session(refresh_token)
            return session is not None
            
        except Exception:
            # If session check fails, rely on JWT validation
            return True


# Dependency function for FastAPI
async def get_current_user(request: Request) -> Optional[dict]:
    """
    FastAPI dependency to get current authenticated user
    
    """
    # Get auth middleware instance from app state or dependency injection
    # TODO: Replace with proper DI from bootstrap
    auth_middleware = getattr(request.app.state, 'auth_middleware', None)
    
    if not auth_middleware:
        return None
    
    return await auth_middleware.authenticate_request(request)


# Decorator for protected endpoints
def require_auth(func: Callable = None):
    """
    Decorator to require authentication for endpoints
    
    """
    def decorator(endpoint_func: Callable):
        @wraps(endpoint_func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Look in kwargs
                request = kwargs.get('request')
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"error": "Request object not found", "code": "INTERNAL_ERROR"}
                )
            
            # Get current user
            current_user = await get_current_user(request)
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"error": "Authentication required", "code": "NOT_AUTHENTICATED"}
                )
            
            # Add user to request state
            request.state.current_user = current_user
            
            # Call original endpoint
            return await endpoint_func(*args, **kwargs)
        
        return wrapper
    
    # Handle both @require_auth and @require_auth() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


# FastAPI dependency for protected routes
async def require_authentication(request: Request) -> dict:
    """
    FastAPI dependency for protected routes
    
    """
    current_user = await get_current_user(request)
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Authentication required", "code": "NOT_AUTHENTICATED"}
        )
    
    # Add user to request state for controllers
    request.state.current_user = current_user
    
    return current_user


# Optional: Middleware for automatic request processing
async def auth_middleware_handler(request: Request, call_next):
    """
    ASGI middleware to automatically process authentication for all requests
    
    """
    # Automatically authenticate request and add user to context
    auth_middleware = getattr(request.app.state, 'auth_middleware', None)
    
    if auth_middleware:
        current_user = await auth_middleware.authenticate_request(request)
        if current_user:
            request.state.current_user = current_user
            request.state.authenticated = True
        else:
            request.state.current_user = None
            request.state.authenticated = False
    
    # Continue to next handler
    response = await call_next(request)
    return response


# Utility function to check if request is authenticated
def is_authenticated(request: Request) -> bool:
    """
    Check if current request is authenticated
    
    Args:
        request: FastAPI request object
        
    Returns:
        True if authenticated, False otherwise
    """
    return getattr(request.state, 'authenticated', False)


# Utility function to get current user from request
def get_request_user(request: Request) -> Optional[dict]:
    """
    Get current user from request state
    
    Args:
        request: FastAPI request object
        
    Returns:
        User information or None
    """
    return getattr(request.state, 'current_user', None)
