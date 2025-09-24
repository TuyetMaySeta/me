from typing import Optional

from pydantic import BaseModel


class CallbackDTO(BaseModel):
    code: str
    state: Optional[str] = None
