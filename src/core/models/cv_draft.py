# src/core/models/employee_draft.py
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum
from sqlalchemy.sql import func
from src.core.models.employee import Base, ProficiencyEnum, SkillCategoryEnum, SoftSkillEnum
import enum

class DraftStatusEnum(enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED" 
    REJECTED = "REJECTED"

class EmployeeDraft(Base):
    __tablename__ = "employee_draft"

    id = Column(String(6), primary_key=True, unique=True)  # Technical ID
    employee_id = Column(String(50), unique=True, nullable=False)  # Business ID (formerly id_seta)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)  # Bắt buộc
    gender = Column(String(50))
    current_position = Column(String(255))
    summary = Column(Text)
    status = Column(Enum(DraftStatusEnum), default=DraftStatusEnum.DRAFT)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class EmployeeLanguageDraft(Base):
    __tablename__ = "employee_language_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String(6), nullable=False)  # References employee_draft.id
    language_name = Column(String(100))
    proficiency = Column(Enum(ProficiencyEnum))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class EmployeeTechnicalSkillDraft(Base):
    __tablename__ = "employee_technical_skill_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String(6), nullable=False)  # References employee_draft.id
    category = Column(Enum(SkillCategoryEnum))
    skill_name = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class EmployeeSoftSkillDraft(Base):
    __tablename__ = "employee_soft_skill_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String(6), nullable=False)  # References employee_draft.id
    skill_name = Column(Enum(SoftSkillEnum))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class EmployeeProjectDraft(Base):
    __tablename__ = "employee_project_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String(6), nullable=False)  # References employee_draft.id
    project_name = Column(String(255))
    project_description = Column(Text)
    position = Column(String(255))
    responsibilities = Column(Text)
    programming_languages = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
