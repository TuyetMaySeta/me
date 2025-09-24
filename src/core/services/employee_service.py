import logging
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError

from src.common.exception.exceptions import (
    ConflictException,
    InternalServerException,
    NotFoundException,
    ValidationException,
)
from src.core.utils.password_utils import hash_password
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

logger = logging.getLogger(__name__)


class EmployeeService:
    """Employee service with business logic for Employee operations"""

    def __init__(self, employee_repository: EmployeeRepository):
        self.employee_repository = employee_repository

    def create_employee(self, employee_create: CreateEmployeeDTO) -> Employee:
        """Create a new Employee (basic info only)"""
        logger.info(f"Starting Employee creation process for: {employee_create.email}")

        try:
            # Check for email duplicate
            if self.employee_repository.email_exists(employee_create.email):
                logger.warning(
                    f"Employee creation failed: Email '{employee_create.email}' already exists"
                )
                raise ConflictException(
                    f"Email '{employee_create.email}' already exists in the system.",
                    "DUPLICATE_EMAIL",
                )

            # Check for phone duplicate if provided
            if employee_create.phone and self.employee_repository.phone_exists(
                employee_create.phone
            ):
                logger.warning(
                    f"Employee creation failed: Phone '{employee_create.phone}' already exists"
                )
                raise ConflictException(
                    f"Phone number '{employee_create.phone}' already exists in the system.",
                    "DUPLICATE_PHONE",
                )

            # Map DTO to SQLAlchemy model including related entities
            employee_model = map_create_employee_dto_to_model(employee_create)
            employee_model.hashed_password = hash_password(
                employee_create.password
            )  # Hash password at creation

            # Create Employee using repository (handles model instance)
            employee = self.employee_repository.create_employee(employee_model)
            logger.info(
                f"Employee created successfully: {employee.id} for {employee.email}"
            )

            return Employee(employee)

        except ValidationException:
            raise
        except ConflictException:
            raise
        except IntegrityError as e:
            logger.error(f"Database integrity error during Employee creation: {str(e)}")
            error_str = str(e).lower()

            if "email" in error_str and "unique" in error_str:
                raise ConflictException(
                    f"Email '{employee_create.email}' already exists in the system.",
                    "DUPLICATE_EMAIL",
                )
            elif "phone" in error_str and "unique" in error_str:
                raise ConflictException(
                    f"Phone number '{employee_create.phone}' already exists.",
                    "DUPLICATE_PHONE",
                )
            else:
                raise ConflictException(
                    f"Data conflict: {str(e)[:100]}...", "DATABASE_CONSTRAINT_ERROR"
                )
        except Exception as e:
            logger.error(f"Unexpected error during Employee creation: {str(e)}")
            raise InternalServerException(
                f"Employee creation failed due to server error: {str(e)}",
                "EMPLOYEE_CREATION_ERROR",
            )

    def get_employee(self, employee_tech_id: int) -> Employee:
        """Get base Employee by technical ID"""
        logger.info(f"Getting Employee: {employee_tech_id}")

        employee = self.employee_repository.get_employee_by_id(employee_tech_id)
        if not employee:
            logger.warning(f"Employee with ID {employee_tech_id} not found")
            raise NotFoundException(
                f"Employee with ID '{employee_tech_id}' not found", "EMPLOYEE_NOT_FOUND"
            )

        return Employee(employee)

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
            f"Getting Employees: page={page}, page_size={page_size}, sort_by={sort_by}, sort_direction={sort_direction}"
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
