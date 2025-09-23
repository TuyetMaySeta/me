"""
Custom exceptions for EMS application
"""

from typing import Optional


class EMSException(Exception):
    """Base custom exception for EMS application"""

    def __init__(
        self, message: str, http_status: int = 500, error_code: Optional[str] = None
    ):
        self.message = message
        self.http_status = http_status
        self.error_code = error_code or f"EMS_{http_status}"
        super().__init__(self.message)


class ValidationException(EMSException):
    """Exception for validation errors"""

    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, http_status=400, error_code=error_code)


class NotFoundException(EMSException):
    """Exception for resource not found errors"""

    def __init__(self, message: str, error_code: str = "NOT_FOUND"):
        super().__init__(message, http_status=404, error_code=error_code)


class ConflictException(EMSException):
    """Exception for conflict errors (e.g., duplicate data)"""

    def __init__(self, message: str, error_code: str = "CONFLICT"):
        super().__init__(message, http_status=409, error_code=error_code)


class UnauthorizedException(EMSException):
    """Exception for authentication/authorization errors"""

    def __init__(self, message: str, error_code: str = "UNAUTHORIZED"):
        super().__init__(message, http_status=401, error_code=error_code)


class ForbiddenException(EMSException):
    """Exception for forbidden access errors"""

    def __init__(self, message: str, error_code: str = "FORBIDDEN"):
        super().__init__(message, http_status=403, error_code=error_code)


class InternalServerException(EMSException):
    """Exception for internal server errors"""

    def __init__(
        self, message: str = "Internal server error", error_code: str = "INTERNAL_ERROR"
    ):
        super().__init__(message, http_status=500, error_code=error_code)

class DatabaseException(EMSException):
    """Exception for database operation errors"""
    
    def __init__(self, message: str, error_code: str = "DATABASE_ERROR"):
        super().__init__(
            message=message,
            error_code=error_code,
            http_status=500
        )

class AuthenticationException(EMSException):
    """Exception for authentication-related errors"""
    
    def __init__(self, message: str, error_code: str = "AUTH_ERROR"):
        super().__init__(
            message=message,
            error_code=error_code,
            http_status=401
        )

