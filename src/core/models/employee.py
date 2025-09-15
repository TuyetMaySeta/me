# src/core/models/employee.py
from sqlalchemy import (
    Column, String, Integer, BigInteger, Date, Text, DateTime,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.sql import func
from src.bootstrap.database_bootstrap import Base
from src.core.enums import (
    GenderEnum, ProficiencyEnum, SkillCategoryEnum, 
    SoftSkillEnum, MaritalStatusEnum, EmployeeStatusEnum
)


class Employee(Base):
    __tablename__ = "employees"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    full_name = Column(String(255))
    email = Column(String(255), unique=True)
    phone = Column(String(20), unique=True)
    gender = Column(SQLEnum(GenderEnum, name="gender"))
    date_of_birth = Column(Date)
    marital_status = Column(SQLEnum(MaritalStatusEnum, name="marital_status"))
    join_date = Column(Date)
    current_position = Column(String(255))
    permanent_address = Column(Text)
    current_address = Column(Text)
    status = Column(SQLEnum(EmployeeStatusEnum, name="employee_status"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeContact(Base):
    __tablename__ = "employee_contacts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    name = Column(String(255))
    relation = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeDocument(Base):
    __tablename__ = "employee_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    identity_number = Column(String(50), unique=True)
    identity_date = Column(Date)
    identity_place = Column(String(255))
    old_identity_number = Column(String(50))
    old_identity_date = Column(Date)
    old_identity_place = Column(String(255))
    tax_id_number = Column(String(50), unique=True)
    social_insurance_number = Column(String(50), unique=True)
    bank_name = Column(String(100))
    branch_name = Column(String(255))
    account_bank_number = Column(String(50), unique=True)
    motorbike_plate = Column(String(50), unique=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeEducation(Base):
    __tablename__ = "employee_education"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    school_name = Column(String(255))
    graduation_year = Column(Integer)
    degree = Column(String(255))
    major = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeCertification(Base):
    __tablename__ = "employee_certifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    certificate_name = Column(String(255))
    issued_by = Column(String(255))
    issued_date = Column(Date)
    expiry_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeProfile(Base):
    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    facebook_link = Column(String(255))
    linkedin_link = Column(String(255))
    how_heard_about_company = Column(Text)
    hobbies = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    language_name = Column(String(100))
    proficiency = Column(SQLEnum(ProficiencyEnum, name="proficiency"))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeTechnicalSkill(Base):
    __tablename__ = "employee_technical_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    category = Column(SQLEnum(SkillCategoryEnum, name="skill_category"))
    skill_name = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeProject(Base):
    __tablename__ = "employee_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    project_name = Column(String(255))
    project_description = Column(Text)
    position = Column(String(255))
    responsibilities = Column(Text)
    programming_languages = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeChild(Base):
    __tablename__ = "employee_children"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(BigInteger, ForeignKey("employees.id"))
    full_name = Column(String(255))
    date_of_birth = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
