# src/core/models/employee.py
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum
from sqlalchemy.sql import func
from src.bootstrap.database_bootstrap import database_bootstrap

# Import từ centralized enums
from src.core.enums import ProficiencyEnum, SkillCategoryEnum, SoftSkillEnum

# Use the same Base as in env.py
Base = database_bootstrap.get_base()


class Employee(Base):
    __tablename__ = "employee"
    
    id = Column(String(6), primary_key=True)  # Technical ID (6 chars)
    employee_id = Column(String(50), unique=True, nullable=False)  # Business ID (formerly id_seta)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)  # Bắt buộc
    gender = Column(String(50))
    current_position = Column(String(255))
    summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EmployeeLanguage(Base):
    __tablename__ = "employee_languages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(6), nullable=False)  # References employee.id
    language_name = Column(String(100))
    proficiency = Column(Enum(ProficiencyEnum))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class EmployeeTechnicalSkill(Base):
    __tablename__ = "employee_technical_skills"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(6), nullable=False)  # References employee.id
    category = Column(Enum(SkillCategoryEnum))
    skill_name = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class EmployeeSoftSkill(Base):
    __tablename__ = "employee_soft_skills"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(6), nullable=False)  # References employee.id
    skill_name = Column(Enum(SoftSkillEnum))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class EmployeeProject(Base):
    __tablename__ = "employee_projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(6), nullable=False)  # References employee.id
    project_name = Column(String(255))
    project_description = Column(Text)
    position = Column(String(255))
    responsibilities = Column(Text)
    programming_languages = Column(Text)
    created_at = Column(DateTime, server_default=func.now())