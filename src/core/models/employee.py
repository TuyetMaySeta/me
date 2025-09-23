from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    Boolean,
    Index,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.bootstrap.database_bootstrap import Base
from src.core.enums import EmployeeStatusEnum, GenderEnum, MaritalStatusEnum


class Employee(Base):
    __tablename__ = "employees"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(
        String(15), unique=True
    )  # Changed to 15 to accommodate country codes
    gender = Column(SQLEnum(GenderEnum, name="gender"))
    date_of_birth = Column(Date)
    marital_status = Column(SQLEnum(MaritalStatusEnum, name="marital_status"))
    join_date = Column(Date)
    current_position = Column(String(255))
    permanent_address = Column(Text)
    current_address = Column(Text)
    status = Column(
        SQLEnum(EmployeeStatusEnum, name="employee_status"),
        default=EmployeeStatusEnum.ACTIVE,
    )
    hashed_password = Column(String(255), nullable=True)
    password_is_changed_at = Column(DateTime,nullable=True)
    is_password_default = Column(Boolean, default=True)  # Track if user are using default password

    # Add index for email (add this after the class definition)
    __table_args__ = (
        Index('idx_employee_email', 'email'),
        Index('idx_employee_email_active', 'email', 'status'),
    )

    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    children = relationship(
        "EmployeeChild", back_populates="employee", cascade="all, delete-orphan"
    )
    contacts = relationship(
        "EmployeeContact", back_populates="employee", cascade="all, delete-orphan"
    )
    documents = relationship(
        "EmployeeDocument", back_populates="employee", cascade="all, delete-orphan"
    )
    educations = relationship(
        "EmployeeEducation", back_populates="employee", cascade="all, delete-orphan"
    )
    certifications = relationship(
        "EmployeeCertification", back_populates="employee", cascade="all, delete-orphan"
    )
    profile = relationship(
        "EmployeeProfile",
        uselist=False,
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    languages = relationship(
        "Language", back_populates="employee", cascade="all, delete-orphan"
    )
    technical_skills = relationship(
        "EmployeeTechnicalSkill",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    projects = relationship(
        "EmployeeProject", back_populates="employee", cascade="all, delete-orphan"
    )
    sessions = relationship("EmployeeSession", back_populates="employee", cascade="all, delete-orphan")
    __table_args__ = (
        Index('idx_employee_email', 'email'),
    )
