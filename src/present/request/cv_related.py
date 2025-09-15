# src/present/request/cv_related.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

# Import từ centralized enums
from src.core.enums import ProficiencyEnum, SkillCategoryEnum, SoftSkillEnum

# Language Models
class LanguageCreateRequest(BaseModel):
    cv_id: str
    language_name: str
    proficiency: ProficiencyEnum
    description: Optional[str] = None
    
    @validator('cv_id')
    def validate_cv_id(cls, v):
        if not v or len(v) != 6:
            raise ValueError('CV ID must be exactly 6 characters')
        return v
    
    @validator('language_name')
    def validate_language_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Language name is required')
        if len(v) > 100:
            raise ValueError('Language name must not exceed 100 characters')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description must not exceed 1000 characters')
        return v

class LanguageUpdateRequest(BaseModel):
    language_name: Optional[str] = None
    proficiency: Optional[ProficiencyEnum] = None
    description: Optional[str] = None
    
    @validator('language_name')
    def validate_language_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Language name cannot be empty')
            if len(v) > 100:
                raise ValueError('Language name must not exceed 100 characters')
            return v.strip()
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description must not exceed 1000 characters')
        return v

class LanguageResponse(BaseModel):
    id: int
    cv_id: str
    language_name: str
    proficiency: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Technical Skill Models
class TechnicalSkillCreateRequest(BaseModel):
    cv_id: str
    category: SkillCategoryEnum
    skill_name: str
    description: Optional[str] = None
    
    @validator('cv_id')
    def validate_cv_id(cls, v):
        if not v or len(v) != 6:
            raise ValueError('CV ID must be exactly 6 characters')
        return v
    
    @validator('skill_name')
    def validate_skill_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Skill name is required')
        if len(v) > 255:
            raise ValueError('Skill name must not exceed 255 characters')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description must not exceed 1000 characters')
        return v

class TechnicalSkillUpdateRequest(BaseModel):
    category: Optional[SkillCategoryEnum] = None
    skill_name: Optional[str] = None
    description: Optional[str] = None
    
    @validator('skill_name')
    def validate_skill_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Skill name cannot be empty')
            if len(v) > 255:
                raise ValueError('Skill name must not exceed 255 characters')
            return v.strip()
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description must not exceed 1000 characters')
        return v

class TechnicalSkillResponse(BaseModel):
    id: int
    cv_id: str
    category: str
    skill_name: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Soft Skill Models
class SoftSkillCreateRequest(BaseModel):
    cv_id: str
    skill_name: SoftSkillEnum
    description: Optional[str] = None
    
    @validator('cv_id')
    def validate_cv_id(cls, v):
        if not v or len(v) != 6:
            raise ValueError('CV ID must be exactly 6 characters')
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description must not exceed 1000 characters')
        return v

class SoftSkillUpdateRequest(BaseModel):
    skill_name: Optional[SoftSkillEnum] = None
    description: Optional[str] = None
    
    @validator('description')
    def validate_description(cls, v):
        if v and len(v) > 1000:
            raise ValueError('Description must not exceed 1000 characters')
        return v

class SoftSkillResponse(BaseModel):
    id: int
    cv_id: str
    skill_name: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Project Models
class ProjectCreateRequest(BaseModel):
    cv_id: str
    project_name: str
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None
    
    @validator('cv_id')
    def validate_cv_id(cls, v):
        if not v or len(v) != 6:
            raise ValueError('CV ID must be exactly 6 characters')
        return v
    
    @validator('project_name')
    def validate_project_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Project name is required')
        if len(v) > 255:
            raise ValueError('Project name must not exceed 255 characters')
        return v.strip()
    
    @validator('project_description')
    def validate_project_description(cls, v):
        if v and len(v) > 2000:
            raise ValueError('Project description must not exceed 2000 characters')
        return v
    
    @validator('position')
    def validate_position(cls, v):
        if v and len(v) > 255:
            raise ValueError('Position must not exceed 255 characters')
        return v
    
    @validator('responsibilities')
    def validate_responsibilities(cls, v):
        if v and len(v) > 2000:
            raise ValueError('Responsibilities must not exceed 2000 characters')
        return v
    
    @validator('programming_languages')
    def validate_programming_languages(cls, v):
        if v and len(v) > 500:
            raise ValueError('Programming languages must not exceed 500 characters')
        return v

class ProjectUpdateRequest(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None
    
    @validator('project_name')
    def validate_project_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Project name cannot be empty')
            if len(v) > 255:
                raise ValueError('Project name must not exceed 255 characters')
            return v.strip()
        return v
    
    @validator('project_description')
    def validate_project_description(cls, v):
        if v and len(v) > 2000:
            raise ValueError('Project description must not exceed 2000 characters')
        return v
    
    @validator('position')
    def validate_position(cls, v):
        if v and len(v) > 255:
            raise ValueError('Position must not exceed 255 characters')
        return v
    
    @validator('responsibilities')
    def validate_responsibilities(cls, v):
        if v and len(v) > 2000:
            raise ValueError('Responsibilities must not exceed 2000 characters')
        return v
    
    @validator('programming_languages')
    def validate_programming_languages(cls, v):
        if v and len(v) > 500:
            raise ValueError('Programming languages must not exceed 500 characters')
        return v

class ProjectResponse(BaseModel):
    id: int
    cv_id: str
    project_name: str
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Bulk Operations for CV Components
class BulkComponentCreateRequest(BaseModel):
    cv_id: str
    languages: Optional[List[LanguageCreateRequest]] = []
    technical_skills: Optional[List[TechnicalSkillCreateRequest]] = []
    soft_skills: Optional[List[SoftSkillCreateRequest]] = []
    projects: Optional[List[ProjectCreateRequest]] = []

class BulkComponentResponse(BaseModel):
    cv_id: str
    created_counts: dict
    languages: List[LanguageResponse] = []
    technical_skills: List[TechnicalSkillResponse] = []
    soft_skills: List[SoftSkillResponse] = []
    projects: List[ProjectResponse] = []
