import logging
from datetime import datetime, timezone
from typing import Callable, Optional

import jwt
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.bootstrap.application_bootstrap import app_bootstrap
from src.config.config import settings

logger = logging.getLogger(__name__)


class JWTMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)
        self.auth_service = app_bootstrap.auth_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        logger.debug(f"Processing request path: {request.url.path}")

        # Skip public
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)

        # Extract and validate token
        token = self._extract_token(request)
        if not token:
            return self._auth_error("Missing Authorization header", "MISSING_TOKEN")

        try:

            payload = self.auth_service.verify_access_token(token)

            employee_id = payload.get("employee_id")
            employee_email = payload.get("email")
            # Attach employee info to request.state
            request.state.employee_id = employee_id
            request.state.employee_email = employee_email

            return await call_next(request)

        except jwt.ExpiredSignatureError:
            return self._auth_error("Token expired", "TOKEN_EXPIRED")
        except jwt.InvalidTokenError as e:
            return self._auth_error(f"Invalid token: {str(e)}", "INVALID_TOKEN")
        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            return self._auth_error("Authentication failed", "AUTH_ERROR")

    def _extract_token(self, request: Request) -> Optional[str]:
        headers = dict(request.scope["headers"])
        auth_header = headers.get(b"authorization")
        if auth_header:
            auth_header = auth_header.decode("utf-8")
            logger.debug(f"Raw Authorization header: {auth_header}")
            if auth_header.startswith("Bearer "):
                return auth_header[7:]
        logger.debug("Authorization header missing or not in 'Bearer' format.")
        return None

    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no auth required)"""
        public_paths = [
            "/health",
            "/ems/api/v1/health",
            "/ems/api/v1/auth/login",
            "/ems/api/v1/auth/refresh",
            "/ems/api/v1/auth/login/microsoft",
            "/ems/api/v1/auth/microsoft/callback",
            "/ems/api/v1/auth/public",
            "/ems/api/v1/docs",
            "/ems/api/v1/redoc",
            "/ems/api/v1/openapi.json",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        return any(path.startswith(p) for p in public_paths)

    def _auth_error(self, message: str, code: str = "AUTH_ERROR") -> JSONResponse:
        """Return authentication error response"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "code": code,
                    "message": message,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "login_url": f"{settings.api_prefix}/auth/login",
                }
            },
        )
