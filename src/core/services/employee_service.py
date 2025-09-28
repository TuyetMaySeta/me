import logging
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError

from src.common.exception.exceptions import (
    ConflictException,
    NotFoundException,
)
from src.present.dto.employee.create_employee_dto import CreateEmployeeDTO
from src.present.dto.employee.employee_response_dto import (
    EmployeePaginationDTO as EmployeePaginationResponse,
)
from src.present.dto.employee.employee_response_dto import (
    EmployeeResponseDTO as Employee,
)
from src.present.dto.employee.employee_response_dto import (
    EmployeeWithDetailsResponseDTO as EmployeeWithDetails,
)
from src.present.dto.employee.mapper import map_create_employee_dto_to_model
from src.repository.employee_repository import EmployeeRepository
from src.utils.password_utils import hash_password

logger = logging.getLogger(__name__)


class EmployeeService:
    """Employee service with business logic for Employee operations"""

    def __init__(self, employee_repository: EmployeeRepository):
        self.employee_repository = employee_repository

    def create_employee(self, createEmployee_dto: CreateEmployeeDTO) -> Employee:
        # Check for email duplicate
        if self.employee_repository.email_exists(createEmployee_dto.email):
            logger.warning(
                (
                    f"Employee creation failed: "
                    f"Email '{createEmployee_dto.email}' already exists"
                )
            )
            raise ConflictException(
                f"Email '{createEmployee_dto.email}' already exists in the system.",
                "DUPLICATE_EMAIL",
            )

        # Check for phone duplicate if provided
        if createEmployee_dto.phone and self.employee_repository.phone_exists(
            createEmployee_dto.phone
        ):
            logger.warning(
                (
                    f"Employee creation failed: "
                    f"Phone '{createEmployee_dto.phone}' already exists"
                )
            )
            raise ConflictException(
                f"Phone number '{createEmployee_dto.phone}' "
                f"already exists in the system.",
                "DUPLICATE_PHONE",
            )

        # Map DTO to SQLAlchemy model including related entities
        employee_model = map_create_employee_dto_to_model(createEmployee_dto)
        employee_model.hashed_password = hash_password(createEmployee_dto.password)

        # Create Employee using repository (handles model instance)
        employee = self.employee_repository.create_employee(employee_model)
        return employee

    def get_employee(self, employee_tech_id: int) -> Employee:
        """Get base Employee by technical ID"""
        logger.info(f"Getting Employee: {employee_tech_id}")

        employee = self.employee_repository.get_employee_by_id(employee_tech_id)
        if not employee:
            logger.warning(f"Employee with ID {employee_tech_id} not found")
            raise NotFoundException(
                f"Employee with ID '{employee_tech_id}' not found", "EMPLOYEE_NOT_FOUND"
            )

        return employee

    def get_employee_with_details(self, employee_tech_id: int) -> EmployeeWithDetails:
        """Get Employee with all related components"""
        logger.info(f"Getting Employee with details: {employee_tech_id}")

        # Get Employee
        employee = self.employee_repository.get_employee_by_id(employee_tech_id)
        if not employee:
            logger.warning(f"Employee with ID {employee_tech_id} not found")
            raise NotFoundException(
                f"Employee with ID '{employee_tech_id}' not found", "EMPLOYEE_NOT_FOUND"
            )

        return employee

    def get_employees(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: Optional[str] = None,
        sort_direction: str = "asc",
        filters: Optional[Dict[str, Any]] = None,
    ) -> EmployeePaginationResponse:
        """Get Employees with pagination (basic info + skills table) and sorting"""
        logger.info(
            (
                f"Getting Employees: page={page}, page_size={page_size}, "
                f"sort_by={sort_by}, sort_direction={sort_direction}"
            )
        )

        # Calculate skip
        skip = (page - 1) * page_size

        employees = self.employee_repository.get_all_employees(
            skip, page_size, sort_by, sort_direction, filters
        )

        # Get Employees and total count
        total = self.employee_repository.count_total_employees(filters)

        # Map to DTOs (base fields only)
        employee_items = [Employee.model_validate(emp) for emp in employees]

        return EmployeePaginationResponse(
            employees=employee_items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def delete_employee(self, employee_id: int) -> None:
        """Delete employee and all related data"""
        try:
            employee = self.employee_repository.get_employee_by_id(employee_id)
            if not employee:
                raise NotFoundException(
                    f"Employee with ID '{employee_id}' not found", "EMPLOYEE_NOT_FOUND"
                )

            # Soft delete hoặc hard delete
            self.employee_repository.delete_employee(employee_id)
            logger.info(f"Service: Employee {employee_id} deleted")
        except Exception as e:
            logger.error(f"Service: Delete failed for employee {employee_id}: {str(e)}")
            raise
