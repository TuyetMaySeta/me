import logging
from typing import Any, Dict, Optional

from sqlalchemy.exc import IntegrityError

import src.utils.password_utils as password_utils
from src.common.exception.exceptions import (
    ConflictException,
    NotFoundException,
)
from src.core.mapper.employee import EmployeeMapper
from src.core.models.organization import EmployeeOrganizationRole
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
from src.core.mapper.employee import EmployeeMapper
from src.repository.employee_repository import EmployeeRepository
from src.repository.role import RoleRepository
from src.utils.password_utils import hash_password
import src.utils.password_utils as password_utils
logger = logging.getLogger(__name__)


class EmployeeService:
    def __init__(
        self,
        employee_repository: EmployeeRepository,
        employee_mapper: EmployeeMapper,
        role_repository: RoleRepository,
    ):
        self.employee_repository = employee_repository
        self.employee_mapper = employee_mapper
        self.role_repository = role_repository

    def create_employee(self, createEmployee_dto: CreateEmployeeDTO) -> Employee:
        # Check for email and phone in employee table duplicate
        fields_to_check = {
            'email': createEmployee_dto.email,
            'phone': createEmployee_dto.phone,
        }
        
        if createEmployee_dto.documents:
            doc_dict = createEmployee_dto.documents.model_dump()
            fields_to_check.update({
                'identity_number': doc_dict.get('identity_number'),
                'old_identity_number': doc_dict.get('old_identity_number'),
                'tax_id_number': doc_dict.get('tax_id_number'),
                'social_insurance_number': doc_dict.get('social_insurance_number'),
                'account_bank_number': doc_dict.get('account_bank_number'),
                'motorbike_plate': doc_dict.get('motorbike_plate'),  

            })
        
        duplicate_field = self.employee_repository.check_field_exists(fields_to_check)
        
        if duplicate_field:
            field_labels = {
                'email': 'Email',
                'phone': 'Phone number',
                'identity_number': 'Identity number (CCCD)',
                'old_identity_number': 'Old identity number (CMND)',
                'tax_id_number': 'Tax ID (MST)',
                'social_insurance_number': 'Social insurance number (BHXH)',
                'account_bank_number': 'Bank account number',
                'motorbike_plate': 'Motorbike plate number',  

            }
            raise ConflictException(
                f"{field_labels[duplicate_field]} already exists",
                f"DUPLICATE_{duplicate_field.upper()}"
            )

        # Map DTO to SQLAlchemy model including related entities
        employee_model = EmployeeMapper.map_create_employee_dto_to_model(
            createEmployee_dto
        )
        employee_model.hashed_password = hash_password(
            password_utils.generate_random_password()
        )
        # Todo: Send email to employee with password

        org_role_default = self.role_repository.getOrgRoleDefault()
        employee = self.employee_repository.create_employee(employee_model)
        employee_organization_role = EmployeeOrganizationRole(
            employee_id=employee.id,
            organization_id=organization_id,
            role_id=org_role_default.id,
        )
        self.role_repository.create_employee_organization_role(
            employee_organization_role
        )
        return employee

    def get_employee_with_details(self, employee_tech_id: int) -> EmployeeWithDetails:
        employee = self.employee_repository.get_employee_by_id(employee_tech_id)
        if not employee:
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
        employee = self.employee_repository.get_employee_by_id(employee_id)
        if not employee:
            raise NotFoundException(
                f"Employee with ID '{employee_id}' not found", "EMPLOYEE_NOT_FOUND"
            )
        self.employee_repository.delete_employee(employee_id)
        self.role_repository.delete_employee(employee_id)

    def update_employee(self, employee_id: int, update_data: UpdateEmployeeDTO):
        """Update employee with full details"""
        update_dict = update_data.model_dump(exclude_none=True)

        if not update_dict:
            raise ValueError("No data to update")

        updated_employee = self.employee_repository.update_employee(
            employee_id, update_dict
        )

        if not updated_employee:
            raise NotFoundException(
                f"Employee with ID '{employee_id}' not found", "EMPLOYEE_NOT_FOUND"
            )

        return EmployeeWithDetails.model_validate(updated_employee)
