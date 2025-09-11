from sqlalchemy import Column, String, Text, DateTime, Integer, Enum
from sqlalchemy.sql import func
from src.core.models.cv import Base, ProficiencyEnum, SkillCategoryEnum, SoftSkillEnum
import enum

class DraftStatusEnum(enum.Enum):
    DRAFT = "Draft"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class CVDraft(Base):
    __tablename__ = "cv_draft"

    id = Column(String(6), primary_key=True, unique=True)
    id_seta = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    gender = Column(String(50))
    current_position = Column(String(255))
    summary = Column(Text)
    status = Column(Enum(DraftStatusEnum))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class LanguageDraft(Base):
    __tablename__ = "language_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String(6), nullable=False)
    language_name = Column(String(100))
    proficiency = Column(Enum(ProficiencyEnum))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class TechnicalSkillDraft(Base):
    __tablename__ = "technical_skill_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String(6), nullable=False)
    category = Column(Enum(SkillCategoryEnum))
    skill_name = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class SoftSkillDraft(Base):
    __tablename__ = "soft_skill_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String(6), nullable=False)
    skill_name = Column(Enum(SoftSkillEnum))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class ProjectDraft(Base):
    __tablename__ = "project_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(String(6), nullable=False)
    project_name = Column(String(255))
    project_description = Column(Text)
    position = Column(String(255))
    responsibilities = Column(Text)
    programming_languages = Column(Text)
    created_at = Column(DateTime, server_default=func.now())