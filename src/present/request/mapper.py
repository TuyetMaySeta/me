

from src.core.models.employee import Employee
from src.core.models.employee_related import (
    EmployeeCertification,
    EmployeeChild,
    EmployeeContact,
    EmployeeDocument,
    EmployeeEducation,
    EmployeeProfile,
    EmployeeProject,
    EmployeeTechnicalSkill,
    Language,
)


def map_create_employee_dto_to_model(dto) -> Employee:
    """
    Map CreateEmployeeDTO -> Employee (SQLAlchemy model) cùng tất cả quan hệ.
    """
    employee = Employee(
        full_name=dto.full_name,
        email=dto.email,
        phone=dto.phone,
        gender=dto.gender,
        date_of_birth=dto.date_of_birth,
        marital_status=dto.marital_status,
        join_date=dto.join_date,
        current_position=dto.current_position,
        permanent_address=dto.permanent_address,
        current_address=dto.current_address,
        status=dto.status,
    )

    # One-to-Many
    if dto.contacts:
        employee.contacts = [EmployeeContact(**c.model_dump()) for c in dto.contacts]

    if dto.educations:
        employee.educations = [
            EmployeeEducation(**e.model_dump()) for e in dto.educations
        ]

    if dto.certifications:
        employee.certifications = [
            EmployeeCertification(**c.model_dump()) for c in dto.certifications
        ]

    if dto.languages:
        employee.languages = [Language(**l.model_dump()) for l in dto.languages]

    if dto.technical_skills:
        employee.technical_skills = [
            EmployeeTechnicalSkill(**s.model_dump()) for s in dto.technical_skills
        ]

    if dto.projects:
        employee.projects = [EmployeeProject(**p.model_dump()) for p in dto.projects]

    if dto.children:
        employee.children = [EmployeeChild(**ch.model_dump()) for ch in dto.children]

    # One-to-One
    if dto.documents:
        employee.documents = [EmployeeDocument(**dto.documents.model_dump())]

    if dto.profile:
        employee.profile = EmployeeProfile(**dto.profile.model_dump())

    return employee
