# src/core/models/cv_models.py
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey, CHAR
from sqlalchemy.orm import relationship
from src.bootstrap.database_bootstrap import database_bootstrap

Base = database_bootstrap.get_base()

# ---------- ENUMs ----------

class ProficiencyEnum(str, Enum):
    Native = "Native"
    Fluent = "Fluent"
    Intermediate = "Intermediate"
    Basic = "Basic"

class SkillCategoryEnum(str, Enum):
    Programming_Language = "Programming Language"
    Database = "Database"
    Framework = "Framework"
    Tool = "Tool"
    Hardware = "Hardware"

class SoftSkillEnum(str, Enum):
    Communication = "Communication"
    Teamwork = "Teamwork"
    Problem_Solving = "Problem Solving"
    Decision_Making = "Decision Making"
    Leadership = "Leadership"
    Time_Management = "Time Management"
    Adaptability = "Adaptability"
    Other = "Other"

class DraftStatusEnum(str, Enum):
    Draft = "Draft"
    Approved = "Approved"
    Rejected = "Rejected"

# ---------- TABLES ----------
class CV(Base):
    __tablename__ = "cv"
    id = Column(CHAR(6), primary_key=True)
    full_name = Column(String(255))
    gender = Column(String(50))
    current_position = Column(String(255))
    summary = Column(Text)
    updated_at = Column(DateTime)

    drafts = relationship("CVDraft", back_populates="cv")
    languages = relationship("Language", back_populates="cv")
    technical_skills = relationship("TechnicalSkill", back_populates="cv")
    soft_skills = relationship("SoftSkill", back_populates="cv")
    projects = relationship("Project", back_populates="cv")

class CVDraft(Base):
    __tablename__ = "cv_draft"
    id = Column(CHAR(6), ForeignKey("cv.id"), primary_key=True, unique=True)
    full_name = Column(String(255))
    gender = Column(String(50))
    current_position = Column(String(255))
    summary = Column(Text)
    status = Column(SQLEnum(DraftStatusEnum, name="DraftStatus", native_enum=True))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    cv = relationship("CV", back_populates="drafts")
    language_drafts = relationship("LanguageDraft", back_populates="draft")
    technical_skill_drafts = relationship("TechnicalSkillDraft", back_populates="draft")
    soft_skill_drafts = relationship("SoftSkillDraft", back_populates="draft")
    project_drafts = relationship("ProjectDraft", back_populates="draft")

class Language(Base):
    __tablename__ = "languages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_id = Column(CHAR(6), ForeignKey("cv.id"))
    language_name = Column(String(100))
    proficiency = Column(SQLEnum(ProficiencyEnum, name="Proficiency", native_enum=True))
    description = Column(Text)

    cv = relationship("CV", back_populates="languages")

class LanguageDraft(Base):
    __tablename__ = "language_drafts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(CHAR(6), ForeignKey("cv_draft.id"))
    language_name = Column(String(100))
    proficiency = Column(SQLEnum(ProficiencyEnum, name="Proficiency", native_enum=True))
    description = Column(Text)

    draft = relationship("CVDraft", back_populates="language_drafts")

class TechnicalSkill(Base):
    __tablename__ = "technical_skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_id = Column(CHAR(6), ForeignKey("cv.id"))
    category = Column(SQLEnum(SkillCategoryEnum, name="SkillCategory", native_enum=True))
    skill_name = Column(String(255))
    description = Column(Text)

    cv = relationship("CV", back_populates="technical_skills")

class TechnicalSkillDraft(Base):
    __tablename__ = "technical_skill_drafts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(CHAR(6), ForeignKey("cv_draft.id"))
    category = Column(SQLEnum(SkillCategoryEnum, name="SkillCategory", native_enum=True))
    skill_name = Column(String(255))
    description = Column(Text)

    draft = relationship("CVDraft", back_populates="technical_skill_drafts")

class SoftSkill(Base):
    __tablename__ = "soft_skills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_id = Column(CHAR(6), ForeignKey("cv.id"))
    skill_name = Column(SQLEnum(SoftSkillEnum, name="SoftSkill", native_enum=True))
    description = Column(Text)

    cv = relationship("CV", back_populates="soft_skills")

class SoftSkillDraft(Base):
    __tablename__ = "soft_skill_drafts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(CHAR(6), ForeignKey("cv_draft.id"))
    skill_name = Column(SQLEnum(SoftSkillEnum, name="SoftSkill", native_enum=True))
    description = Column(Text)

    draft = relationship("CVDraft", back_populates="soft_skill_drafts")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cv_id = Column(CHAR(6), ForeignKey("cv.id"))
    project_name = Column(String(255))
    project_description = Column(Text)
    position = Column(String(255))
    responsibilities = Column(Text)
    programming_languages = Column(Text)

    cv = relationship("CV", back_populates="projects")

class ProjectDraft(Base):
    __tablename__ = "project_drafts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    draft_id = Column(CHAR(6), ForeignKey("cv_draft.id"))
    project_name = Column(String(255))
    project_description = Column(Text)
    position = Column(String(255))
    responsibilities = Column(Text)
    programming_languages = Column(Text)

    draft = relationship("CVDraft", back_populates="project_drafts")
