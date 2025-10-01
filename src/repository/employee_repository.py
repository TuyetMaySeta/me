import logging
import re
from typing import Any, Dict, List, Optional

from sqlalchemy import String, case, cast, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from src.core.models.employee import Employee
from src.core.models.employee_related import EmployeeTechnicalSkill

from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class EmployeeRepository(BaseRepository[Employee]):
    """Repository for Employee entity."""

    def __init__(self, db: Session):
        super().__init__(db, Employee)
        self.db_session = db

    def create_employee(self, employee_model: Employee) -> Employee:
        """Create a new employee from model instance"""
        self.db.add(employee_model)
        self.db.commit()
        logger.info(f"Successfully created employee: {employee_model.id}")
        return employee_model

    def get_employee_by_id(self, id: int) -> Optional[Employee]:
        """Get employee by ID"""
        return self.db.query(Employee).filter(Employee.id == id).first()

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        return self.db.query(Employee).filter(Employee.email == email).first()

    def get_employee_by_phone(self, phone: str) -> Optional[Employee]:
        """Get employee by phone"""
        return self.db.query(Employee).filter(Employee.phone == phone).first()

    def get_all_employees(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_direction: str = "asc",
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Employee]:
        """Get all employees with pagination and filtering"""
        try:
            query = self.db.query(Employee)
            # Filter

            query, skill_search = self._apply_filters(query, filters)

            if sort_by and hasattr(Employee, sort_by):
                sort_column = getattr(Employee, sort_by)
                if sort_direction.lower() == "desc":
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(Employee.created_at.desc())

            employees = query.offset(skip).limit(limit).all()

            if skill_search:

                def get_skill_priority(skill):
                    s = skill.skill_name.lower()
                    search = skill_search.lower()

                    if s == search:
                        return (0, s)
                    if s.startswith(search):
                        return (1, s)
                    if search in s:
                        return (2, s)
                    return (3, s)

                for emp in employees:
                    emp.technical_skills.sort(key=get_skill_priority)

            return employees
        except SQLAlchemyError:
            raise

    def count_total_employees(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count total employees with optional filters"""
        try:
            query = self.db.query(Employee)

            # Apply same filters as get_all_employees
            query, _ = self._apply_filters(query, filters)

            count = query.count()
            logger.debug(f"Total employees count: {count}")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Error counting employees: {str(e)}")
            raise

    def update_employee(
        self, employee_id: int, update_data: Dict[str, Any]
    ) -> Optional[Employee]:
        """Update employee with all nested relationships"""
        try:
            employee = self.get_employee_by_id(employee_id)
            if not employee:
                return None
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

            # Extract nested data
            nested_data = {
                "contacts": update_data.pop("contacts", None),
                "documents": update_data.pop("documents", None),
                "educations": update_data.pop("educations", None),
                "certifications": update_data.pop("certifications", None),
                "profile": update_data.pop("profile", None),
                "languages": update_data.pop("languages", None),
                "technical_skills": update_data.pop("technical_skills", None),
                "projects": update_data.pop("projects", None),
                "children": update_data.pop("children", None),
            }

            for field, value in update_data.items():
                if hasattr(employee, field) and value is not None:
                    setattr(employee, field, value)

            if nested_data["contacts"] is not None:
                for contact in employee.contacts:
                    self.db.delete(contact)
                for contact_data in nested_data["contacts"]:
                    self.db.add(
                        EmployeeContact(employee_id=employee_id, **contact_data)
                    )

            if nested_data["documents"] is not None:
                if employee.documents:
                    for field, value in nested_data["documents"].items():
                        setattr(employee.documents, field, value)
                else:
                    self.db.add(
                        EmployeeDocument(
                            employee_id=employee_id, **nested_data["documents"]
                        )
                    )

            if nested_data["educations"] is not None:
                for edu in employee.educations:
                    self.db.delete(edu)
                for edu_data in nested_data["educations"]:
                    self.db.add(EmployeeEducation(employee_id=employee_id, **edu_data))

            if nested_data["certifications"] is not None:
                for cert in employee.certifications:
                    self.db.delete(cert)
                for cert_data in nested_data["certifications"]:
                    self.db.add(
                        EmployeeCertification(employee_id=employee_id, **cert_data)
                    )

            if nested_data["profile"] is not None:
                if employee.profile:
                    for field, value in nested_data["profile"].items():
                        setattr(employee.profile, field, value)
                else:
                    self.db.add(
                        EmployeeProfile(
                            employee_id=employee_id, **nested_data["profile"]
                        )
                    )

            if nested_data["languages"] is not None:
                for lang in employee.languages:
                    self.db.delete(lang)
                for lang_data in nested_data["languages"]:
                    self.db.add(Language(employee_id=employee_id, **lang_data))

            if nested_data["technical_skills"] is not None:
                for skill in employee.technical_skills:
                    self.db.delete(skill)
                for skill_data in nested_data["technical_skills"]:
                    self.db.add(
                        EmployeeTechnicalSkill(employee_id=employee_id, **skill_data)
                    )

            if nested_data["projects"] is not None:
                for proj in employee.projects:
                    self.db.delete(proj)
                for proj_data in nested_data["projects"]:
                    self.db.add(EmployeeProject(employee_id=employee_id, **proj_data))

            if nested_data["children"] is not None:
                for child in employee.children:
                    self.db.delete(child)
                for child_data in nested_data["children"]:
                    self.db.add(EmployeeChild(employee_id=employee_id, **child_data))

            self.db.commit()
            self.db.refresh(employee)
            return employee

        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating employee {employee_id}: {e}")
            raise

    def update_employee_password(
        self, employee_id: int, new_hashed_password: str
    ) -> None:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise Exception("Employee not found")
        employee.hashed_password = new_hashed_password
        self.db.commit()

    def delete_employee(self, employee_tech_id: int) -> bool:
        """Delete employee by technical ID"""
        try:
            employee = self.get_employee_by_id(employee_tech_id)
            if not employee:
                return False

            self.db.delete(employee)
            self.db.commit()
            logger.info(f"Successfully deleted employee: {employee_tech_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting employee {employee_tech_id}: {str(e)}")
            raise

    # Existence check methods
    def employee_exists(self, employee_tech_id: int) -> bool:
        """Check if employee exists by technical ID"""
        try:
            exists = (
                self.db.query(Employee).filter(Employee.id == employee_tech_id).first()
                is not None
            )
            return exists
        except SQLAlchemyError as e:
            logger.error(
                f"Error checking employee existence {employee_tech_id}: {str(e)}"
            )
            raise

    def check_field_exists(
        self, field_checks: Dict[str, Any], exclude_employee_id: Optional[int] = None
    ) -> Optional[str]:
        try:
            from src.core.models.employee_related import EmployeeDocument

            employee_fields = ["email", "phone"]
            for field_name in employee_fields:
                field_value = field_checks.get(field_name)
                if not field_value:
                    continue

                query = self.db.query(Employee).filter(
                    getattr(Employee, field_name) == field_value
                )
                if exclude_employee_id:
                    query = query.filter(Employee.id != exclude_employee_id)

                if query.first():
                    return field_name

            document_fields = [
                "identity_number",
                "old_identity_number",
                "tax_id_number",
                "social_insurance_number",
                "account_bank_number",
                "motorbike_plate",
            ]
            for field_name in document_fields:
                field_value = field_checks.get(field_name)
                if not field_value:
                    continue

                query = self.db.query(EmployeeDocument).filter(
                    getattr(EmployeeDocument, field_name) == field_value
                )
                if exclude_employee_id:
                    query = query.filter(
                        EmployeeDocument.employee_id != exclude_employee_id
                    )

                if query.first():
                    return field_name

            return None

        except SQLAlchemyError:
            raise

    def verify_employee_exists_and_active(self, employee_id: int) -> bool:
        """Verify if employee exists and is active"""
        try:
            from src.core.enums import EmployeeStatusEnum

            employee = (
                self.db.query(Employee)
                .filter(
                    Employee.id == employee_id,
                    Employee.status == EmployeeStatusEnum.ACTIVE,
                )
                .first()
            )
            return employee is not None
        except SQLAlchemyError as e:
            logger.error(f"Error verifying employee {employee_id}: {str(e)}")
            return False

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]] = None):
        """Helper: apply filters to query"""
        if not filters:
            return query

        filter_map = {
            "id": lambda v: Employee.id == int(v),
            "email": lambda v: Employee.email.ilike(f"%{v}%"),
            "full_name": lambda v: Employee.full_name.ilike(f"%{v}%"),
            "phone": lambda v: Employee.phone.ilike(f"%{v}%"),
            "current_position": lambda v: Employee.current_position.ilike(f"%{v}%"),
            "gender": lambda v: Employee.gender.ilike(f"%{v}%"),
            "status": lambda v: Employee.status.ilike(f"%{v}%"),
            "marital_status": lambda v: Employee.marital_status.ilike(f"%{v}%"),
            "join_date_from": lambda v: Employee.join_date >= v,
            "join_date_to": lambda v: Employee.join_date <= v,
        }

        for key, filter_func in filter_map.items():
            if filters.get(key):
                query = query.filter(filter_func(filters[key]))

        if filters.get("skill_name"):
            skill_search = filters["skill_name"].lower()
            query = query.join(Employee.technical_skills).filter(
                EmployeeTechnicalSkill.skill_name.ilike(f"%{skill_search}%")
            )
            return query, skill_search

        return query, None
