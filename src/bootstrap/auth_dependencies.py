
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

from src.bootstrap.dependencies import get_auth_service
from src.core.services.auth_service import AuthService
from src.common.exception.exceptions import ValidationException

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

class AuthenticationResult:
    """Authentication result với employee info"""
    def __init__(self, employee_id: int, email: str, token_info: Dict[str, Any]):
        self.employee_id = employee_id
        self.email = email
        self.token_info = token_info
        self.is_near_expiry = token_info.get("is_near_expiry", False)

def get_token_from_request(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
        """Extract token từ Authorization header hoặc Cookie"""
        if credentials:
            return credentials.credentials
        return request.cookies.get("access_token")

def require_authentication(
        request: Request,
        response: Response,
        token: Optional[str] = Depends(get_token_from_request),
        auth_service: AuthService = Depends(get_auth_service)
    ) -> "AuthenticationResult":

        """Required authentication dependency"""
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "MISSING_TOKEN",
                        "message": "Authentication token required",
                        "suggestion": "Please login to access this resource",
                        "action": "Login",
                        "login_endpoint": "/ems/api/v1/auth/login"
                    }
                }
            )
        
        try:
            result = auth_service.verify_token(token)
            return AuthenticationResult(
                employee_id=result["employee_id"],
                email=result["email"],
                token_info=result
            )
        except ValidationException as e:
            if e.error_code == "TOKEN_EXPIRED":
                # Try refresh with refresh token
                refresh_token = request.cookies.get("refresh_token")
                if refresh_token:
                    try:
                        refresh_result = auth_service.refresh_access_token(refresh_token)
                        response.set_cookie(
                            key="access_token",
                            value=refresh_result["access_token"],
                            max_age=refresh_result["expires_in"],
                            httponly=True,
                            secure=False,
                            samesite="lax"
                        )
                        
                        result = auth_service.verify_token(refresh_result["access_token"])
                        return AuthenticationResult(
                            employee_id=result["employee_id"],
                            email=result["email"],
                            token_info=result
                        )
                    except Exception:
                        pass  # Fall through to error
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": {
                            "code": "TOKEN_EXPIRED",
                            "message": "Access token has expired",
                            "suggestion": "Please login again",
                            "action": "Re-authenticate",
                            "login_endpoint": "/ems/api/v1/auth/login"
                        }
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": {
                            "code": e.error_code,
                            "message": e.message,
                            "suggestion": "Please login again",
                            "action": "Re-authenticate"
                        }
                    }
                )
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "AUTH_ERROR",
                        "message": "Authentication failed",
                        "suggestion": "Please login again",
                        "action": "Re-authenticate"
                    }
                }
            )

def optional_authentication(
        request: Request,
        response: Response,
        token: Optional[str] = Depends(get_token_from_request),
        auth_service: AuthService = Depends(get_auth_service)
    ) -> Optional[AuthenticationResult]:
        """Optional authentication - returns None if no valid token"""
        if not token:
            return None
        
        try:
            return require_authentication(request, response, token, auth_service)
        except HTTPException:
            return None