import jwt
import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime
from src.config.config import settings
from src.repository.employee_repository import EmployeeRepository
from src.bootstrap import application_bootstrap
from src.bootstrap.application_bootstrap import get_current_user, get_current_user_optional
logger = logging.getLogger(__name__)

class JWTMiddleware(BaseHTTPMiddleware):
    """
    JWT Middleware for FastAPI using BaseHTTPMiddleware
    """
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Skip public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)

        # Extract token
        token = self._extract_token(request)
        if not token:
            return self._auth_error("Missing Authorization header", "MISSING_TOKEN")

        # Verify and validate token
        try:
            payload = self._verify_token(token)
            
            # Validate session token
            session_token = payload.get("session_token")
            if not session_token:
                return self._auth_error("Session token not found in JWT", "MISSING_SESSION_TOKEN")
            
            session_valid = await self._validate_session_token(payload["employee_id"], session_token)
            if not session_valid:
                return self._auth_error("Invalid or expired session", "INVALID_SESSION")
            
            employee = await self._validate_employee(payload["employee_id"])
            if not employee:
                return self._auth_error("Employee not found or inactive", "EMPLOYEE_INACTIVE")

            # Add user to request state
            request.state.current_user = employee
            request.state.authenticated = True

        except jwt.ExpiredSignatureError:
            return self._auth_error("Token has expired - please login again", "TOKEN_EXPIRED")
        except jwt.InvalidSignatureError:
            return self._auth_error("Token signature invalid - possible tampering", "INVALID_SIGNATURE")
        except jwt.InvalidIssuerError:
            return self._auth_error("Token from untrusted issuer", "INVALID_ISSUER")
        except jwt.InvalidAudienceError:
            return self._auth_error("Token not intended for this application", "INVALID_AUDIENCE")
        except jwt.InvalidTokenError as e:
            return self._auth_error(f"Invalid token: {str(e)}", "INVALID_TOKEN")
        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            return self._auth_error("Authentication failed", "AUTH_ERROR")

        return await call_next(request)

    def _extract_token(self, request: Request) -> Optional[str]:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None

    def _verify_token(self, token: str) -> Dict[str, Any]:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iss": True,
                "verify_aud": True,
            },
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience
        )

        # Token type check
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError("Invalid token type")
        return payload
    # validate session token
    
    async def _validate_session_token(self, employee_id: int, session_token: str) -> bool:
        """
        Validate session token against database
        """
        db = application_bootstrap.SessionLocal()
        try:
            # Query session from database
            from src.core.models.employee_session import EmployeeSession
            
            session = db.query(EmployeeSession).filter(
                EmployeeSession.employee_id == employee_id,
                EmployeeSession.session_token == session_token,
                EmployeeSession.is_active == True,
                EmployeeSession.expires_at > datetime.utcnow(),
                EmployeeSession.revoked_at.is_(None)
            ).first()
            
            return session is not None
            
        except Exception as e:
            logger.error(f"Session validation error: {str(e)}")
            return False
        finally:
            db.close()
    
    
    async def _validate_employee(self, employee_id: int) -> Optional[Dict[str, Any]]:
        db = application_bootstrap.SessionLocal()
        try:
            employee_repo = EmployeeRepository(db)
            employee = employee_repo.get_employee_by_id(employee_id)
            if not employee or employee.status.value != "Active":
                return None
            return {
                "id": employee.id,
                "email": employee.email,
                "full_name": employee.full_name,
                "current_position": employee.current_position
            }
        finally:
            db.close()

    def _is_public_endpoint(self, path: str) -> bool:
        public_paths = [
            "/",
            "/status",
            "/auth-info",
            "/ems/api/v1/auth/login",
            "/ems/api/v1/auth/refresh",
            "/openapi.json",
            "/docs",
            "/redoc"
        ]
        return any(path.startswith(p) for p in public_paths)

    def _auth_error(self, message: str, code: str = "AUTH_ERROR") -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "code": code,
                    "message": message,
                    "suggestion": "Include valid JWT token in Authorization header",
                    "format": "Authorization: Bearer <your-jwt-token>",
                    "login_url": f"{settings.api_prefix}/auth/login"
                }
            }
        )
