# src/repository/employee_repository.py (update existing file)
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func

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
        self.db_session = db  # Add this line to fix the error

    def create_employee(self, employee_model: Employee) -> Employee:
        """Create a new employee from model instance"""
        try:
            self.db.add(employee_model)
            self.db.commit()
            self.db.refresh(employee_model)
            logger.info(f"Successfully created employee: {employee_model.id}")
            return employee_model
        except SQLAlchemyError as e:
            self.db.rollback()
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
            if employee:
                logger.debug(f"Found employee by email: {email}")
            else:
                logger.debug(f"Employee not found by email: {email}")
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

    def get_all_employees(self, 
                         skip: int = 0, 
                         limit: int = 100,
                         sort_by: Optional[str] = None,
                         sort_direction: str = "asc",
                         filters: Optional[Dict[str, Any]] = None) -> List[Employee]:
        """Get all employees with pagination and filtering"""
        try:
            query = self.db.query(Employee)
            
            # Apply filters if provided
            if filters:
                if filters.get('email'):
                    query = query.filter(Employee.email.ilike(f"%{filters['email']}%"))
                if filters.get('full_name'):
                    query = query.filter(Employee.full_name.ilike(f"%{filters['full_name']}%"))
                if filters.get('phone'):
                    query = query.filter(Employee.phone.ilike(f"%{filters['phone']}%"))
                if filters.get('current_position'):
                    query = query.filter(Employee.current_position.ilike(f"%{filters['current_position']}%"))
                if filters.get('gender'):
                    query = query.filter(Employee.gender == filters['gender'])
                if filters.get('status'):
                    query = query.filter(Employee.status == filters['status'])
                if filters.get('marital_status'):
                    query = query.filter(Employee.marital_status == filters['marital_status'])
                if filters.get('join_date_from'):
                    query = query.filter(Employee.join_date >= filters['join_date_from'])
                if filters.get('join_date_to'):
                    query = query.filter(Employee.join_date <= filters['join_date_to'])
            
            # Apply sorting
            if sort_by and hasattr(Employee, sort_by):
                sort_column = getattr(Employee, sort_by)
                if sort_direction.lower() == 'desc':
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(Employee.created_at.desc())
            
            employees = query.offset(skip).limit(limit).all()
            logger.debug(f"Retrieved {len(employees)} employees (skip={skip}, limit={limit})")
            return employees
        except SQLAlchemyError as e:
            logger.error(f"Error getting employees: {str(e)}")
            raise

    def count_total_employees(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count total employees with optional filters"""
        try:
            query = self.db.query(Employee)
            
            # Apply same filters as get_all_employees
            if filters:
                if filters.get('email'):
                    query = query.filter(Employee.email.ilike(f"%{filters['email']}%"))
                if filters.get('full_name'):
                    query = query.filter(Employee.full_name.ilike(f"%{filters['full_name']}%"))
                if filters.get('phone'):
                    query = query.filter(Employee.phone.ilike(f"%{filters['phone']}%"))
                if filters.get('current_position'):
                    query = query.filter(Employee.current_position.ilike(f"%{filters['current_position']}%"))
                if filters.get('gender'):
                    query = query.filter(Employee.gender == filters['gender'])
                if filters.get('status'):
                    query = query.filter(Employee.status == filters['status'])
                if filters.get('marital_status'):
                    query = query.filter(Employee.marital_status == filters['marital_status'])
                if filters.get('join_date_from'):
                    query = query.filter(Employee.join_date >= filters['join_date_from'])
                if filters.get('join_date_to'):
                    query = query.filter(Employee.join_date <= filters['join_date_to'])
            
            count = query.count()
            logger.debug(f"Total employees count: {count}")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Error counting employees: {str(e)}")
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

