from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from src.core.models.cv_models import ProficiencyEnum, SkillCategoryEnum, SoftSkillEnum, DraftStatusEnum

# Base schemas
class CVBase(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    current_position: Optional[str] = None
    summary: Optional[str] = None

class CVCreate(CVBase):
    id: str

class CVUpdate(CVBase):
    updated_at: Optional[datetime] = None

class CVInDBBase(CVBase):
    id: str
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CV(CVInDBBase):
    pass

class CVInDB(CVInDBBase):
    pass

# CV Draft schemas
class CVDraftBase(BaseModel):
    full_name: Optional[str] = None
    gender: Optional[str] = None
    current_position: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[DraftStatusEnum] = None

class CVDraftCreate(CVDraftBase):
    id: str

class CVDraftUpdate(CVDraftBase):
    updated_at: Optional[datetime] = None

class CVDraftInDBBase(CVDraftBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CVDraft(CVDraftInDBBase):
    pass

# Language schemas
class LanguageBase(BaseModel):
    language_name: Optional[str] = None
    proficiency: Optional[ProficiencyEnum] = None
    description: Optional[str] = None

class LanguageCreate(LanguageBase):
    cv_id: str

class LanguageUpdate(LanguageBase):
    pass

class LanguageInDBBase(LanguageBase):
    id: int
    cv_id: str
    
    class Config:
        from_attributes = True

class Language(LanguageInDBBase):
    pass

# Language Draft schemas
class LanguageDraftBase(BaseModel):
    language_name: Optional[str] = None
    proficiency: Optional[ProficiencyEnum] = None
    description: Optional[str] = None

class LanguageDraftCreate(LanguageDraftBase):
    draft_id: str

class LanguageDraftUpdate(LanguageDraftBase):
    pass

class LanguageDraftInDBBase(LanguageDraftBase):
    id: int
    draft_id: str
    
    class Config:
        from_attributes = True

class LanguageDraft(LanguageDraftInDBBase):
    pass

# Technical Skill schemas
class TechnicalSkillBase(BaseModel):
    category: Optional[SkillCategoryEnum] = None
    skill_name: Optional[str] = None
    description: Optional[str] = None

class TechnicalSkillCreate(TechnicalSkillBase):
    cv_id: str

class TechnicalSkillUpdate(TechnicalSkillBase):
    pass

class TechnicalSkillInDBBase(TechnicalSkillBase):
    id: int
    cv_id: str
    
    class Config:
        from_attributes = True

class TechnicalSkill(TechnicalSkillInDBBase):
    pass

# Technical Skill Draft schemas
class TechnicalSkillDraftBase(BaseModel):
    category: Optional[SkillCategoryEnum] = None
    skill_name: Optional[str] = None
    description: Optional[str] = None

class TechnicalSkillDraftCreate(TechnicalSkillDraftBase):
    draft_id: str

class TechnicalSkillDraftUpdate(TechnicalSkillDraftBase):
    pass

class TechnicalSkillDraftInDBBase(TechnicalSkillDraftBase):
    id: int
    draft_id: str
    
    class Config:
        from_attributes = True

class TechnicalSkillDraft(TechnicalSkillDraftInDBBase):
    pass

# Soft Skill schemas
class SoftSkillBase(BaseModel):
    skill_name: Optional[SoftSkillEnum] = None
    description: Optional[str] = None

class SoftSkillCreate(SoftSkillBase):
    cv_id: str

class SoftSkillUpdate(SoftSkillBase):
    pass

class SoftSkillInDBBase(SoftSkillBase):
    id: int
    cv_id: str
    
    class Config:
        from_attributes = True

class SoftSkill(SoftSkillInDBBase):
    pass

# Soft Skill Draft schemas
class SoftSkillDraftBase(BaseModel):
    skill_name: Optional[SoftSkillEnum] = None
    description: Optional[str] = None

class SoftSkillDraftCreate(SoftSkillDraftBase):
    draft_id: str

class SoftSkillDraftUpdate(SoftSkillDraftBase):
    pass

class SoftSkillDraftInDBBase(SoftSkillDraftBase):
    id: int
    draft_id: str
    
    class Config:
        from_attributes = True

class SoftSkillDraft(SoftSkillDraftInDBBase):
    pass

# Project schemas
class ProjectBase(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None

class ProjectCreate(ProjectBase):
    cv_id: str

class ProjectUpdate(ProjectBase):
    pass

class ProjectInDBBase(ProjectBase):
    id: int
    cv_id: str
    
    class Config:
        from_attributes = True

class Project(ProjectInDBBase):
    pass

# Project Draft schemas
class ProjectDraftBase(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None

class ProjectDraftCreate(ProjectDraftBase):
    draft_id: str

class ProjectDraftUpdate(ProjectDraftBase):
    pass

class ProjectDraftInDBBase(ProjectDraftBase):
    id: int
    draft_id: str
    
    class Config:
        from_attributes = True

class ProjectDraft(ProjectDraftInDBBase):
    pass