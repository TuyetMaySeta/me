from sqlalchemy import Column, String, Text, DateTime, Integer, Enum
from sqlalchemy.sql import func
from src.bootstrap.database_bootstrap import database_bootstrap
import enum

# Use the same Base as in env.py
Base = database_bootstrap.get_base()

class ProficiencyEnum(enum.Enum):
    NATIVE = "Native"
    FLUENT = "Fluent"
    INTERMEDIATE = "Intermediate"
    BASIC = "Basic"

class SkillCategoryEnum(enum.Enum):
    PROGRAMMING_LANGUAGE = "Programming Language"
    DATABASE = "Database"
    FRAMEWORK = "Framework"
    TOOL = "Tool"
    HARDWARE = "Hardware"

class SoftSkillEnum(enum.Enum):
    COMMUNICATION = "Communication"
    TEAMWORK = "Teamwork"
    PROBLEM_SOLVING = "Problem Solving"
    DECISION_MAKING = "Decision Making"
    LEADERSHIP = "Leadership"
    TIME_MANAGEMENT = "Time Management"
    ADAPTABILITY = "Adaptability"
    OTHER = "Other"

class CV(Base):
    __tablename__ = "cv"
    
    id = Column(String(6), primary_key=True)
    id_seta = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    gender = Column(String(50))
    current_position = Column(String(255))
    summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Language(Base):
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_id = Column(String(6), nullable=False)
    language_name = Column(String(100))
    proficiency = Column(Enum(ProficiencyEnum))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class TechnicalSkill(Base):
    __tablename__ = "technical_skills"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_id = Column(String(6), nullable=False)
    category = Column(Enum(SkillCategoryEnum))
    skill_name = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class SoftSkill(Base):
    __tablename__ = "soft_skills"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_id = Column(String(6), nullable=False)
    skill_name = Column(Enum(SoftSkillEnum))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_id = Column(String(6), nullable=False)
    project_name = Column(String(255))
    project_description = Column(Text)
    position = Column(String(255))
    responsibilities = Column(Text)
    programming_languages = Column(Text)
    created_at = Column(DateTime, server_default=func.now())