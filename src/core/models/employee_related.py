# src/core/models/employee_related.py
from sqlalchemy import (
    Column, String, Integer, BigInteger, Date, Text, DateTime,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.sql import func
from src.bootstrap.database_bootstrap import Base
from src.core.enums import (
    ProficiencyEnum, SkillCategoryEnum
)


class EmployeeContact(Base):
    __tablename__ = "employee_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    relation = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)  # Changed to 15
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeDocument(Base):
    __tablename__ = "employee_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"))
    identity_number = Column(String(20), unique=True)  # CCCD Vietnam is 12 digits
    identity_date = Column(Date)
    identity_place = Column(String(255))
    old_identity_number = Column(String(15))  # Old CMND is 9 digits
    old_identity_date = Column(Date)
    old_identity_place = Column(String(255))
    tax_id_number = Column(String(15), unique=True)  # MST Vietnam is 10-13 digits
    social_insurance_number = Column(String(15), unique=True)  # BHXH Vietnam
    bank_name = Column(String(100))
    branch_name = Column(String(255))
    account_bank_number = Column(String(30), unique=True)  # Bank account numbers
    motorbike_plate = Column(String(15), unique=True)  # License plate format
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeEducation(Base):
    __tablename__ = "employee_education"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"))
    school_name = Column(String(255), nullable=False)
    graduation_year = Column(Integer)
    degree = Column(String(255))
    major = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeCertification(Base):
    __tablename__ = "employee_certifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"))
    certificate_name = Column(String(255), nullable=False)
    issued_by = Column(String(255), nullable=False)
    issued_date = Column(Date)
    expiry_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"))
    facebook_link = Column(String(500))  # URLs can be long
    linkedin_link = Column(String(500))
    how_heard_about_company = Column(Text)
    hobbies = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"))
    language_name = Column(String(100), nullable=False)
    proficiency = Column(SQLEnum(ProficiencyEnum, name="proficiency"), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeTechnicalSkill(Base):
    __tablename__ = "employee_technical_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"))
    category = Column(SQLEnum(SkillCategoryEnum, name="skill_category"), nullable=False)
    skill_name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeProject(Base):
    __tablename__ = "employee_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"))
    project_name = Column(String(255), nullable=False)
    project_description = Column(Text)
    position = Column(String(255))
    responsibilities = Column(Text)
    programming_languages = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeChild(Base):
    __tablename__ = "employee_children"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id", ondelete="CASCADE"))
    full_name = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

