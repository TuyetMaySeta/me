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

class SoftSkill(SoftSkill
