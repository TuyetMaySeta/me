from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class AuthInfo(BaseModel):
    """Login response with tokens and user info"""

    employee_id: int
    email: str
