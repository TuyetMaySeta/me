# src/repository/employee_repository.py
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from src.core.models.employee import (
    Employee, EmployeeContact, EmployeeDocument, EmployeeEducation,
    EmployeeCertification, EmployeeProfile, Language,
    EmployeeTechnicalSkill, EmployeeProject, EmployeeChild
)

logger = logging.getLogger(__name__)


class EmployeeRepository(BaseRepository[Employee]):
    """Repository for Employee entity."""

    def __init__(self, db: Session):
        super().__init__(db, Employee)

    def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        """Create a new employee"""
        try:
            employee = self.create(employee_data)
            logger.info(f"Successfully created employee: {employee.id}")
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Failed to create employee: {str(e)}")
            raise

    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        """Get employee by ID"""
        try:
            employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
            if employee:
                logger.debug(f"Found employee: {employee_id}")
            else:
                logger.debug(f"Employee not found: {employee_id}")
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Error getting employee {employee_id}: {str(e)}")
            raise

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        try:
            employee = self.db.query(Employee).filter(Employee.email == email).first()
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Error getting employee by email {email}: {str(e)}")
            raise

    def get_all_employees(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Get all employees with pagination"""
        try:
            employees = (
                self.db.query(Employee)
                .offset(skip)
                .limit(limit)
                .all()
            )
            logger.debug(f"Retrieved {len(employees)} employees (skip={skip}, limit={limit})")
            return employees
        except SQLAlchemyError as e:
            logger.error(f"Error getting employees: {str(e)}")
            raise

    def update_employee(self, employee_id: int, update_data: Dict[str, Any]) -> Optional[Employee]:
        """Update employee by ID"""
        try:
            employee = self.get_employee_by_id(employee_id)
            if not employee:
                return None

            for field, value in update_data.items():
                if hasattr(employee, field) and value is not None:
                    setattr(employee, field, value)

            self.db.commit()
            self.db.refresh(employee)
            logger.info(f"Successfully updated employee: {employee_id}")
            return employee
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating employee {employee_id}: {str(e)}")
            raise

    def delete_employee(self, employee_id: int) -> bool:
        """Delete employee by ID"""
        try:
            employee = self.get_employee_by_id(employee_id)
            if not employee:
                return False

            self.db.delete(employee)
            self.db.commit()
            logger.info(f"Successfully deleted employee: {employee_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting employee {employee_id}: {str(e)}")
            raise

    def count_total_employees(self) -> int:
        """Count total employees"""
        try:
            count = self.db.query(Employee).count()
            logger.debug(f"Total employees count: {count}")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Error counting employees: {str(e)}")
            raise

    def search_employees(self, 
                        email: Optional[str] = None,
                        position: Optional[str] = None,
                        status: Optional[str] = None,
                        skip: int = 0,
                        limit: int = 100) -> List[Employee]:
        """Search employees by criteria"""
        try:
            query = self.db.query(Employee)

            if email:
                query = query.filter(Employee.email.ilike(f"%{email}%"))

            if position:
                query = query.filter(Employee.current_position.ilike(f"%{position}%"))

            if status:
                query = query.filter(Employee.status == status)

            employees = query.offset(skip).limit(limit).all()
            logger.debug(f"Search found {len(employees)} employees")
            return employees
        except SQLAlchemyError as e:
            logger.error(f"Error searching employees: {str(e)}")
            raise

    def employee_exists(self, employee_id: int) -> bool:
        """Check if employee exists by ID"""
        try:
            exists = self.db.query(Employee).filter(Employee.id == employee_id).first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking employee existence {employee_id}: {str(e)}")
            raise

    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email exists"""
        try:
            query = self.db.query(Employee).filter(Employee.email == email)
            if exclude_id:
                query = query.filter(Employee.id != exclude_id)
            
            exists = query.first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking email existence {email}: {str(e)}")
            raise

    def phone_exists(self, phone: str, exclude_id: Optional[int] = None) -> bool:
        """Check if phone exists"""
        try:
            query = self.db.query(Employee).filter(Employee.phone == phone)
            if exclude_id:
                query = query.filter(Employee.id != exclude_id)
            
            exists = query.first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking phone existence {phone}: {str(e)}")
            raise


# Helper repositories for related entities
class EmployeeContactRepository(BaseRepository[EmployeeContact]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeContact)

    def get_by_employee_id(self, employee_id: int) -> List[EmployeeContact]:
        return self.db.query(EmployeeContact).filter(EmployeeContact.employee_id == employee_id).all()

    def delete_by_employee_id(self, employee_id: int) -> int:
        count = self.db.query(EmployeeContact).filter(EmployeeContact.employee_id == employee_id).delete()
        self.db.commit()
        return count


class EmployeeDocumentRepository(BaseRepository[EmployeeDocument]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeDocument)

    def get_by_employee_id(self, employee_id: int) -> List[EmployeeDocument]:
        return self.db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == employee_id).all()


