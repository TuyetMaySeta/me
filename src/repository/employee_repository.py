# src/repository/employee_repository.py
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from src.core.models.employee import Employee
from src.core.models.employee_related import (
    EmployeeContact, EmployeeDocument, EmployeeEducation,
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

    def get_employee_by_id(self, employee_tech_id: int) -> Optional[Employee]:
        """Get employee by technical ID"""
        try:
            employee = self.db.query(Employee).filter(Employee.id == employee_tech_id).first()
            if employee:
                logger.debug(f"Found employee: {employee_tech_id}")
            else:
                logger.debug(f"Employee not found: {employee_tech_id}")
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Error getting employee {employee_tech_id}: {str(e)}")
            raise

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email"""
        try:
            employee = self.db.query(Employee).filter(Employee.email == email).first()
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Error getting employee by email {email}: {str(e)}")
            raise

    def get_employee_by_phone(self, phone: str) -> Optional[Employee]:
        """Get employee by phone"""
        try:
            employee = self.db.query(Employee).filter(Employee.phone == phone).first()
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Error getting employee by phone {phone}: {str(e)}")
            raise

    def get_all_employees(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        """Get all employees with pagination"""
        try:
            employees = (
                self.db.query(Employee)
                .order_by(Employee.created_at.desc())  # Order by newest first
                .offset(skip)
                .limit(limit)
                .all()
            )
            logger.debug(f"Retrieved {len(employees)} employees (skip={skip}, limit={limit})")
            return employees
        except SQLAlchemyError as e:
            logger.error(f"Error getting employees: {str(e)}")
            raise

    def update_employee(self, employee_tech_id: int, update_data: Dict[str, Any]) -> Optional[Employee]:
        """Update employee by technical ID"""
        try:
            employee = self.get_employee_by_id(employee_tech_id)
            if not employee:
                return None

            for field, value in update_data.items():
                if hasattr(employee, field) and value is not None:
                    setattr(employee, field, value)

            self.db.commit()
            self.db.refresh(employee)
            logger.info(f"Successfully updated employee: {employee_tech_id}")
            return employee
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating employee {employee_tech_id}: {str(e)}")
            raise

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

            employees = query.order_by(Employee.created_at.desc()).offset(skip).limit(limit).all()
            logger.debug(f"Search found {len(employees)} employees")
            return employees
        except SQLAlchemyError as e:
            logger.error(f"Error searching employees: {str(e)}")
            raise

    # Existence check methods
    def employee_exists(self, employee_tech_id: int) -> bool:
        """Check if employee exists by technical ID"""
        try:
            exists = self.db.query(Employee).filter(Employee.id == employee_tech_id).first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking employee existence {employee_tech_id}: {str(e)}")
            raise

    def email_exists(self, email: str, exclude_tech_id: Optional[int] = None) -> bool:
        """Check if email exists"""
        try:
            query = self.db.query(Employee).filter(Employee.email == email)
            if exclude_tech_id:
                query = query.filter(Employee.id != exclude_tech_id)
            
            exists = query.first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking email existence {email}: {str(e)}")
            raise

    def phone_exists(self, phone: str, exclude_tech_id: Optional[int] = None) -> bool:
        """Check if phone exists"""
        try:
            query = self.db.query(Employee).filter(Employee.phone == phone)
            if exclude_tech_id:
                query = query.filter(Employee.id != exclude_tech_id)
            
            exists = query.first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking phone existence {phone}: {str(e)}")
            raise

    def filter_employees_with_details(self, filters: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Employee]:
        """Advanced filter employees with support for related data filters"""
        try:
            from sqlalchemy import and_, or_, func, extract
            from datetime import date
            
            query = self.db.query(Employee)
            
            # Basic string filters (case-insensitive partial match)
            if filters.get('email'):
                query = query.filter(Employee.email.ilike(f"%{filters['email']}%"))
            
            if filters.get('full_name'):
                query = query.filter(Employee.full_name.ilike(f"%{filters['full_name']}%"))
            
            if filters.get('phone'):
                query = query.filter(Employee.phone.ilike(f"%{filters['phone']}%"))
            
            if filters.get('current_position'):
                query = query.filter(Employee.current_position.ilike(f"%{filters['current_position']}%"))
            
            # Enum filters (exact match)
            if filters.get('gender'):
                query = query.filter(Employee.gender == filters['gender'])
            
            if filters.get('marital_status'):
                query = query.filter(Employee.marital_status == filters['marital_status'])
            
            if filters.get('status'):
                query = query.filter(Employee.status == filters['status'])
            
            # Date range filters
            if filters.get('join_date_from'):
                query = query.filter(Employee.join_date >= filters['join_date_from'])
            
            if filters.get('join_date_to'):
                query = query.filter(Employee.join_date <= filters['join_date_to'])
            
            if filters.get('date_of_birth_from'):
                query = query.filter(Employee.date_of_birth >= filters['date_of_birth_from'])
            
            if filters.get('date_of_birth_to'):
                query = query.filter(Employee.date_of_birth <= filters['date_of_birth_to'])
            
            # Related data existence filters
            if filters.get('has_contacts') is not None:
                if filters['has_contacts']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(EmployeeContact.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(EmployeeContact.employee_id).distinct()
                    ))
            
            if filters.get('has_documents') is not None:
                if filters['has_documents']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(EmployeeDocument.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(EmployeeDocument.employee_id).distinct()
                    ))
            
            if filters.get('has_languages') is not None:
                if filters['has_languages']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(Language.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(Language.employee_id).distinct()
                    ))
            
            if filters.get('has_technical_skills') is not None:
                if filters['has_technical_skills']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(EmployeeTechnicalSkill.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(EmployeeTechnicalSkill.employee_id).distinct()
                    ))
            
            if filters.get('has_projects') is not None:
                if filters['has_projects']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(EmployeeProject.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(EmployeeProject.employee_id).distinct()
                    ))
            
            # Specific skill filters
            if filters.get('language_name'):
                query = query.filter(Employee.id.in_(
                    self.db.query(Language.employee_id).filter(
                        Language.language_name.ilike(f"%{filters['language_name']}%")
                    )
                ))
            
            if filters.get('technical_skill'):
                query = query.filter(Employee.id.in_(
                    self.db.query(EmployeeTechnicalSkill.employee_id).filter(
                        EmployeeTechnicalSkill.skill_name.ilike(f"%{filters['technical_skill']}%")
                    )
                ))
            
            if filters.get('skill_category'):
                query = query.filter(Employee.id.in_(
                    self.db.query(EmployeeTechnicalSkill.employee_id).filter(
                        EmployeeTechnicalSkill.category == filters['skill_category']
                    )
                ))
            
            # Sorting
            sort_by = filters.get('sort_by', 'created_at')
            sort_order = filters.get('sort_order', 'desc')
            
            # Validate sort field
            valid_sort_fields = ['id', 'full_name', 'email', 'join_date', 'created_at']
            if sort_by not in valid_sort_fields:
                sort_by = 'created_at'
            
            sort_column = getattr(Employee, sort_by)
            if sort_order.lower() == 'asc':
                query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(sort_column.desc())
            
            # Apply pagination
            employees = query.offset(skip).limit(limit).all()
            
            logger.debug(f"Filter found {len(employees)} employees with filters: {filters}")
            return employees
            
        except SQLAlchemyError as e:
            logger.error(f"Error filtering employees: {str(e)}")
            raise

    def count_filtered_employees(self, filters: Dict[str, Any]) -> int:
        """Count total employees matching the filters"""
        try:
            from sqlalchemy import and_, or_, func
            from datetime import date
            
            query = self.db.query(Employee)
            
            # Apply same filters as filter_employees_with_details but without pagination
            # Basic string filters
            if filters.get('email'):
                query = query.filter(Employee.email.ilike(f"%{filters['email']}%"))
            
            if filters.get('full_name'):
                query = query.filter(Employee.full_name.ilike(f"%{filters['full_name']}%"))
            
            if filters.get('phone'):
                query = query.filter(Employee.phone.ilike(f"%{filters['phone']}%"))
            
            if filters.get('current_position'):
                query = query.filter(Employee.current_position.ilike(f"%{filters['current_position']}%"))
            
            # Enum filters
            if filters.get('gender'):
                query = query.filter(Employee.gender == filters['gender'])
            
            if filters.get('marital_status'):
                query = query.filter(Employee.marital_status == filters['marital_status'])
            
            if filters.get('status'):
                query = query.filter(Employee.status == filters['status'])
            
            # Date range filters
            if filters.get('join_date_from'):
                query = query.filter(Employee.join_date >= filters['join_date_from'])
            
            if filters.get('join_date_to'):
                query = query.filter(Employee.join_date <= filters['join_date_to'])
            
            if filters.get('date_of_birth_from'):
                query = query.filter(Employee.date_of_birth >= filters['date_of_birth_from'])
            
            if filters.get('date_of_birth_to'):
                query = query.filter(Employee.date_of_birth <= filters['date_of_birth_to'])
            
            # Related data existence filters (same as above)
            if filters.get('has_contacts') is not None:
                if filters['has_contacts']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(EmployeeContact.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(EmployeeContact.employee_id).distinct()
                    ))
            
            if filters.get('has_documents') is not None:
                if filters['has_documents']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(EmployeeDocument.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(EmployeeDocument.employee_id).distinct()
                    ))
            
            if filters.get('has_languages') is not None:
                if filters['has_languages']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(Language.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(Language.employee_id).distinct()
                    ))
            
            if filters.get('has_technical_skills') is not None:
                if filters['has_technical_skills']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(EmployeeTechnicalSkill.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(EmployeeTechnicalSkill.employee_id).distinct()
                    ))
            
            if filters.get('has_projects') is not None:
                if filters['has_projects']:
                    query = query.filter(Employee.id.in_(
                        self.db.query(EmployeeProject.employee_id).distinct()
                    ))
                else:
                    query = query.filter(~Employee.id.in_(
                        self.db.query(EmployeeProject.employee_id).distinct()
                    ))
            
            # Specific skill filters
            if filters.get('language_name'):
                query = query.filter(Employee.id.in_(
                    self.db.query(Language.employee_id).filter(
                        Language.language_name.ilike(f"%{filters['language_name']}%")
                    )
                ))
            
            if filters.get('technical_skill'):
                query = query.filter(Employee.id.in_(
                    self.db.query(EmployeeTechnicalSkill.employee_id).filter(
                        EmployeeTechnicalSkill.skill_name.ilike(f"%{filters['technical_skill']}%")
                    )
                ))
            
            if filters.get('skill_category'):
                query = query.filter(Employee.id.in_(
                    self.db.query(EmployeeTechnicalSkill.employee_id).filter(
                        EmployeeTechnicalSkill.category == filters['skill_category']
                    )
                ))
            
            count = query.count()
            logger.debug(f"Total filtered employees count: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting filtered employees: {str(e)}")
            raise


# Helper repositories for related entities
class EmployeeContactRepository(BaseRepository[EmployeeContact]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeContact)

    def get_by_employee_id(self, employee_tech_id: int) -> List[EmployeeContact]:
        return self.db.query(EmployeeContact).filter(EmployeeContact.employee_id == employee_tech_id).all()

    def delete_by_employee_id(self, employee_tech_id: int) -> int:
        count = self.db.query(EmployeeContact).filter(EmployeeContact.employee_id == employee_tech_id).delete()
        self.db.commit()
        return count


class EmployeeDocumentRepository(BaseRepository[EmployeeDocument]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeDocument)

    def get_by_employee_id(self, employee_tech_id: int) -> List[EmployeeDocument]:
        return self.db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == employee_tech_id).all()


class LanguageRepository(BaseRepository[Language]):
    def __init__(self, db: Session):
        super().__init__(db, Language)

    def get_by_employee_id(self, employee_tech_id: int) -> List[Language]:
        return self.db.query(Language).filter(Language.employee_id == employee_tech_id).all()


class EmployeeTechnicalSkillRepository(BaseRepository[EmployeeTechnicalSkill]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeTechnicalSkill)

    def get_by_employee_id(self, employee_tech_id: int) -> List[EmployeeTechnicalSkill]:
        return self.db.query(EmployeeTechnicalSkill).filter(EmployeeTechnicalSkill.employee_id == employee_tech_id).all()


class EmployeeProjectRepository(BaseRepository[EmployeeProject]):
    def __init__(self, db: Session):
        super().__init__(db, EmployeeProject)

    def get_by_employee_id(self, employee_tech_id: int) -> List[EmployeeProject]:
        return self.db.query(EmployeeProject).filter(EmployeeProject.employee_id == employee_tech_id).all()


# Bulk operations helper
class EmployeeRelatedBulkOperations:
    """Helper class for bulk operations across all employee-related repositories."""
    
    def __init__(self, db: Session):
        self.db = db
        self.contact_repo = EmployeeContactRepository(db)
        self.document_repo = EmployeeDocumentRepository(db)
        self.language_repo = LanguageRepository(db)
        self.tech_skill_repo = EmployeeTechnicalSkillRepository(db)
        self.project_repo = EmployeeProjectRepository(db)
    
    def get_all_employee_components(self, employee_tech_id: int) -> Dict[str, List]:
        """Get all components for an employee."""
        try:
            return {
                'contacts': self.contact_repo.get_by_employee_id(employee_tech_id),
                'documents': self.document_repo.get_by_employee_id(employee_tech_id),
                'languages': self.language_repo.get_by_employee_id(employee_tech_id),
                'technical_skills': self.tech_skill_repo.get_by_employee_id(employee_tech_id),
                'projects': self.project_repo.get_by_employee_id(employee_tech_id)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting employee components for {employee_tech_id}: {str(e)}")
            raise

    def delete_all_employee_components(self, employee_tech_id: int) -> Dict[str, int]:
        """Delete all components for an employee."""
        try:
            deleted_counts = {}
            deleted_counts['contacts'] = self.contact_repo.delete_by_employee_id(employee_tech_id)
            deleted_counts['documents'] = self.db.query(EmployeeDocument).filter(EmployeeDocument.employee_id == employee_tech_id).delete()
            deleted_counts['languages'] = self.db.query(Language).filter(Language.employee_id == employee_tech_id).delete()
            deleted_counts['technical_skills'] = self.db.query(EmployeeTechnicalSkill).filter(EmployeeTechnicalSkill.employee_id == employee_tech_id).delete()
            deleted_counts['projects'] = self.db.query(EmployeeProject).filter(EmployeeProject.employee_id == employee_tech_id).delete()
            
            self.db.commit()
            logger.info(f"Deleted all components for employee {employee_tech_id}: {deleted_counts}")
            return deleted_counts
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting employee components for {employee_tech_id}: {str(e)}")
            raise

    def bulk_create_employee_components(self, employee_tech_id: int, components: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List]:
        """Bulk create all employee components."""
        results = {
            'contacts': [],
            'documents': [],
            'languages': [],
            'technical_skills': [],
            'projects': []
        }
        
        try:
            if 'contacts' in components:
                for contact_data in components['contacts']:
                    contact_data['employee_id'] = employee_tech_id
                    results['contacts'].append(self.contact_repo.create(contact_data))
            
            if 'documents' in components:
                for doc_data in components['documents']:
                    doc_data['employee_id'] = employee_tech_id
                    results['documents'].append(self.document_repo.create(doc_data))
            
            if 'languages' in components:
                for lang_data in components['languages']:
                    lang_data['employee_id'] = employee_tech_id
                    results['languages'].append(self.language_repo.create(lang_data))
            
            if 'technical_skills' in components:
                for skill_data in components['technical_skills']:
                    skill_data['employee_id'] = employee_tech_id
                    results['technical_skills'].append(self.tech_skill_repo.create(skill_data))
            
            if 'projects' in components:
                for proj_data in components['projects']:
                    proj_data['employee_id'] = employee_tech_id
                    results['projects'].append(self.project_repo.create(proj_data))
            
            logger.info(f"Successfully bulk created employee components for employee: {employee_tech_id}")
            return results
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error bulk creating employee components for {employee_tech_id}: {str(e)}")
            raise
