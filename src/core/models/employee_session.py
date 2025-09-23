from sqlalchemy import (
    Column, String, BigInteger, Text, DateTime, Boolean, 
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.bootstrap.database_bootstrap import Base
from src.core.enums import SessionProviderEnum


class EmployeeSession(Base):
    __tablename__ = "employee_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    provider = Column(SQLEnum(SessionProviderEnum, name="session_provider"), default=SessionProviderEnum.LOCAL)
    device_info = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    # Relationship back to Employee
    employee = relationship("Employee", back_populates="sessions")

    # Indexes for performance
    __table_args__ = (
        Index('idx_session_token', 'session_token'),
        Index('idx_employee_active_sessions', 'employee_id', 'is_active', 'expires_at'),
        Index('idx_session_cleanup', 'expires_at', 'is_active'),
    )
