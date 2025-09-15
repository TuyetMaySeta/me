# src/present/request/employee.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date

from src.core.enums import (
    GenderEnum, ProficiencyEnum, SkillCategoryEnum, 
    SoftSkillEnum, MaritalStatusEnum, EmployeeStatusEnum
)

# Base Employee Models
class EmployeeBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    marital_status: Optional[MaritalStatusEnum] = None
    join_date: Optional[date] = None
    current_position: Optional[str] = None
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None
    status: Optional[EmployeeStatusEnum] = EmployeeStatusEnum.ACTIVE

    @validator('full_name')
    def validate_full_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Full name is required and cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()

# Employee Contact Models
class EmployeeContactBase(BaseModel):
    name: str
    relation: str
    phone: str

class EmployeeContactCreate(EmployeeContactBase):
    pass

class EmployeeContactUpdate(BaseModel):
    name: Optional[str] = None
    relation: Optional[str] = None
    phone: Optional[str] = None

class EmployeeContactResponse(EmployeeContactBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Employee Document Models
class EmployeeDocumentBase(BaseModel):
    identity_number: Optional[str] = None
    identity_date: Optional[date] = None
    identity_place: Optional[str] = None
    old_identity_number: Optional[str] = None
    old_identity_date: Optional[date] = None
    old_identity_place: Optional[str] = None
    tax_id_number: Optional[str] = None
    social_insurance_number: Optional[str] = None
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    account_bank_number: Optional[str] = None
    motorbike_plate: Optional[str] = None

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

# Employee Education Models
class EmployeeEducationBase(BaseModel):
    school_name: str
    graduation_year: Optional[int] = None
    degree: Optional[str] = None
    major: Optional[str] = None

class EmployeeEducationCreate(EmployeeEducationBase):
    pass

class EmployeeEducationUpdate(BaseModel):
    school_name: Optional[str] = None
    graduation_year: Optional[int] = None
    degree: Optional[str] = None
    major: Optional[str] = None

class EmployeeEducationResponse(EmployeeEducationBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Employee Certification Models
class EmployeeCertificationBase(BaseModel):
    certificate_name: str
    issued_by: str
    issued_date: Optional[date] = None
    expiry_date: Optional[date] = None

class EmployeeCertificationCreate(EmployeeCertificationBase):
    pass

class EmployeeCertificationUpdate(BaseModel):
    certificate_name: Optional[str] = None
    issued_by: Optional[str] = None
    issued_date: Optional[date] = None
    expiry_date: Optional[date] = None

class EmployeeCertificationResponse(EmployeeCertificationBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Employee Profile Models
class EmployeeProfileBase(BaseModel):
    facebook_link: Optional[str] = None
    linkedin_link: Optional[str] = None
    how_heard_about_company: Optional[str] = None
    hobbies: Optional[str] = None

class EmployeeProfileCreate(EmployeeProfileBase):
    pass

class EmployeeProfileUpdate(EmployeeProfileBase):
    pass

class EmployeeProfileResponse(EmployeeProfileBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Employee Language Models
class EmployeeLanguageBase(BaseModel):
    language_name: str
    proficiency: ProficiencyEnum
    description: Optional[str] = None

class EmployeeLanguageCreate(EmployeeLanguageBase):
    pass

class EmployeeLanguageUpdate(BaseModel):
    language_name: Optional[str] = None
    proficiency: Optional[ProficiencyEnum] = None
    description: Optional[str] = None

class EmployeeLanguageResponse(EmployeeLanguageBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Employee Technical Skill Models
class EmployeeTechnicalSkillBase(BaseModel):
    category: SkillCategoryEnum
    skill_name: str
    description: Optional[str] = None

class EmployeeTechnicalSkillCreate(EmployeeTechnicalSkillBase):
    pass

class EmployeeTechnicalSkillUpdate(BaseModel):
    category: Optional[SkillCategoryEnum] = None
    skill_name: Optional[str] = None
    description: Optional[str] = None

class EmployeeTechnicalSkillResponse(EmployeeTechnicalSkillBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Employee Project Models
class EmployeeProjectBase(BaseModel):
    project_name: str
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None

class EmployeeProjectCreate(EmployeeProjectBase):
    pass

class EmployeeProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None

class EmployeeProjectResponse(EmployeeProjectBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Employee Child Models
class EmployeeChildBase(BaseModel):
    full_name: str
    date_of_birth: date

class EmployeeChildCreate(EmployeeChildBase):
    pass

class EmployeeChildUpdate(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None

class EmployeeChildResponse(EmployeeChildBase):
    id: int
    employee_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Main Employee Models
class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gender: Optional[GenderEnum] = None
    date_of_birth: Optional[date] = None
    marital_status: Optional[MaritalStatusEnum] = None
    join_date: Optional[date] = None
    current_position: Optional[str] = None
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None
    status: Optional[EmployeeStatusEnum] = None

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
    education: List[EmployeeEducationResponse] = []
    certifications: List[EmployeeCertificationResponse] = []
    profiles: List[EmployeeProfileResponse] = []
    languages: List[EmployeeLanguageResponse] = []
    technical_skills: List[EmployeeTechnicalSkillResponse] = []
    projects: List[EmployeeProjectResponse] = []
    children: List[EmployeeChildResponse] = []

# Employee Detail Create (for creating employee with all related data)
class EmployeeDetailCreate(EmployeeBase):
    contacts: Optional[List[EmployeeContactCreate]] = []
    documents: Optional[List[EmployeeDocumentCreate]] = []
    education: Optional[List[EmployeeEducationCreate]] = []
    certifications: Optional[List[EmployeeCertificationCreate]] = []
    profiles: Optional[List[EmployeeProfileCreate]] = []
    languages: Optional[List[EmployeeLanguageCreate]] = []
    technical_skills: Optional[List[EmployeeTechnicalSkillCreate]] = []
    projects: Optional[List[EmployeeProjectCreate]] = []
    children: Optional[List[EmployeeChildCreate]] = []

# Bulk operations
class EmployeeBulkCreate(BaseModel):
    employees: List[EmployeeCreate]

class EmployeeBulkDetailCreate(BaseModel):
    employees: List[EmployeeDetailCreate]

class EmployeeBulkResponse(BaseModel):
    created_count: int
    created_employees: List[Employee]
    errors: Optional[List[str]] = []

class EmployeeBulkDetailResponse(BaseModel):
    created_count: int
    created_employees: List[EmployeeWithDetails]
    errors: Optional[List[str]] = []

# Search and pagination
class EmployeeSearchRequest(BaseModel):
    email: Optional[str] = None
    position: Optional[str] = None
    status: Optional[EmployeeStatusEnum] = None
    page: int = 1
    page_size: int = 10

class EmployeePaginationResponse(BaseModel):
    employees: List[EmployeeWithDetails]
    total: int
    page: int
    page_size: int
