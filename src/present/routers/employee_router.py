# src/present/routers/employee_router.py
from fastapi import APIRouter, Depends, status, Query, Path
from typing import List, Dict

from src.present.request.employee import (
    EmployeeCreate, Employee, EmployeeWithDetails,
    EmployeeDetailCreate, EmployeePaginationResponse, EmployeeFilterRequest
)
from src.present.controllers.employee_controller import EmployeeController
from src.bootstrap.dependencies import get_employee_controller

router = APIRouter(prefix="/employees", tags=["Employee Management"])


# 1. POST routes first (no conflict)
@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate, 
    controller: EmployeeController = Depends(get_employee_controller)
):
    """Create a new Employee (basic information only)"""
    return controller.create_employee(employee)


@router.post("/detail", response_model=EmployeeWithDetails, status_code=status.HTTP_201_CREATED)
def create_employee_detail(
    employee_detail: EmployeeDetailCreate, 
    controller: EmployeeController = Depends(get_employee_controller)
):
    """Create a new Employee with all related information"""
    return controller.create_employee_detail(employee_detail)


# 2. CRITICAL: Put /filter route BEFORE any /{employee_id} routes
@router.post("/filter", response_model=EmployeePaginationResponse)
def filter_employees(
    filter_request: EmployeeFilterRequest,
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Advanced Employee Filter with Pagination
    
    **IMPORTANT: This route must be defined BEFORE /{employee_id} routes**
    """
    return controller.filter_employees(filter_request)


# 3. GET / route (no path parameters)
@router.get("/", response_model=EmployeePaginationResponse)
def get_employees(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    controller: EmployeeController = Depends(get_employee_controller),
):
    """Get all Employees with pagination"""
    return controller.get_employees(page, page_size)


# 4. Routes with path parameters MUST come LAST
@router.get("/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: int = Path(..., description="Employee technical ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """Get Employee by technical ID (basic information only)"""
    return controller.get_employee(employee_id)


@router.get("/{employee_id}/details", response_model=EmployeeWithDetails)
def get_employee_with_details(
    employee_id: int = Path(..., description="Employee technical ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """Get Employee with all related information"""
    return controller.get_employee_with_details(employee_id)
