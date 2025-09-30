from sqlalchemy import BigInteger, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.sql import func

from src.core.enums.verification import VerificationTypeEnum
from src.core.models.base import Base


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, nullable=False)
    organization_id = Column(BigInteger, nullable=True)
    code = Column(String(255), nullable=False)
    type = Column(SQLEnum(VerificationTypeEnum, name="type"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
