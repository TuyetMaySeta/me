# src/present/routers/employee_router.py
from fastapi import APIRouter, Depends, status, Query, Path
from typing import List, Dict

from src.present.request.employee import (
    EmployeeCreate, EmployeeUpdate, Employee, EmployeeWithDetails,
    EmployeeBulkCreate, EmployeeBulkResponse, EmployeeSearchRequest, 
    EmployeePaginationResponse, EmployeeDetailCreate, EmployeeBulkDetailCreate,
    EmployeeBulkDetailResponse
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
    Create a new Employee (basic information only)
    
    - **full_name**: Employee's full name (required)
    - **email**: Valid email address (unique)
    - **phone**: Phone number (optional, unique if provided)
    - **gender**: Gender (Male/Female)
    - **date_of_birth**: Date of birth
    - **marital_status**: Marital status (Single/Married/Divorced/Widowed)
    - **join_date**: Date employee joined the company
    - **current_position**: Current job position
    - **permanent_address**: Permanent address
    - **current_address**: Current address
    - **status**: Employee status (Active/On Leave/Resigned)
    """
    return controller.create_employee(employee)


@router.post("/detail", response_model=EmployeeWithDetails, status_code=status.HTTP_201_CREATED)
def create_employee_detail(
    employee_detail: EmployeeDetailCreate, 
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Create a new Employee with all related information
    
    Creates an employee with basic info plus all related data:
    - Contacts, Documents, Education, Certifications
    - Profiles, Languages, Technical Skills, Projects, Children
    """
    return controller.create_employee_detail(employee_detail)


@router.get("/", response_model=EmployeePaginationResponse)
def get_employees(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page"),
    controller: EmployeeController = Depends(get_employee_controller),
):
    """
    Get all Employees with pagination (includes all related data)
    
    - **page**: Page number (default: 1)
    - **page_size**: Records per page (default: 10, max: 100)
    
    Returns employees with all related information (contacts, documents, etc.)
    """
    return controller.get_employees(page, page_size)


@router.get("/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get Employee by ID (basic information only)
    
    - **employee_id**: Employee identifier
    """
    return controller.get_employee(employee_id)


@router.get("/{employee_id}/details", response_model=EmployeeWithDetails)
def get_employee_with_details(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get Employee with all related information
    
    - **employee_id**: Employee identifier
    
    Returns employee with all related data (contacts, documents, education, etc.)
    """
    return controller.get_employee_with_details(employee_id)


@router.put("/{employee_id}", response_model=Employee)
def update_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    employee_update: EmployeeUpdate = ...,
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Update Employee by ID
    
    - **employee_id**: Employee identifier
    - **employee_update**: Fields to update (all optional)
    """
    return controller.update_employee(employee_id, employee_update)


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Delete Employee and all related data
    
    - **employee_id**: Employee identifier
    
    **Warning**: This will permanently delete the Employee and ALL related data
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
    - **status**: Filter by employee status
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
    Bulk create multiple Employees (basic information only)
    
    - **employees**: List of employee creation requests
    
    **Note**: Partial success is possible - some employees may be created while others fail
    """
    return controller.bulk_create_employees(bulk_request)


@router.post("/bulk-detail", response_model=EmployeeBulkDetailResponse)
def bulk_create_employees_detail(
    bulk_request: EmployeeBulkDetailCreate,
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Bulk create multiple Employees with all related information
    
    - **employees**: List of detailed employee creation requests
    
    **Note**: Partial success is possible - some employees may be created while others fail
    """
    return controller.bulk_create_employees_detail(bulk_request)


# Additional utility endpoints
@router.get("/{employee_id}/summary")
def get_employee_summary(
    employee_id: int = Path(..., description="Employee ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get Employee summary statistics
    
    - **employee_id**: Employee identifier
    """
    employee_details = controller.get_employee_with_details(employee_id)
    
    return {
        "employee_id": employee_id,
        "email": employee_details.email,
        "full_name": employee_details.full_name,
        "current_position": employee_details.current_position,
        "status": employee_details.status,
        "component_counts": {
            "contacts": len(employee_details.contacts),
            "documents": len(employee_details.documents),
            "education": len(employee_details.education),
            "certifications": len(employee_details.certifications),
            "profiles": len(employee_details.profiles),
            "languages": len(employee_details.languages),
            "technical_skills": len(employee_details.technical_skills),
            "projects": len(employee_details.projects),
            "children": len(employee_details.children)
        },
        "join_date": employee_details.join_date,
        "created_at": employee_details.created_at,
        "updated_at": employee_details.updated_at
    }


@router.get("/statistics/overview")
def get_employees_statistics(
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get overall employee statistics
    """
    # Get first page to calculate basic stats
    result = controller.get_employees(page=1, page_size=100)
    
    # Calculate statistics
    total_employees = result.total
    active_count = sum(1 for emp in result.employees if emp.status == "Active")
    on_leave_count = sum(1 for emp in result.employees if emp.status == "On Leave")
    resigned_count = sum(1 for emp in result.employees if emp.status == "Resigned")
    
    return {
        "total_employees": total_employees,
        "status_breakdown": {
            "active": active_count,
            "on_leave": on_leave_count,
            "resigned": resigned_count
        },
        "completion_stats": {
            "with_contacts": sum(1 for emp in result.employees if len(emp.contacts) > 0),
            "with_education": sum(1 for emp in result.employees if len(emp.education) > 0),
            "with_certifications": sum(1 for emp in result.employees if len(emp.certifications) > 0),
            "with_projects": sum(1 for emp in result.employees if len(emp.projects) > 0)
        }
    }
