from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.bootstrap.application_bootstrap import get_employee_controller

# FIX: Change this import line
from src.present.controllers.employee_controller import EmployeeController
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

router = APIRouter(prefix="/employees", tags=["Employee Management"])


# 1. POST routes (no conflicts)
@router.post("", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: CreateEmployeeDTO,
    controller: EmployeeController = Depends(get_employee_controller),
):
    """Create a new Employee (basic information only)"""
    return controller.create_employee(employee)


# 3. GET / route (no path parameters)
@router.get("", response_model=EmployeePaginationResponse)
def get_employees(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query(
        None,
        description="Field to sort by (id, full_name, email, phone, gender, date_of_birth, marital_status, join_date, current_position, permanent_address, current_address, status, created_at, updated_at, skill_category)",
    ),
    sort_direction: Optional[str] = Query(
        "asc", regex="^(asc|desc)$", description="Sort direction: asc or desc"
    ),
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
    controller: EmployeeController = Depends(get_employee_controller),
):
    """Get all Employees with pagination (includes full details)"""
    return controller.get_employees(
        page,
        page_size,
        sort_by,
        sort_direction,
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


@router.get("/{employee_id}", response_model=EmployeeWithDetails)
def get_employee(
    employee_id: int = Path(..., description="Employee technical ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller),
):
    """👤 Get Employee by technical ID with full related details"""
    return controller.get_employee(employee_id)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller),
):
    """Delete employee by ID"""
    try:
        controller.delete_employee(employee_id)
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        # Convert unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error")
