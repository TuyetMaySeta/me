import jwt
import secrets
import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from src.config.config import settings
from src.common.exception.exceptions import ValidationException

class JWTService:
    """Enhanced JWT Service with better expiry handling"""
    
    @staticmethod
    def generate_access_token(employee_id: int, employee_email: str) -> str:
        """Generate JWT access token with configurable expiry"""
        now = datetime.now(timezone.utc)
        expire_time = now + timedelta(minutes=settings.access_token_expire_minutes)
        
        payload = {
            "employee_id": employee_id,
            "email": employee_email,
            "iat": int(now.timestamp()),
            "exp": int(expire_time.timestamp()),
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # Add unique JWT ID
        }
        
        token = jwt.encode(
            payload, 
            settings.jwt_secret_key, 
            algorithm=settings.jwt_algorithm
        )
        
        return token
    
    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """Verify JWT access token with detailed expiry info"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            
            # Verify token type
            if payload.get("type") != "access":
                raise ValidationException("Invalid token type", "INVALID_TOKEN_TYPE")
            
            # Add expiry info to response
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                payload["expires_at"] = datetime.fromtimestamp(exp_timestamp, timezone.utc)
                payload["time_until_expiry"] = exp_timestamp - int(datetime.now(timezone.utc).timestamp())
                
            return payload
            
        except jwt.ExpiredSignatureError:
            # Get expired token info without verification
            try:
                expired_payload = jwt.decode(
                    token,
                    options={"verify_signature": False, "verify_exp": False}
                )
                exp_time = datetime.fromtimestamp(expired_payload.get("exp", 0), timezone.utc)
                
                raise ValidationException(
                    f"Token expired at {exp_time.isoformat()}", 
                    "TOKEN_EXPIRED"
                )
            except:
                raise ValidationException("Token has expired", "TOKEN_EXPIRED")
                
        except jwt.InvalidTokenError as e:
            raise ValidationException(f"Invalid token: {str(e)}", "INVALID_TOKEN")
        except Exception as e:
            raise ValidationException(f"Token verification failed: {str(e)}", "TOKEN_ERROR")
    
    @staticmethod
    def is_token_near_expiry(token: str, threshold_minutes: int = 30) -> bool:
        """Check if token will expire within threshold"""
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            
            exp_timestamp = payload.get("exp")
            if not exp_timestamp:
                return True
            
            exp_time = datetime.fromtimestamp(exp_timestamp, timezone.utc)
            now = datetime.now(timezone.utc)
            threshold_time = now + timedelta(minutes=threshold_minutes)
            
            return exp_time <= threshold_time
            
        except Exception:
            return True  # If can't parse, assume expired
    
    @staticmethod
    def get_token_info(token: str) -> Dict[str, Any]:
        """Get token information without verification"""
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            
            exp_timestamp = payload.get("exp", 0)
            iat_timestamp = payload.get("iat", 0)
            now_timestamp = int(datetime.now(timezone.utc).timestamp())
            
            return {
                "employee_id": payload.get("employee_id"),
                "email": payload.get("email"),
                "issued_at": datetime.fromtimestamp(iat_timestamp, timezone.utc) if iat_timestamp else None,
                "expires_at": datetime.fromtimestamp(exp_timestamp, timezone.utc) if exp_timestamp else None,
                "is_expired": now_timestamp > exp_timestamp if exp_timestamp else True,
                "seconds_until_expiry": exp_timestamp - now_timestamp if exp_timestamp else 0,
                "token_type": payload.get("type"),
                "jti": payload.get("jti")
            }
        except Exception:
            return {"error": "Could not parse token"}
    @staticmethod
    def generate_refresh_token() -> str:
        """
        Generate secure random refresh token (not JWT)
        """
        # Generate 32 bytes of random data
        random_bytes = secrets.token_bytes(32)
        # Encode as base64url for URL safety
        token = base64.urlsafe_b64encode(random_bytes).decode('utf-8')
        # Remove padding
        token = token.rstrip('=')
        return token