class EmployeeEducationRepository(BaseRepository[EmployeeEducation]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeEducation)

    def get_by_employee_id(self, employee_id: int) -> List[EmployeeEducation]:
        return self.db.query(EmployeeEducation).filter(EmployeeEducation.employee_id == employee_id).all()


class EmployeeCertificationRepository(BaseRepository[EmployeeCertification]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeCertification)

    def get_by_employee_id(self, employee_id: int) -> List[EmployeeCertification]:
        return self.db.query(EmployeeCertification).filter(EmployeeCertification.employee_id == employee_id).all()


class EmployeeProfileRepository(BaseRepository[EmployeeProfile]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeProfile)

    def get_by_employee_id(self, employee_id: int) -> List[EmployeeProfile]:
        return self.db.query(EmployeeProfile).filter(EmployeeProfile.employee_id == employee_id).all()


class LanguageRepository(BaseRepository[Language]):
    def __init__(self, db: Session):
        super().__init__(db, Language)

    def get_by_employee_id(self, employee_id: int) -> List[Language]:
        return self.db.query(Language).filter(Language.employee_id == employee_id).all()


class EmployeeTechnicalSkillRepository(BaseRepository[EmployeeTechnicalSkill]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeTechnicalSkill)

    def get_by_employee_id(self, employee_id: int) -> List[EmployeeTechnicalSkill]:
        return self.db.query(EmployeeTechnicalSkill).filter(EmployeeTechnicalSkill.employee_id == employee_id).all()


class EmployeeProjectRepository(BaseRepository[EmployeeProject]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeProject)

    def get_by_employee_id(self, employee_id: int) -> List[EmployeeProject]:
        return self.db.query(EmployeeProject).filter(EmployeeProject.employee_id == employee_id).all()


class EmployeeChildRepository(BaseRepository[EmployeeChild]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeChild)

    def get_by_employee_id(self, employee_id: int) -> List[EmployeeChild]:
        return self.db.query(EmployeeChild).filter(EmployeeChild.employee_id == employee_id).all()


