from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.core.enums import ProficiencyEnum, SkillCategoryEnum


class EmployeeContactDTO(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
    name: str = Field(..., max_length=255)
    relation: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=15)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeDocumentDTO(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
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
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeEducationDTO(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
    school_name: str = Field(..., max_length=255)
    graduation_year: Optional[int] = None
    degree: Optional[str] = Field(None, max_length=255)
    major: Optional[str] = Field(None, max_length=255)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeCertificationDTO(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
    certificate_name: str = Field(..., max_length=255)
    issued_by: str = Field(..., max_length=255)
    issued_date: Optional[date] = None
    expiry_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeProfileDTO(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
    facebook_link: Optional[str] = Field(None, max_length=500)
    linkedin_link: Optional[str] = Field(None, max_length=500)
    how_heard_about_company: Optional[str] = None
    hobbies: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LanguageDTO(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
    language_name: str = Field(..., max_length=100)
    proficiency: ProficiencyEnum
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeTechnicalSkillDTO(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
    category: SkillCategoryEnum
    skill_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeProjectDTO(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
    project_name: str = Field(..., max_length=255)
    project_description: Optional[str] = None
    position: Optional[str] = Field(None, max_length=255)
    responsibilities: Optional[str] = None
    programming_languages: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeChildDTO(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
    full_name: str = Field(..., max_length=255)
    date_of_birth: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Response DTOs (moved from request models)
class EmployeeContactResponse(BaseModel):
    id: int
    employee_id: int
    name: str
    relation: str
    phone: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeDocumentResponse(BaseModel):
    id: int
    employee_id: int
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
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeLanguageResponse(BaseModel):
    id: int
    employee_id: int
    language_name: str
    proficiency: ProficiencyEnum
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeTechnicalSkillResponse(BaseModel):
    id: int
    employee_id: int
    category: SkillCategoryEnum
    skill_name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeProjectResponse(BaseModel):
    id: int
    employee_id: int
    project_name: str
    project_description: Optional[str] = None
    position: Optional[str] = None
    responsibilities: Optional[str] = None

    programming_languages: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
