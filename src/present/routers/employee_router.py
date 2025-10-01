from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.bootstrap.application_bootstrap import get_employee_controller
from src.present.controllers.employee_controller import EmployeeController
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

org_router = APIRouter(prefix="/orgs/{org_id}/employees", tags=["Employee Management"])

controller: EmployeeController = get_employee_controller()


# 1. POST routes (no conflicts)
@org_router.post("", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(org_id: int, employee: CreateEmployeeDTO):
    return controller.create_employee(org_id, employee)


@org_router.get("", response_model=EmployeePaginationResponse)
def get_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(
        None,
        description=(
            "Field to sort by (id, full_name, email, phone, gender, date_of_birth, "
            "marital_status, join_date, current_position, permanent_address, "
            "current_address, status, created_at, updated_at, skill_category)"
        ),
    ),
    sort_direction: Optional[str] = Query(
        "asc", regex="^(asc|desc)$", description="Sort direction: asc or desc"
    ),
    id: Optional[int] = Query(None, description="Filter by id (partial match)"),
    full_name: Optional[str] = Query(
        None, description="Filter by full name (partial match)"
    ),
    email: Optional[str] = Query(None, description="Filter by email (partial match)"),
    phone: Optional[str] = Query(None, description="Filter by phone (partial match)"),
    current_position: Optional[str] = Query(
        None, description="Filter by current position (partial match)"
    ),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    status: Optional[str] = Query(None, description="Filter by  status"),
    marital_status: Optional[str] = Query(None, description="Filter by maritalstatus"),
    skill_name: Optional[str] = Query(
        None, description="Filter by skill name (partial match)"
    ),
    skill_category: Optional[str] = Query(None, description="Filter by skill category"),
    join_date_from: Optional[date] = Query(
        None, description="Filter by join date from (YYYY-MM-DD)"
    ),
    join_date_to: Optional[date] = Query(
        None, description="Filter by join date to (YYYY-MM-DD)"
    ),
):
    return controller.get_employees(
        page,
        page_size,
        sort_by,
        sort_direction,
        id,
        full_name,
        email,
        phone,
        current_position,
        gender,
        status,
        marital_status,
        skill_name,
        skill_category,
        join_date_from,
        join_date_to,
    )


@org_router.get("/{employee_id}", response_model=EmployeeWithDetails)
def get_employee(
    employee_id: int = Path(..., description="Employee technical ID", gt=0)
):
    return controller.get_employee(employee_id)


@org_router.put("/{employee_id}", response_model=dict)
def update_employee(
    employee_id: int,
    update_data: UpdateEmployeeDTO,
    controller: EmployeeController = Depends(get_employee_controller),
):
    return controller.update_employee(employee_id, update_data)


@org_router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int = Path(..., description="Employee ID", gt=0)):
    controller.delete_employee(employee_id)
