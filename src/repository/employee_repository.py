from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from ..core.models.employee import Employee

logger = logging.getLogger(__name__)


class EmployeeRepository(BaseRepository[Employee]):
    """
    Repository for Employee entity.
    Only handles pure CRUD operations (no validation or business rules).
    """

    def __init__(self, db: Session):
        """Initialize Employee repository with Employee model."""
        super().__init__(db, Employee)

    def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        try:
            employee = self.create(employee_data)
            logger.info(f"Successfully created Employee: {employee.id}")
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Failed to create Employee: {str(e)}")
            raise

    def get_employee_by_id(self, employee_tech_id: str) -> Optional[Employee]:
        """Get employee by technical ID (6-char)"""
        try:
            employee = self.db.query(Employee).filter(Employee.id == employee_tech_id).first()
            if employee:
                logger.debug(f"Found Employee: {employee_tech_id}")
            else:
                logger.debug(f"Employee not found: {employee_tech_id}")
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Error getting Employee {employee_tech_id}: {str(e)}")
            raise

    def get_employee_by_employee_id(self, employee_id: str) -> Optional[Employee]:
        """Get employee by business ID (employee_id)"""
        try:
            employee = self.db.query(Employee).filter(Employee.employee_id == employee_id).first()
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Error getting Employee by employee_id {employee_id}: {str(e)}")
            raise

    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        try:
            employee = self.db.query(Employee).filter(Employee.email == email).first()
            return employee
        except SQLAlchemyError as e:
            logger.error(f"Error getting Employee by email {email}: {str(e)}")
            raise

    def get_all_employees(self, skip: int = 0, limit: int = 100) -> List[Employee]:
        try:
            employees = (
                self.db.query(Employee)
                .offset(skip)
                .limit(limit)
                .all()
            )
            logger.debug(f"Retrieved {len(employees)} Employees (skip={skip}, limit={limit})")
            return employees
        except SQLAlchemyError as e:
            logger.error(f"Error getting Employees: {str(e)}")
            raise

    def update_employee(self, employee_tech_id: str, update_data: Dict[str, Any]) -> Optional[Employee]:
        """
        Update Employee by technical ID.
        """
        try:
            employee = self.get_employee_by_id(employee_tech_id)
            if not employee:
                return None

            # Update fields
            for field, value in update_data.items():
                if hasattr(employee, field) and value is not None:
                    setattr(employee, field, value)

            self.db.commit()
            self.db.refresh(employee)
            logger.info(f"Successfully updated Employee: {employee_tech_id}")
            return employee
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating Employee {employee_tech_id}: {str(e)}")
            raise

    def delete_employee(self, employee_tech_id: str) -> bool:
        try:
            employee = self.get_employee_by_id(employee_tech_id)
            if not employee:
                return False

            self.db.delete(employee)
            self.db.commit()
            logger.info(f"Successfully deleted Employee: {employee_tech_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting Employee {employee_tech_id}: {str(e)}")
            raise

    def count_total_employees(self) -> int:
        try:
            count = self.db.query(Employee).count()
            logger.debug(f"Total Employees count: {count}")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Error counting Employees: {str(e)}")
            raise

    def search_employees(self, 
                        email: Optional[str] = None,
                        position: Optional[str] = None,
                        employee_id: Optional[str] = None,
                        skip: int = 0,
                        limit: int = 100) -> List[Employee]:
        try:
            query = self.db.query(Employee)

            if email:
                query = query.filter(Employee.email.ilike(f"%{email}%"))

            if position:
                query = query.filter(Employee.current_position.ilike(f"%{position}%"))

            if employee_id:
                query = query.filter(Employee.employee_id.ilike(f"%{employee_id}%"))

            employees = query.offset(skip).limit(limit).all()
            logger.debug(f"Search found {len(employees)} Employees")
            return employees
        except SQLAlchemyError as e:
            logger.error(f"Error searching Employees: {str(e)}")
            raise

    def bulk_create_employees(self, employees_data: List[Dict[str, Any]]) -> List[Employee]:
        try:
            employees = []
            for employee_data in employees_data:
                employee = Employee(**employee_data)
                self.db.add(employee)
                employees.append(employee)

            self.db.commit()
            
            # Refresh all instances
            for employee in employees:
                self.db.refresh(employee)

            logger.info(f"Successfully bulk created {len(employees)} Employees")
            return employees
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error bulk creating Employees: {str(e)}")
            raise

    def employee_exists(self, employee_tech_id: str) -> bool:
        """
        Check if Employee exists by technical ID.
        """
        try:
            exists = self.db.query(Employee).filter(Employee.id == employee_tech_id).first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking Employee existence {employee_tech_id}: {str(e)}")
            raise

    def employee_id_exists(self, employee_id: str, exclude_tech_id: Optional[str] = None) -> bool:
        """Check if business employee_id exists"""
        try:
            query = self.db.query(Employee).filter(Employee.employee_id == employee_id)
            if exclude_tech_id:
                query = query.filter(Employee.id != exclude_tech_id)
            
            exists = query.first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking employee_id existence {employee_id}: {str(e)}")
            raise

    def email_exists(self, email: str, exclude_tech_id: Optional[str] = None) -> bool:
        try:
            query = self.db.query(Employee).filter(Employee.email == email)
            if exclude_tech_id:
                query = query.filter(Employee.id != exclude_tech_id)
            
            exists = query.first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking email existence {email}: {str(e)}")
            raise