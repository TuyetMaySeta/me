from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class ProficiencyEnum(str, Enum):
    NATIVE = "Native"
    FLUENT = "Fluent"
    INTERMEDIATE = "Intermediate"
    BASIC = "Basic"

class SkillCategoryEnum(str, Enum):
    PROGRAMMING_LANGUAGE = "Programming Language"
    DATABASE = "Database"
    FRAMEWORK = "Framework"
    TOOL = "Tool"
    HARDWARE = "Hardware"

class SoftSkillEnum(str, Enum):
    COMMUNICATION = "Communication"
    TEAMWORK = "Teamwork"
    PROBLEM_SOLVING = "Problem Solving"
    DECISION_MAKING = "Decision Making"
    LEADERSHIP = "Leadership"
    TIME_MANAGEMENT = "Time Management"
    ADAPTABILITY = "Adaptability"
    OTHER = "Other"

# Language Request/Response
class LanguageBase(BaseModel):
    language_name: str
    proficiency: ProficiencyEnum
    description: Optional[str] = None

class LanguageCreate(LanguageBase):
    pass

class Language(LanguageBase):
    id: int
    cv_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Technical Skill Request/Response
class TechnicalSkillBase(BaseModel):
    category: SkillCategoryEnum
    skill_name: str
    description: Optional[str] = None

class TechnicalSkillCreate(TechnicalSkillBase):
    pass

class TechnicalSkill(TechnicalSkillBase):
    id: int
    cv_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Soft Skill Request/Response
class SoftSkillBase(BaseModel):
    skill_name: SoftSkillEnum
    description: Optional[str] = None

class SoftSkillCreate(SoftSkillBase):
    pass

class SoftSkill(SoftSkillBase):
    id: int
    cv_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Project Request/Response
class ProjectBase(BaseModel):
    project_name: str
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    cv_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# CV Request/Response
class CVBase(BaseModel):
    id_seta: str
    email: EmailStr
    full_name: str
    gender: Optional[GenderEnum] = None
    current_position: Optional[str] = None
    summary: Optional[str] = None
    
    @validator('id_seta')
    def validate_id_seta(cls, v):
        if not v.upper().startswith('EMP'):
            raise ValueError('SETA ID must start with EMP prefix')
        return v

class CVCreate(CVBase):
    # Optional related data for creating complete CV
    languages: Optional[List[LanguageCreate]] = []
    technical_skills: Optional[List[TechnicalSkillCreate]] = []
    soft_skills: Optional[List[SoftSkillCreate]] = []
    projects: Optional[List[ProjectCreate]] = []

class CVUpdate(BaseModel):
    id_seta: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    current_position: Optional[str] = None
    summary: Optional[str] = None

class CV(CVBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CVWithDetails(CV):
    languages: List[Language] = []
    technical_skills: List[TechnicalSkill] = []
    soft_skills: List[SoftSkill] = []
    projects: List[Project] = []

# Bulk Operations
class CVBulkCreate(BaseModel):
    cvs: List[CVCreate]

class CVBulkResponse(BaseModel):
    created_count: int
    created_cvs: List[CV]
    errors: Optional[List[str]] = []