# src/present/controllers/employee_controller.py
import logging
from typing import List, Dict, Any

from src.core.services.employee_service import EmployeeService
from src.present.request.employee import (
    EmployeeCreate, EmployeeUpdate, Employee, EmployeeWithDetails,
    EmployeeBulkCreate, EmployeeBulkResponse, EmployeeSearchRequest, 
    EmployeePaginationResponse, EmployeeDetailCreate, EmployeeBulkDetailCreate,
    EmployeeBulkDetailResponse
)

logger = logging.getLogger(__name__)


class EmployeeController:
    """Employee controller - handles HTTP requests for Employee operations"""
    
    def __init__(self, employee_service: EmployeeService):
        self.employee_service = employee_service
    
    def create_employee(self, employee_create: EmployeeCreate) -> Employee:
        """Create a new Employee (basic info only)"""
        logger.info(f"Controller: Creating Employee for {employee_create.email}")
        
        try:
            employee = self.employee_service.create_employee(employee_create)
            logger.info(f"Controller: Employee created successfully - {employee.email} (ID: {employee.id})")
            return employee
        except Exception as e:
            logger.error(f"Controller: Employee creation failed for {employee_create.email}: {str(e)}")
            raise

    def create_employee_detail(self, employee_detail_create: EmployeeDetailCreate) -> EmployeeWithDetails:
        """Create a new Employee with all related data"""
        logger.info(f"Controller: Creating Employee detail for {employee_detail_create.email}")
        
        try:
            employee = self.employee_service.create_employee_detail(employee_detail_create)
            logger.info(f"Controller: Employee detail created successfully - {employee.email} (ID: {employee.id})")
            return employee
        except Exception as e:
            logger.error(f"Controller: Employee detail creation failed for {employee_detail_create.email}: {str(e)}")
            raise

    def get_employee(self, employee_id: int) -> Employee:
        """Get Employee by ID (basic info only)"""
        logger.info(f"Controller: Getting Employee {employee_id}")
        
        try:
            employee = self.employee_service.get_employee(employee_id)
            logger.info(f"Controller: Retrieved Employee {employee_id}")
            return employee
        except Exception as e:
            logger.error(f"Controller: Failed to get Employee {employee_id}: {str(e)}")
            raise

    def get_employee_with_details(self, employee_id: int) -> EmployeeWithDetails:
        """Get Employee with all related components"""
        logger.info(f"Controller: Getting Employee with details {employee_id}")
        
        try:
            employee_details = self.employee_service.get_employee_with_details(employee_id)
            logger.info(f"Controller: Retrieved Employee details {employee_id}")
            return employee_details
        except Exception as e:
            logger.error(f"Controller: Failed to get Employee details {employee_id}: {str(e)}")
            raise

    def get_employees(self, page: int = 1, page_size: int = 10) -> EmployeePaginationResponse:
        """Get all Employees with pagination and full details"""
        logger.info(f"Controller: Getting Employees - page={page}, page_size={page_size}")
        
        try:
            result = self.employee_service.get_employees(page, page_size)
            logger.info(f"Controller: Retrieved {len(result.employees)} Employees (page {page})")
            return result
        except Exception as e:
            logger.error(f"Controller: Failed to get Employees: {str(e)}")
            raise

    def update_employee(self, employee_id: int, employee_update: EmployeeUpdate) -> Employee:
        """Update Employee"""
        logger.info(f"Controller: Updating Employee {employee_id}")
        
        try:
            employee = self.employee_service.update_employee(employee_id, employee_update)
            logger.info(f"Controller: Employee updated successfully {employee_id}")
            return employee
        except Exception as e:
            logger.error(f"Controller: Failed to update Employee {employee_id}: {str(e)}")
            raise

    def delete_employee(self, employee_id: int) -> Dict[str, str]:
        """Delete Employee"""
        logger.info(f"Controller: Deleting Employee {employee_id}")
        
        try:
            self.employee_service.delete_employee(employee_id)
            logger.info(f"Controller: Employee deleted successfully {employee_id}")
            return {"message": f"Employee {employee_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete Employee {employee_id}: {str(e)}")
            raise

    def search_employees(self, search_request: EmployeeSearchRequest) -> EmployeePaginationResponse:
        """Search Employees"""
        logger.info(f"Controller: Searching Employees with criteria: {search_request.model_dump()}")
        
        try:
            result = self.employee_service.search_employees(search_request)
            logger.info(f"Controller: Search found {len(result.employees)} Employees")
            return result
        except Exception as e:
            logger.error(f"Controller: Search failed: {str(e)}")
            raise

    def bulk_create_employees(self, bulk_request: EmployeeBulkCreate) -> EmployeeBulkResponse:
        """Bulk create Employees (basic info only)"""
        logger.info(f"Controller: Bulk creating {len(bulk_request.employees)} Employees")
        
        try:
            result = self.employee_service.bulk_create_employees(bulk_request)
            logger.info(f"Controller: Bulk creation completed - {result.created_count} success, {len(result.errors or [])} errors")
            return result
        except Exception as e:
            logger.error(f"Controller: Bulk creation failed: {str(e)}")
            raise

    def bulk_create_employees_detail(self, bulk_request: EmployeeBulkDetailCreate) -> EmployeeBulkDetailResponse:
        """Bulk create Employees with all details"""
        logger.info(f"Controller: Bulk creating {len(bulk_request.employees)} Employee details")
        
        try:
            result = self.employee_service.bulk_create_employees_detail(bulk_request)
            logger.info(f"Controller: Bulk detail creation completed - {result.created_count} success, {len(result.errors or [])} errors")
            return result
        except Exception as e:
            logger.error(f"Controller: Bulk detail creation failed: {str(e)}")
            raise
