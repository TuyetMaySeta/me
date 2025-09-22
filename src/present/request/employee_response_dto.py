

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from src.core.enums import EmployeeStatusEnum, GenderEnum, MaritalStatusEnum
from src.present.dto.employee_related.create_employee_related_dto import (
    EmployeeContactResponse,
    EmployeeDocumentResponse,
    EmployeeLanguageResponse,
    EmployeeProjectResponse,
    EmployeeTechnicalSkillResponse,
)


class EmployeeResponseDTO(BaseModel):
    id: int
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
    technical_skills: List[EmployeeTechnicalSkillResponse] = []

    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeWithDetailsResponseDTO(EmployeeResponseDTO):
    contacts: List[EmployeeContactResponse] = []
    documents: List[EmployeeDocumentResponse] = []
    languages: List[EmployeeLanguageResponse] = []
    technical_skills: List[EmployeeTechnicalSkillResponse] = []
    projects: List[EmployeeProjectResponse] = []


class EmployeePaginationDTO(BaseModel):
    employees: List[EmployeeResponseDTO]
    total: int
    page: int
    page_size: int
