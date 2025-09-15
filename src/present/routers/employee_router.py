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


@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate, 
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Create a new Employee (basic information only)
    
    - **employee_id**: Unique business employee ID (required)
    - **full_name**: Employee's full name (required, min 2 chars)
    - **email**: Valid email address (unique)
    - **phone**: Vietnamese phone number (10-11 digits starting with 0)
    - **gender**: Gender (Male/Female)
    - **date_of_birth**: Date of birth (must be 16-100 years old)
    - **marital_status**: Marital status (Single/Married/Divorced/Widowed)
    - **join_date**: Date employee joined the company (cannot be future)
    - **current_position**: Current job position
    - **permanent_address**: Permanent address
    - **current_address**: Current address
    - **status**: Employee status (Active/On Leave/Resigned)
    
    **Validation Rules:**
    - Phone: 10-11 digits, starts with 0, mobile must start with 03/05/07/08/09
    - Employee ID: 3-50 chars, alphanumeric with dash/underscore only
    - Age: Must be 16-100 years old
    - Join date: Cannot be in future or more than 50 years ago
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
    - Contacts (emergency contacts, family members)
    - Documents (CCCD, CMND, tax ID, bank account, etc.)
    - Languages (with proficiency levels)
    - Technical Skills (programming languages, tools, frameworks)
    - Projects (work experience and responsibilities)
    
    **Validation includes all basic employee validations plus:**
    - Contact phone: Vietnamese format validation
    - CCCD: Exactly 12 digits
    - CMND: Exactly 9 digits  
    - Tax ID: 10-13 digits
    - Social Insurance: 2 letters + 8 digits (e.g., HN12345678)
    - Bank Account: 6-30 digits
    - Motorbike Plate: Vietnamese format (e.g., 30A12345)
    """
    return controller.create_employee_detail(employee_detail)


@router.get("/", response_model=EmployeePaginationResponse)
def get_employees(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of records per page (max 100)"),
    controller: EmployeeController = Depends(get_employee_controller),
):
    """
    Get all Employees with pagination (includes all related data)
    
    - **page**: Page number (default: 1, minimum: 1)
    - **page_size**: Records per page (default: 10, max: 100)
    
    **Returns employees with all related information:**
    - Basic employee info (name, email, phone, position, etc.)
    - All contacts (emergency contacts, family)
    - All documents (CCCD, tax ID, bank info, etc.)
    - All languages with proficiency levels
    - All technical skills categorized
    - All projects with roles and technologies
    
    **Response includes:**
    - employees: List of EmployeeWithDetails
    - total: Total number of employees
    - page: Current page number
    - page_size: Number of items per page
    """
    return controller.get_employees(page, page_size)


@router.get("/{employee_id}", response_model=Employee)
def get_employee(
    employee_id: int = Path(..., description="Employee technical ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get Employee by technical ID (basic information only)
    
    - **employee_id**: Employee technical identifier (auto-generated integer)
    
    **Returns only basic employee information:**
    - Employee ID (business ID)
    - Full name, email, phone
    - Gender, date of birth, marital status
    - Join date, current position
    - Addresses and status
    - Created/updated timestamps
    
    **Note:** This endpoint returns basic info only. Use /employees/{id}/details for complete information.
    """
    return controller.get_employee(employee_id)


@router.get("/{employee_id}/details", response_model=EmployeeWithDetails)
def get_employee_with_details(
    employee_id: int = Path(..., description="Employee technical ID", gt=0),
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Get Employee with all related information
    
    - **employee_id**: Employee technical identifier (auto-generated integer)
    
    **Returns complete employee profile including:**
    
    **Basic Info:**
    - Employee ID, full name, email, phone
    - Gender, date of birth, marital status  
    - Join date, current position, addresses, status
    
    **Related Data:**
    - **Contacts**: Emergency contacts, family members with relationships
    - **Documents**: 
      - Identity documents (CCCD, old CMND)
      - Tax ID number
      - Social insurance number  
      - Bank account information
      - Motorbike license plate
    - **Languages**: Language skills with proficiency levels (Native/Fluent/Intermediate/Basic)
    - **Technical Skills**: Categorized by type (Programming Language/Database/Framework/Tool/Hardware)
    - **Projects**: Work experience with roles, responsibilities, and technologies used
    
    **Use Cases:**
    - Complete employee profile view
    - HR management and reviews
    - Skills assessment and project assignment
    - Contact information for emergencies
    """
    return controller.get_employee_with_details(employee_id)


@router.post("/filter", response_model=EmployeePaginationResponse)
def filter_employees(
    filter_request: EmployeeFilterRequest,
    controller: EmployeeController = Depends(get_employee_controller)
):
    """
    Advanced Employee Filter with Pagination (returns full details)
    
    **Comprehensive filtering system với pagination và full employee details**
    
    **Basic Filters:**
    - **email**: Filter by email (partial match)
    - **employee_id**: Filter by employee ID (partial match)  
    - **full_name**: Filter by full name (partial match)
    - **phone**: Filter by phone number (partial match)
    - **current_position**: Filter by position (partial match)
    
    **Status Filters:**
    - **gender**: Filter by gender (Male/Female)
    - **marital_status**: Filter by marital status
    - **status**: Filter by employee status (Active/On Leave/Resigned)
    
    **Date Range Filters:**
    - **join_date_from/to**: Filter by join date range
    - **date_of_birth_from/to**: Filter by birth date range
    - **min_age/max_age**: Filter by age range (16-100)
    
    **Related Data Filters:**
    - **has_contacts**: Filter employees with/without contacts
    - **has_documents**: Filter employees with/without documents
    - **has_languages**: Filter employees with/without language skills
    - **has_technical_skills**: Filter employees with/without technical skills
    - **has_projects**: Filter employees with/without project experience
    
    **Skill-Specific Filters:**
    - **language_name**: Filter by specific language (e.g., "English")
    - **technical_skill**: Filter by specific technical skill (e.g., "Python")
    - **skill_category**: Filter by skill category (Programming Language/Database/Framework/Tool/Hardware)
    
    **Sorting & Pagination:**
    - **sort_by**: Sort field (id, employee_id, full_name, email, join_date, created_at)
    - **sort_order**: Sort direction (asc/desc)
    - **page**: Page number (default: 1)
    - **page_size**: Records per page (max: 100)
    
    **Examples:**
    ```json
    {
      "current_position": "Developer",
      "has_technical_skills": true,
      "technical_skill": "Python",
      "min_age": 25,
      "max_age": 40,
      "sort_by": "join_date",
      "sort_order": "desc",
      "page": 1,
      "page_size": 20
    }
    ```
    
    **Returns:** Complete employee profiles với all related data (contacts, documents, skills, projects)
    """
    return controller.filter_employees(filter_request)
