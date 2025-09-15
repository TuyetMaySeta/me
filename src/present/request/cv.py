# src/present/request/cv.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# Import từ centralized enums
from src.core.enums import GenderEnum, ProficiencyEnum, SkillCategoryEnum, SoftSkillEnum

# Language Request/Response
class LanguageBase(BaseModel):
    language_name: str
    proficiency: ProficiencyEnum
    description: Optional[str] = None

class LanguageCreate(LanguageBase):
    pass

class LanguageUpdate(BaseModel):
    language_name: Optional[str] = None
    proficiency: Optional[ProficiencyEnum] = None
    description: Optional[str] = None

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

class TechnicalSkillUpdate(BaseModel):
    category: Optional[SkillCategoryEnum] = None
    skill_name: Optional[str] = None
    description: Optional[str] = None

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

class SoftSkillUpdate(BaseModel):
    skill_name: Optional[SoftSkillEnum] = None
    description: Optional[str] = None

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

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None

class Project(ProjectBase):
    id: int
    cv_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# CV Request/Response
class CVBase(BaseModel):
    email: EmailStr
    full_name: str
    gender: Optional[GenderEnum] = None
    current_position: Optional[str] = None
    summary: Optional[str] = None
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Full name is required and cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()

class CVCreate(CVBase):
    # Optional related data for creating complete CV
    languages: Optional[List[LanguageCreate]] = []
    technical_skills: Optional[List[TechnicalSkillCreate]] = []
    soft_skills: Optional[List[SoftSkillCreate]] = []
    projects: Optional[List[ProjectCreate]] = []

class CVUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    gender: Optional[GenderEnum] = None
    current_position: Optional[str] = None
    summary: Optional[str] = None
    
    @validator('full_name')
    def validate_full_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Full name cannot be empty')
            if len(v.strip()) < 2:
                raise ValueError('Full name must be at least 2 characters')
            return v.strip()
        return v

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

# Search Request
class CVSearchRequest(BaseModel):
    email: Optional[str] = None
    position: Optional[str] = None
    skill: Optional[str] = None
    page: int = 1
    page_size: int = 10

# Pagination Response
class CVPaginationResponse(BaseModel):
    cvs: List[CV]
    total: int
    page: int
    page_size: int
    total_pages: int

# CV Component Create with CV ID
class CVComponentCreateRequest(BaseModel):
    cv_id: str
    languages: Optional[List[LanguageCreate]] = []
    technical_skills: Optional[List[TechnicalSkillCreate]] = []
    soft_skills: Optional[List[SoftSkillCreate]] = []
    projects: Optional[List[ProjectCreate]] = []

# CV Components Response
class CVComponentsResponse(BaseModel):
    cv_id: str
    languages: List[Language] = []
    technical_skills: List[TechnicalSkill] = []
    soft_skills: List[SoftSkill] = []
    projects: List[Project] = []
