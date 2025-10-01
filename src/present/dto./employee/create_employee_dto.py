import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.core.enums.employee import EmployeeStatusEnum, GenderEnum, MaritalStatusEnum
from src.present.dto.employee_related.create_employee_related_dto import (
    EmployeeCertificationDTO,
    EmployeeChildDTO,
    EmployeeContactDTO,
    EmployeeDocumentDTO,
    EmployeeEducationDTO,
    EmployeeProfileDTO,
    EmployeeProjectDTO,
    EmployeeTechnicalSkillDTO,
    LanguageDTO,
)


class CreateEmployeeDTO(BaseModel):
    full_name: str
    email: EmailStr = Field(..., example="a@example.com")
    phone: str = Field(..., example="0912345678")
    gender: GenderEnum = Field(..., example=GenderEnum.MALE)
    date_of_birth: date = Field(..., example="1990-01-01")
    marital_status: Optional[MaritalStatusEnum] = Field(
        None, example=MaritalStatusEnum.SINGLE
    )
    join_date: date = Field(..., example="2025-09-01")
    current_position: str = Field(..., example="Software Engineer")
    permanent_address: Optional[str] = None
    current_address: Optional[str] = None
    status: EmployeeStatusEnum = EmployeeStatusEnum.ACTIVE

    contacts: Optional[list[EmployeeContactDTO]] = None
    documents: Optional[EmployeeDocumentDTO] = None
    educations: Optional[list[EmployeeEducationDTO]] = None
    certifications: Optional[list[EmployeeCertificationDTO]] = None
    profile: Optional[EmployeeProfileDTO] = None
    languages: Optional[list[LanguageDTO]] = None
    technical_skills: Optional[list[EmployeeTechnicalSkillDTO]] = None
    projects: Optional[list[EmployeeProjectDTO]] = None
    children: Optional[list[EmployeeChildDTO]] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "full_name": "Nguyen Van A",
                "email": "nguyenvana@example.com",
                "phone": "0912345678",
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "marital_status": "Single",
                "join_date": "2025-09-01",
                "current_position": "Software Engineer",
                "permanent_address": "123 Đường A, Quận B, TP. HCM",
                "current_address": "456 Đường C, Quận D, TP. HCM",
                "status": "Active",
                "password": "Seta123@",
                "contacts": [
                    {
                        "name": "Nguyen Van B",
                        "relation": "Brother",
                        "phone": "0987654321",
                    }
                ],
                "documents": {
                    "identity_number": "123456789",
                    "identity_date": "2010-05-20",
                    "identity_place": "Hà Nội",
                    "old_identity_number": "987654321",
                    "old_identity_date": "2000-05-20",
                    "old_identity_place": "Hà Nam",
                    "tax_id_number": "TAX123456",
                    "social_insurance_number": "SI123456",
                    "bank_name": "Vietcombank",
                    "branch_name": "Chi nhánh Hà Nội",
                    "account_bank_number": "0123456789",
                    "motorbike_plate": "29A1-12345",
                },
                "educations": [
                    {
                        "school_name": "Đại học Bách Khoa Hà Nội",
                        "graduation_year": 2012,
                        "degree": "Cử nhân CNTT",
                        "major": "Khoa học máy tính",
                    },
                    {
                        "school_name": "Đại học FPT",
                        "graduation_year": 2014,
                        "degree": "Thạc sĩ CNTT",
                        "major": "Hệ thống thông tin",
                    },
                ],
                "certifications": [
                    {
                        "certificate_name": "AWS Certified Developer",
                        "issued_by": "Amazon",
                        "issued_date": "2020-01-01",
                        "expiry_date": "2023-01-01",
                    }
                ],
                "profile": {
                    "facebook_link": "https://facebook.com/nguyenvana",
                    "linkedin_link": "https://linkedin.com/in/nguyenvana",
                    "how_heard_about_company": "JobStreet",
                    "hobbies": "Đọc sách, đá bóng",
                },
                "languages": [
                    {
                        "language_name": "English",
                        "proficiency": "Fluent",
                        "description": "IELTS 7.5",
                    },
                    {
                        "language_name": "Japanese",
                        "proficiency": "Intermediate",
                        "description": "JLPT N3",
                    },
                ],
                "technical_skills": [
                    {
                        "category": "Programming Language",
                        "skill_name": "Go",
                        "description": "3 năm kinh nghiệm",
                    },
                    {
                        "category": "Database",
                        "skill_name": "PostgreSQL",
                        "description": "Hiểu rõ về index, transaction",
                    },
                ],
                "projects": [
                    {
                        "project_name": "Hệ thống Quản lý Nhân sự",
                        "project_description": "Quản lý hồ sơ nhân viên và chấm công",
                        "position": "Team Lead",
                        "responsibilities": "Thiết kế kiến trúc, review code",
                        "programming_languages": "Go, React",
                    }
                ],
                "children": [
                    {"full_name": "Nguyen Van C", "date_of_birth": "2015-06-01"}
                ],
            }
        }

    @field_validator("phone")
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        pattern = r"^0\d{9}$"  # 10 số, bắt đầu bằng 0
        if not re.match(pattern, value):
            raise ValueError("Số điện thoại không hợp lệ. VD: 0912345678")
        return value


class UpdateEmployeeDTO(BaseModel):
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

    contacts: Optional[list[EmployeeContactDTO]] = None
    documents: Optional[EmployeeDocumentDTO] = None
    educations: Optional[list[EmployeeEducationDTO]] = None
    certifications: Optional[list[EmployeeCertificationDTO]] = None
    profile: Optional[EmployeeProfileDTO] = None
    languages: Optional[list[LanguageDTO]] = None
    technical_skills: Optional[list[EmployeeTechnicalSkillDTO]] = None
    projects: Optional[list[EmployeeProjectDTO]] = None
    children: Optional[list[EmployeeChildDTO]] = None

    class Config:
        from_attributes = True
