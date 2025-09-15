# src/present/request/employee.py
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import datetime, date
import re

from src.core.enums import (
    GenderEnum, ProficiencyEnum, SkillCategoryEnum, 
    MaritalStatusEnum, EmployeeStatusEnum
)


# Base Employee Models - REMOVED employee_id field
class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None  # NO AGE VALIDATION
    marital_status: Optional[MaritalStatusEnum] = None
    join_date: Optional[date] = None
    current_position: Optional[str] = Field(None, max_length=255)
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None
    status: Optional[EmployeeStatusEnum] = EmployeeStatusEnum.ACTIVE

    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        """Validate full name"""
        if not v or not v.strip():
            raise ValueError('Full name is required and cannot be empty')
        
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Full name must be at least 2 characters')
        
        # Check if contains at least one letter
        if not re.search(r'[a-zA-ZÀ-ỹ]', v):
            raise ValueError('Full name must contain at least one letter')
        
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate Vietnamese phone number"""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        # Remove spaces, dashes, dots for validation
        clean_phone = re.sub(r'[\s\-\.]', '', v)
        
        # Vietnamese phone number patterns:
        # Mobile: 0 + (9 digits) = 10 digits total
        # Landline: 0 + area code (2-3 digits) + number (7-8 digits) = 10-11 digits total
        if not re.match(r'^0\d{9,10}$', clean_phone):
            raise ValueError('Phone number must be 10-11 digits starting with 0 (Vietnamese format)')
        
        # Check for valid mobile prefixes (03, 05, 07, 08, 09)
        if len(clean_phone) == 10:
            if not re.match(r'^0[3579]\d{8}$', clean_phone):
                raise ValueError('Mobile number must start with 03, 05, 07, 08, or 09')
        
        return clean_phone

    @field_validator('join_date')
    @classmethod
    def validate_join_date(cls, v):
        """Validate join date"""
        if v is None:
            return v
        
        today = date.today()
        
        # Cannot be in the future
        if v > today:
            raise ValueError('Join date cannot be in the future')
        
        # Cannot be more than 50 years ago
        min_join_date = date(today.year - 50, today.month, today.day)
        if v < min_join_date:
            raise ValueError('Join date cannot be more than 50 years ago')
        
        return v

    @field_validator('current_position')
    @classmethod
    def validate_current_position(cls, v):
        """Validate current position"""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        if len(v) < 2:
            raise ValueError('Position must be at least 2 characters')
        
        return v


# Employee Contact Models
class EmployeeContactBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    relation: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=15)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate contact name"""
        if not v or not v.strip():
            raise ValueError('Contact name is required')
        
        v = v.strip()
        if not re.search(r'[a-zA-ZÀ-ỹ]', v):
            raise ValueError('Contact name must contain at least one letter')
        
        return v

    @field_validator('relation')
    @classmethod
    def validate_relation(cls, v):
        """Validate relation"""
        if not v or not v.strip():
            raise ValueError('Relation is required')
        
        v = v.strip()
        valid_relations = [
            'spouse', 'father', 'mother', 'brother', 'sister', 'son', 'daughter',
            'emergency contact', 'friend', 'colleague', 'other'
        ]
        
        if v.lower() not in valid_relations:
            raise ValueError(f'Relation must be one of: {", ".join(valid_relations)}')
        
        return v.title()

    @field_validator('phone')
    @classmethod
    def validate_contact_phone(cls, v):
        """Validate contact phone number"""
        if not v or not v.strip():
            raise ValueError('Contact phone is required')
        
        v = v.strip()
        clean_phone = re.sub(r'[\s\-\.]', '', v)
        
        if not re.match(r'^0\d{9,10}$', clean_phone):
            raise ValueError('Contact phone must be 10-11 digits starting with 0')
        
        return clean_phone


class EmployeeContactCreate(EmployeeContactBase):
    pass

class EmployeeContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    relation: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=15)

