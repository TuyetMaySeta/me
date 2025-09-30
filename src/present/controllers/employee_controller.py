import logging
from datetime import date
from typing import Optional

from fastapi import HTTPException, status

from src.common.exception.exceptions import (
    ConflictException,
    InternalServerException,
    NotFoundException,
    ValidationException,
)
from src.core.services.employee_service import EmployeeService
from src.present.dto.employee.create_employee_dto import (
    CreateEmployeeDTO,
    UpdateEmployeeDTO,
)
from src.present.dto.employee.employee_response_dto import (
    EmployeePaginationDTO as EmployeePaginationResponse,
)
from src.present.dto.employee.employee_response_dto import (
    EmployeeResponseDTO as Employee,
)
from src.present.dto.employee.employee_response_dto import (
    EmployeeWithDetailsResponseDTO as EmployeeWithDetails,
)

logger = logging.getLogger(__name__)


class EmployeeController:
    """Employee controller - handles HTTP requests for Employee operations"""

    def __init__(self, employee_service: EmployeeService):
        self.employee_service = employee_service

    def create_employee(
        self, org_id: int, employee_create: CreateEmployeeDTO
    ) -> Employee:
        return self.employee_service.create_employee(org_id, employee_create)

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

    def get_employees(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: Optional[str] = None,
        sort_direction: str = "asc",
        id: Optional[str] = None,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        current_position: Optional[str] = None,
        gender: Optional[str] = None,
        status: Optional[str] = None,
        marital_status: Optional[str] = None,
        skill_name: Optional[str] = None,
        skill_category: Optional[str] = None,
        join_date_from: Optional[date] = None,
        join_date_to: Optional[date] = None,
    ) -> EmployeePaginationResponse:
        """Get all Employees with pagination and sorting"""
        logger.info(
            (
                f"Controller: Getting Employees - page={page}, page_size={page_size}, "
                f"sort_by={sort_by}, sort_direction={sort_direction}"
            )
        )

        try:
            allowed_sort_fields = list(Employee.model_fields.keys())

            if sort_by and sort_by not in allowed_sort_fields:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        (
                            f"Invalid sort field '{sort_by}'. "
                            f"Allowed fields: {allowed_sort_fields}"
                        )
                    ),
                )

            # Validation enum filters
            if gender:
                from src.core.enums import GenderEnum

                try:
                    GenderEnum(gender)
                except ValueError:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid gender value: {gender}"
                    )

            if status:
                from src.core.enums import EmployeeStatusEnum

                try:
                    EmployeeStatusEnum(status)
                except ValueError:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid status value: {status}"
                    )

            if marital_status:
                from src.core.enums import MaritalStatusEnum

                try:
                    MaritalStatusEnum(marital_status)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid status value: {marital_status}",
                    )

            if skill_category:
                from src.core.enums import SkillCategoryEnum

                try:
                    SkillCategoryEnum(skill_category)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid skill category: {skill_category}",
                    )

            # Validate date range
            if join_date_from and join_date_to and join_date_from > join_date_to:
                raise HTTPException(
                    status_code=400,
                    detail="join_date_from cannot be greater than join_date_to",
                )

            filters = {
                "id": id,
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "current_position": current_position,
                "gender": gender,
                "status": status,
                "marital_status": marital_status,
                "skill_name": skill_name,
                "skill_category": skill_category,
                "join_date_from": join_date_from,
                "join_date_to": join_date_to,
            }
            result = self.employee_service.get_employees(
                page, page_size, sort_by, sort_direction, filters
            )

            logger.info(
                f"Controller: Retrieved {len(result.employees)} Employees (page {page})"
            )
            return result
        except Exception as e:
            logger.error(f"Controller: Failed to get Employees: {str(e)}")
            raise

    def update_employee(self, employee_id: int, update_data: UpdateEmployeeDTO):
        """Update employee by ID"""
        try:
            employee = self.employee_service.update_employee(employee_id, update_data)

            return {"message": "Employee updated successfully", "employee": employee}
        except NotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating employee: {str(e)}",
            )

    def delete_employee(self, employee_id: int) -> None:
        self.employee_service.delete_employee(employee_id)
