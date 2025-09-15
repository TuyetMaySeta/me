# src/present/routers/employee_router.py
from fastapi import APIRouter, Depends, status, Query, Path
from typing import List, Dict

from src.present.request.employee import (
    EmployeeCreate, EmployeeUpdate, Employee, EmployeeWithDetails,
    EmployeeBulkCreate, EmployeeBulkResponse, EmployeeSearchRequest, 
    EmployeePaginationResponse, EmployeeSimplePaginationResponse, EmployeeComponentCreateRequest, EmployeeComponentsResponse
)
from src.present.controllers.employee_controller import EmployeeController
from src.bootstrap.dependencies import get_employee_controller

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate, 
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Create a new Employee
    
    - **email**: Valid email address (unique)
    - **full_name**: Full name (required, min 2 characters)
    - **employee_id**: Business Employee ID (unique, 3-50 characters)
    - **gender**: Optional gender (Male/Female/Other)
    - **current_position**: Optional current position
    - **summary**: Optional summary/bio
    - **languages**: Optional list of languages with proficiency
    - **technical_skills**: Optional list of technical skills
    - **soft_skills**: Optional list of soft skills
    - **projects**: Optional list of projects
    """
    return controller.create_employee(employee)


@router.get("/", response_model=EmployeePaginationResponse)
def get_employees(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    controller: EmployeeController = Depends(get_employee_controller),
):
    """
    Get all Employees with pagination
    
    - **page**: Page number (default: 1)
    - **page_size**: Records per page (default: 10, max: 100)
    """
    return controller.get_employees(page, page_size)


@router.get("/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get Employee by technical ID
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    """
    return controller.get_employee(employee_id)


@router.get("/by-employee-id/{employee_business_id}", response_model=Employee)
def get_employee_by_employee_id(
    employee_business_id: str = Path(..., description="Employee business ID", min_length=3, max_length=50),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get Employee by business employee_id
    
    - **employee_business_id**: Employee business identifier (3-50 characters)
    """
    return controller.get_employee_by_employee_id(employee_business_id)


@router.get("/{employee_id}/details", response_model=EmployeeWithDetails)
def get_employee_with_details(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get Employee with all related components (languages, skills, projects)
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    """
    return controller.get_employee_with_details(employee_id)


@router.put("/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    employee_update: EmployeeUpdate = ...,
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Update Employee by technical ID
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    - **employee_update**: Fields to update (all optional)
    """
    return controller.update_employee(employee_id, employee_update)


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Delete Employee and all related data
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    
    **Warning**: This will permanently delete the Employee and ALL related data (languages, skills, projects)
    """
    return controller.delete_employee(employee_id)


@router.post("/search", response_model=EmployeePaginationResponse)
def search_employees(
    search_request: EmployeeSearchRequest,
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Search Employees by various criteria
    
    - **email**: Search by email pattern (case-insensitive)
    - **position**: Search by position pattern (case-insensitive)
    - **employee_id**: Search by business employee_id pattern (case-insensitive)
    - **skill**: Search by skill name (case-insensitive)
    - **page**: Page number (default: 1)
    - **page_size**: Records per page (default: 10)
    """
    return controller.search_employees(search_request)


@router.post("/bulk", response_model=EmployeeBulkResponse)
def bulk_create_employees(
    bulk_request: EmployeeBulkCreate,
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Bulk create multiple Employees
    
    - **employees**: List of Employee creation requests
    
    **Note**: Partial success is possible - some Employees may be created while others fail
    """
    return controller.bulk_create_employees(bulk_request)


@router.post("/{employee_id}/components", response_model=EmployeeComponentsResponse)
def create_employee_components(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    request: EmployeeComponentCreateRequest = ...,
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Create components for existing Employee
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    - **request**: Components to create (languages, skills, projects)
    """
    # Override employee_id in request with path parameter
    request.employee_id = employee_id
    return controller.create_employee_components(request)


@router.get("/{employee_id}/components", response_model=EmployeeComponentsResponse)
def get_employee_components(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get all components for an Employee
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    """
    return controller.get_employee_components(employee_id)


# Additional utility endpoints
@router.get("/{employee_id}/summary")
def get_employee_summary(
    employee_id: str = Path(..., description="Employee technical ID (6 characters)", min_length=6, max_length=6),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get Employee summary statistics
    
    - **employee_id**: Employee technical identifier (exactly 6 characters)
    """
    components = controller.get_employee_components(employee_id)
    employee = controller.get_employee(employee_id)
    
    return {
        "employee_id": employee_id,
        "employee_business_id": employee.employee_id,
        "email": employee.email,
        "full_name": employee.full_name,
        "current_position": employee.current_position,
        "component_counts": {
            "languages": len(components.languages),
            "technical_skills": len(components.technical_skills),
            "soft_skills": len(components.soft_skills),
            "projects": len(components.projects)
        },
        "created_at": employee.created_at,
        "updated_at": employee.updated_at
    }