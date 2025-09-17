import logging
from typing import List, Dict, Any
from src.core.models.employee import Employee as EmployeeModel
from src.present.dto.employee.create_employee_dto import CreateEmployeeDTO
from src.core.services.employee_service import EmployeeService
from src.present.dto.employee.employee_response_dto import (
    EmployeeResponseDTO as Employee,
    EmployeeWithDetailsResponseDTO as EmployeeWithDetails,
    EmployeePaginationDTO as EmployeePaginationResponse,
)

logger = logging.getLogger(__name__)


class EmployeeController:
    """Employee controller - handles HTTP requests for Employee operations"""
    
    def __init__(self, employee_service: EmployeeService):
        self.employee_service = employee_service
    
    def create_employee(self, employee_create: CreateEmployeeDTO) -> Employee:
        """Create a new Employee (basic info only)"""
        logger.info(f"Controller: Creating Employee for {employee_create.email}")
        
        try:
            employee = self.employee_service.create_employee(employee_create)
            logger.info(f"Controller: Employee created successfully - {employee.email} (ID: {employee.id})")
            return employee
        except Exception as e:
            logger.error(f"Controller: Employee creation failed for {employee_create.email}: {str(e)}")
            raise

    def get_employee(self, employee_id: int) -> EmployeeWithDetails:
        """Get Employee by ID with full related details"""
        logger.info(f"Controller: Getting Employee {employee_id}")
        
        try:
            employee = self.employee_service.get_employee_with_details(employee_id)
            logger.info(f"Controller: Retrieved Employee {employee_id}")
            return employee
        except Exception as e:
            logger.error(f"Controller: Failed to get Employee {employee_id}: {str(e)}")
            raise

    def get_employees(self, page: int = 1, page_size: int = 10) -> EmployeePaginationResponse:
        """Get all Employees with pagination (base fields only)"""
        logger.info(f"Controller: Getting Employees - page={page}, page_size={page_size}")
        
        try:
            result = self.employee_service.get_employees(page, page_size)
            logger.info(f"Controller: Retrieved {len(result.employees)} Employees (page {page})")
            return result
        except Exception as e:
            logger.error(f"Controller: Failed to get Employees: {str(e)}")
            raise
