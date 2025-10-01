from typing import Optional

from fastapi import Request
from typing import Dict, Optional

from src.present.dto.auth.auth_info import AuthInfo


def extract_user_info(request: Request) -> AuthInfo:
    """Extract user information from request.state set by middleware"""
    employee_id = getattr(request.state, "employee_id", None)
    employee_email = getattr(request.state, "employee_email", None)
    return AuthInfo(
        employee_id=employee_id,
        email=employee_email
    )
