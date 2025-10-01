import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt

from src.config.config import settings


class JWTService:

    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_expire_minutes = settings.access_expire_minutes
        self.refresh_expire_minutes = settings.refresh_expire_minutes

    def generate_token(self, token_type: str, claims: Dict[str, Any]) -> str:
        """Generate token theo token_type (access/refresh/...)"""
        now = datetime.now(timezone.utc)
        if token_type == "refresh":
            expire_time = now + timedelta(minutes=self.refresh_expire_minutes)
        else:  # default is access token
            expire_time = now + timedelta(minutes=self.access_expire_minutes)

        payload = {
            "iat": int(now.timestamp()),
            "exp": int(expire_time.timestamp()),
            "type": token_type,
            "jti": secrets.token_urlsafe(16),
            **claims,  # merge user claims (vd: employee_id, email)
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return {"token": token, "expire_time": expire_time}

    def verify_token(self, token: str, token_type: str) -> Dict[str, Any]:
        """Verify token theo loại cụ thể và kiểm tra hết hạn"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        if payload.get("type") != token_type:
            raise ValueError("Invalid token type")
        return payload
