from sqlalchemy import (
    Column, String, Integer, BigInteger, Date, Text, DateTime,
    Enum as SQLEnum
)
from sqlalchemy.sql import func
from src.bootstrap.database_bootstrap import Base
from src.core.enums import (
    GenderEnum, MaritalStatusEnum, EmployeeStatusEnum
)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(15), unique=True)  # Changed to 15 to accommodate country codes
    gender = Column(SQLEnum(GenderEnum, name="gender"))
    date_of_birth = Column(Date)
    marital_status = Column(SQLEnum(MaritalStatusEnum, name="marital_status"))
    join_date = Column(Date)
    current_position = Column(String(255))
    permanent_address = Column(Text)
    current_address = Column(Text)
    status = Column(SQLEnum(EmployeeStatusEnum, name="employee_status"), default=EmployeeStatusEnum.ACTIVE)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
