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


class EmployeeMapper:
    def map_create_employee_dto_to_model(self, dto) -> Employee:
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
            employee.contacts = [
                EmployeeContact(**contact.model_dump()) for contact in dto.contacts
            ]

        if dto.educations:
            employee.educations = [
                EmployeeEducation(**education.model_dump())
                for education in dto.educations
            ]

        if dto.certifications:
            employee.certifications = [
                EmployeeCertification(**certification.model_dump())
                for certification in dto.certifications
            ]

        if dto.languages:
            employee.languages = [
                Language(**language.model_dump()) for language in dto.languages
            ]

        if dto.technical_skills:
            employee.technical_skills = [
                EmployeeTechnicalSkill(**s.model_dump()) for s in dto.technical_skills
            ]

        if dto.projects:
            employee.projects = [
                EmployeeProject(**project.model_dump()) for project in dto.projects
            ]

        if dto.children:
            employee.children = [
                EmployeeChild(**child.model_dump()) for child in dto.children
            ]

        # One-to-One
        if dto.documents:
            employee.documents = [EmployeeDocument(**dto.documents.model_dump())]

        if dto.profile:
            employee.profile = EmployeeProfile(**dto.profile.model_dump())

        return employee
