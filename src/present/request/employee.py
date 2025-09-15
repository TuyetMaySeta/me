# src/present/request/employee.py
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
    employee_id: str
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
    employee_id: str
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
    employee_id: str
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
    employee_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Employee Request/Response
class EmployeeBase(BaseModel):
    email: EmailStr
    full_name: str
    employee_id: str  # Business ID (formerly id_seta)
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
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if not v or not v.strip():
            raise ValueError('Employee ID is required and cannot be empty')
        if len(v.strip()) < 3 or len(v.strip()) > 50:
            raise ValueError('Employee ID must be between 3 and 50 characters')
        return v.strip()

class EmployeeCreate(EmployeeBase):
    # Optional related data for creating complete Employee
    languages: Optional[List[LanguageCreate]] = []
    technical_skills: Optional[List[TechnicalSkillCreate]] = []
    soft_skills: Optional[List[SoftSkillCreate]] = []
    projects: Optional[List[ProjectCreate]] = []

class EmployeeUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    employee_id: Optional[str] = None  # Allow updating business ID
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
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Employee ID cannot be empty')
            if len(v.strip()) < 3 or len(v.strip()) > 50:
                raise ValueError('Employee ID must be between 3 and 50 characters')
            return v.strip()
        return v

class Employee(EmployeeBase):
    id: str  # Technical ID (6-char)
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EmployeeWithDetails(Employee):
    languages: List[Language] = []
    technical_skills: List[TechnicalSkill] = []
    soft_skills: List[SoftSkill] = []
    projects: List[Project] = []

# Bulk Operations
class EmployeeBulkCreate(BaseModel):
    employees: List[EmployeeCreate]

class EmployeeBulkResponse(BaseModel):
    created_count: int
    created_employees: List[Employee]
    errors: Optional[List[str]] = []

# Search Request
class EmployeeSearchRequest(BaseModel):
    email: Optional[str] = None
    position: Optional[str] = None
    employee_id: Optional[str] = None  # Search by business ID
    skill: Optional[str] = None
    page: int = 1
    page_size: int = 10

# Pagination Response
class EmployeePaginationResponse(BaseModel):
    employees: List[EmployeeWithDetails]  # Changed to EmployeeWithDetails
    total: int
    page: int
    page_size: int

# Simple Pagination Response (for cases where details not needed)
class EmployeeSimplePaginationResponse(BaseModel):
    employees: List[Employee]  # Simple Employee without components
    total: int
    page: int
    page_size: int



# Employee Component Create with Employee ID
class EmployeeComponentCreateRequest(BaseModel):
    employee_id: str  # Technical ID (6-char)
    languages: Optional[List[LanguageCreate]] = []
    technical_skills: Optional[List[TechnicalSkillCreate]] = []
    soft_skills: Optional[List[SoftSkillCreate]] = []
    projects: Optional[List[ProjectCreate]] = []

# Employee Components Response
class EmployeeComponentsResponse(BaseModel):
    employee_id: str  # Technical ID (6-char)
    languages: List[Language] = []
    technical_skills: List[TechnicalSkill] = []
    soft_skills: List[SoftSkill] = []
    projects: List[Project] = []