# Bulk operations helper
class EmployeeRelatedBulkOperations:
    """Helper class for bulk operations across all employee-related repositories."""
    
    def __init__(self, db: Session):
        self.db = db
        self.contact_repo = EmployeeContactRepository(db)
        self.document_repo = EmployeeDocumentRepository(db)
        self.education_repo = EmployeeEducationRepository(db)
        self.certification_repo = EmployeeCertificationRepository(db)
        self.profile_repo = EmployeeProfileRepository(db)
        self.language_repo = LanguageRepository(db)
        self.tech_skill_repo = EmployeeTechnicalSkillRepository(db)
        self.project_repo = EmployeeProjectRepository(db)
        self.child_repo = EmployeeChildRepository(db)
    
    def get_all_employee_components(self, employee_id: int) -> Dict[str, List]:
        """Get all components for an employee."""
        try:
            return {
                'contacts': self.contact_repo.get_by_employee_id(employee_id),
                'documents': self.document_repo.get_by_employee_id(employee_id),
                'education': self.education_repo.get_by_employee_id(employee_id),
                'certifications': self.certification_repo.get_by_employee_id(employee_id),
                'profiles': self.profile_repo.get_by_employee_id(employee_id),
                'languages': self.language_repo.get_by_employee_id(employee_id),
                'technical_skills': self.tech_skill_repo.get_by_employee_id(employee_id),
                'projects': self.project_repo.get_by_employee_id(employee_id),
                'children': self.child_repo.get_by_employee_id(employee_id)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting employee components for {employee_id}: {str(e)}")
            raise

    def delete_all_employee_components(self, employee_id: int) -> Dict[str, int]:
        """Delete all components for an employee."""
        try:
            deleted_counts = {}
            deleted_counts['contacts'] = self.contact_repo.delete_by_employee_id(employee_id)
            deleted_counts['documents'] = self.db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == employee_id).delete()
            deleted_counts['education'] = self.db.query(EmployeeEducation).filter(EmployeeEducation.employee_id == employee_id).delete()
            deleted_counts['certifications'] = self.db.query(EmployeeCertification).filter(EmployeeCertification.employee_id == employee_id).delete()
            deleted_counts['profiles'] = self.db.query(EmployeeProfile).filter(EmployeeProfile.employee_id == employee_id).delete()
            deleted_counts['languages'] = self.db.query(Language).filter(Language.employee_id == employee_id).delete()
            deleted_counts['technical_skills'] = self.db.query(EmployeeTechnicalSkill).filter(EmployeeTechnicalSkill.employee_id == employee_id).delete()
            deleted_counts['projects'] = self.db.query(EmployeeProject).filter(EmployeeProject.employee_id == employee_id).delete()
            deleted_counts['children'] = self.db.query(EmployeeChild).filter(EmployeeChild.employee_id == employee_id).delete()
            
            self.db.commit()
            logger.info(f"Deleted all components for employee {employee_id}: {deleted_counts}")
            return deleted_counts
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting employee components for {employee_id}: {str(e)}")
            raise

    def bulk_create_employee_components(self, employee_id: int, components: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List]:
        """Bulk create all employee components."""
        results = {
            'contacts': [],
            'documents': [],
            'education': [],
            'certifications': [],
            'profiles': [],
            'languages': [],
            'technical_skills': [],
            'projects': [],
            'children': []
        }
        
        try:
            if 'contacts' in components:
                for contact_data in components['contacts']:
                    contact_data['employee_id'] = employee_id
                    results['contacts'].append(self.contact_repo.create(contact_data))
            
            if 'documents' in components:
                for doc_data in components['documents']:
                    doc_data['employee_id'] = employee_id
                    results['documents'].append(self.document_repo.create(doc_data))
            
            if 'education' in components:
                for edu_data in components['education']:
                    edu_data['employee_id'] = employee_id
                    results['education'].append(self.education_repo.create(edu_data))
            
            if 'certifications' in components:
                for cert_data in components['certifications']:
                    cert_data['employee_id'] = employee_id
                    results['certifications'].append(self.certification_repo.create(cert_data))
            
            if 'profiles' in components:
                for profile_data in components['profiles']:
                    profile_data['employee_id'] = employee_id
                    results['profiles'].append(self.profile_repo.create(profile_data))
            
            if 'languages' in components:
                for lang_data in components['languages']:
                    lang_data['employee_id'] = employee_id
                    results['languages'].append(self.language_repo.create(lang_data))
            
            if 'technical_skills' in components:
                for skill_data in components['technical_skills']:
                    skill_data['employee_id'] = employee_id
                    results['technical_skills'].append(self.tech_skill_repo.create(skill_data))
            
            if 'projects' in components:
                for proj_data in components['projects']:
                    proj_data['employee_id'] = employee_id
                    results['projects'].append(self.project_repo.create(proj_data))
            
            if 'children' in components:
                for child_data in components['children']:
                    child_data['employee_id'] = employee_id
                    results['children'].append(self.child_repo.create(child_data))
            
            logger.info(f"Successfully bulk created employee components for employee: {employee_id}")
            return results
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Bulk employee components creation failed for employee {employee_id}: {str(e)}")
            raise
