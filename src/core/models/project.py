from sqlalchemy import BigInteger, Column, DateTime, String
from sqlalchemy.sql import func

from src.core.models.base import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    organization_id = Column(BigInteger)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeProjectRole(Base):
    __tablename__ = "employee_project_roles"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, nullable=False)
    project_id = Column(BigInteger, nullable=False)
    role_id = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