class EmployeeContactResponse(EmployeeContactBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Employee Document Models with validation
class EmployeeDocumentBase(BaseModel):
    identity_number: Optional[str] = Field(None, max_length=20)
    identity_date: Optional[date] = None
    identity_place: Optional[str] = Field(None, max_length=255)
    old_identity_number: Optional[str] = Field(None, max_length=15)
    old_identity_date: Optional[date] = None
    old_identity_place: Optional[str] = Field(None, max_length=255)
    tax_id_number: Optional[str] = Field(None, max_length=15)
    social_insurance_number: Optional[str] = Field(None, max_length=15)
    bank_name: Optional[str] = Field(None, max_length=100)
    branch_name: Optional[str] = Field(None, max_length=255)
    account_bank_number: Optional[str] = Field(None, max_length=30)
    motorbike_plate: Optional[str] = Field(None, max_length=15)

    @field_validator('identity_number')
    @classmethod
    def validate_identity_number(cls, v):
        """Validate Vietnamese CCCD (12 digits)"""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        if not re.match(r'^\d{12}$', v):
            raise ValueError('Identity number (CCCD) must be exactly 12 digits')
        
        return v

    @field_validator('old_identity_number')
    @classmethod
    def validate_old_identity_number(cls, v):
        """Validate Vietnamese CMND (9 digits)"""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        if not re.match(r'^\d{9}$', v):
            raise ValueError('Old identity number (CMND) must be exactly 9 digits')
        
        return v

    @field_validator('tax_id_number')
    @classmethod
    def validate_tax_id_number(cls, v):
        """Validate Vietnamese tax ID (10-13 digits)"""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        if not re.match(r'^\d{10,13}$', v):
            raise ValueError('Tax ID number must be 10-13 digits')
        
        return v

    @field_validator('social_insurance_number')
    @classmethod
    def validate_social_insurance_number(cls, v):
        """Validate Vietnamese social insurance number"""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        if not re.match(r'^[A-Z]{2}\d{8}$', v):
            raise ValueError('Social insurance number must be 2 letters followed by 8 digits (e.g., HN12345678)')
        
        return v.upper()

    @field_validator('account_bank_number')
    @classmethod
    def validate_account_bank_number(cls, v):
        """Validate bank account number"""
        if v is None:
            return v
        
        v = v.strip()
        if not v:
            return None
        
        if not re.match(r'^\d{6,30}$', v):
            raise ValueError('Bank account number must be 6-30 digits')
        
        return v

    @field_validator('motorbike_plate')
    @classmethod
    def validate_motorbike_plate(cls, v):
        """Validate Vietnamese motorbike license plate"""
        if v is None:
            return v
        
        v = v.strip().replace('-', '').replace('.', '')
        if not v:
            return None
        
        # Vietnamese plate format: 12A12345 or 12AB12345
        if not re.match(r'^\d{2}[A-Z]{1,2}\d{4,5}$', v):
            raise ValueError('Motorbike plate must follow Vietnamese format (e.g., 30A12345 or 29AB12345)')
        
        return v.upper()


class EmployeeDocumentCreate(EmployeeDocumentBase):
    pass

class EmployeeDocumentUpdate(EmployeeDocumentBase):
    pass

class EmployeeDocumentResponse(EmployeeDocumentBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Language Models
class EmployeeLanguageBase(BaseModel):
    language_name: str = Field(..., min_length=2, max_length=100)
    proficiency: ProficiencyEnum
    description: Optional[str] = None

    @field_validator('language_name')
    @classmethod
    def validate_language_name(cls, v):
        """Validate language name"""
        if not v or not v.strip():
            raise ValueError('Language name is required')
        
        v = v.strip()
        if not re.match(r'^[a-zA-ZÀ-ỹ\s]+$', v):
            raise ValueError('Language name can only contain letters and spaces')
        
        return v.title()

class EmployeeLanguageCreate(EmployeeLanguageBase):
    pass

class EmployeeLanguageUpdate(BaseModel):
    language_name: Optional[str] = Field(None, min_length=2, max_length=100)
    proficiency: Optional[ProficiencyEnum] = None
    description: Optional[str] = None

class EmployeeLanguageResponse(EmployeeLanguageBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Technical Skill Models
class EmployeeTechnicalSkillBase(BaseModel):
    category: SkillCategoryEnum
    skill_name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None

    @field_validator('skill_name')
    @classmethod
    def validate_skill_name(cls, v):
        """Validate skill name"""
        if not v or not v.strip():
            raise ValueError('Skill name is required')
        
        return v.strip()

class EmployeeTechnicalSkillCreate(EmployeeTechnicalSkillBase):
    pass

class EmployeeTechnicalSkillUpdate(BaseModel):
    category: Optional[SkillCategoryEnum] = None
    skill_name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None

class EmployeeTechnicalSkillResponse(EmployeeTechnicalSkillBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Project Models
class EmployeeProjectBase(BaseModel):
    project_name: str = Field(..., min_length=2, max_length=255)
    project_description: Optional[str] = None
    position: Optional[str] = Field(None, max_length=255)
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None

    @field_validator('project_name')
    @classmethod
    def validate_project_name(cls, v):
        """Validate project name"""
        if not v or not v.strip():
            raise ValueError('Project name is required')
        
        return v.strip()

class EmployeeProjectCreate(EmployeeProjectBase):
    pass

class EmployeeProjectUpdate(BaseModel):
    project_name: Optional[str] = Field(None, min_length=2, max_length=255)
    project_description: Optional[str] = None
    position: Optional[str] = Field(None, max_length=255)
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None

class EmployeeProjectResponse(EmployeeProjectBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Main Employee Models - REMOVED employee_id field
class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None  # NO AGE VALIDATION
    marital_status: Optional[MaritalStatusEnum] = None
    join_date: Optional[date] = None
    current_position: Optional[str] = Field(None, max_length=255)
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None
    status: Optional[EmployeeStatusEnum] = None

    # Use the same validators from EmployeeBase (without employee_id)
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        if v is None:
            return v
        return EmployeeBase.validate_full_name(v)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        return EmployeeBase.validate_phone(v)

    @field_validator('join_date')
    @classmethod
    def validate_join_date(cls, v):
        if v is None:
            return v
        return EmployeeBase.validate_join_date(v)

    @field_validator('current_position')
    @classmethod
    def validate_current_position(cls, v):
        if v is None:
            return v
        return EmployeeBase.validate_current_position(v)

class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Employee with all details
class EmployeeWithDetails(Employee):
    contacts: List[EmployeeContactResponse] = []
    documents: List[EmployeeDocumentResponse] = []
    languages: List[EmployeeLanguageResponse] = []
    technical_skills: List[EmployeeTechnicalSkillResponse] = []
    projects: List[EmployeeProjectResponse] = []

# Employee Detail Create (for creating employee with all related data)
class EmployeeDetailCreate(EmployeeBase):
    contacts: Optional[List[EmployeeContactCreate]] = []
    documents: Optional[List[EmployeeDocumentCreate]] = []
    languages: Optional[List[EmployeeLanguageCreate]] = []
    technical_skills: Optional[List[EmployeeTechnicalSkillCreate]] = []
    projects: Optional[List[EmployeeProjectCreate]] = []

# Search and pagination with filters - REMOVED employee_id field and age validation
class EmployeeFilterRequest(BaseModel):
    # Basic filters
    email: Optional[str] = Field(None, description="Filter by email (partial match)")
    full_name: Optional[str] = Field(None, description="Filter by full name (partial match)")
    phone: Optional[str] = Field(None, description="Filter by phone number (partial match)")
    current_position: Optional[str] = Field(None, description="Filter by position (partial match)")
    
    # Enum filters
    gender: Optional[GenderEnum] = Field(None, description="Filter by gender")
    marital_status: Optional[MaritalStatusEnum] = Field(None, description="Filter by marital status")
    status: Optional[EmployeeStatusEnum] = Field(None, description="Filter by employee status")
    
    # Date range filters
    join_date_from: Optional[date] = Field(None, description="Filter employees joined from this date")
    join_date_to: Optional[date] = Field(None, description="Filter employees joined until this date")
    date_of_birth_from: Optional[date] = Field(None, description="Filter employees born from this date")
    date_of_birth_to: Optional[date] = Field(None, description="Filter employees born until this date")
    
    # Related data filters
    has_contacts: Optional[bool] = Field(None, description="Filter employees who have/don't have contacts")
    has_documents: Optional[bool] = Field(None, description="Filter employees who have/don't have documents")
    has_languages: Optional[bool] = Field(None, description="Filter employees who have/don't have language skills")
    has_technical_skills: Optional[bool] = Field(None, description="Filter employees who have/don't have technical skills")
    has_projects: Optional[bool] = Field(None, description="Filter employees who have/don't have project experience")
    
    # Language and skill filters
    language_name: Optional[str] = Field(None, description="Filter by specific language skill")
    technical_skill: Optional[str] = Field(None, description="Filter by specific technical skill")
    skill_category: Optional[SkillCategoryEnum] = Field(None, description="Filter by technical skill category")
    
    # Sorting
    sort_by: Optional[str] = Field("created_at", description="Sort field: id, full_name, email, join_date, created_at")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Sort order: asc or desc")
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number (starting from 1)")
    page_size: int = Field(10, ge=1, le=100, description="Number of records per page (max 100)")

    @field_validator('join_date_from', 'join_date_to')
    @classmethod
    def validate_join_dates(cls, v):
        if v and v > date.today():
            raise ValueError('Join date cannot be in the future')
        return v

class EmployeeSearchRequest(BaseModel):
    email: Optional[str] = None
    position: Optional[str] = None
    status: Optional[EmployeeStatusEnum] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=100)

class EmployeePaginationResponse(BaseModel):
    employees: List[EmployeeWithDetails]
    total: int
    page: int
    page_size: int
