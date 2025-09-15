# src/core/services/employee_service.py
from typing import List, Optional, Dict, Any
import logging
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.present.request.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeWithDetails, Employee, 
    EmployeeDetailCreate, EmployeePaginationResponse, EmployeeFilterRequest
)
from src.common.exception.exceptions import (
    ValidationException, ConflictException, NotFoundException, InternalServerException
)
from src.repository.employee_repository import EmployeeRepository, EmployeeRelatedBulkOperations
from src.core.models.employee import Employee as EmployeeModel

logger = logging.getLogger(__name__)


class EmployeeService:
    """Employee service with business logic for Employee operations"""
    
    def __init__(self, employee_repository: EmployeeRepository, db_session: Session):
        self.employee_repository = employee_repository
        self.db_session = db_session
        self.bulk_operations = EmployeeRelatedBulkOperations(db_session)

    def create_employee(self, employee_create: EmployeeCreate) -> Employee:
        """Create a new Employee (basic info only)"""
        logger.info(f"Starting Employee creation process for: {employee_create.email}")
        
        try:
            # Check for email duplicate
            if self.employee_repository.email_exists(employee_create.email):
                logger.warning(f"Employee creation failed: Email '{employee_create.email}' already exists")
                raise ConflictException(
                    f"Email '{employee_create.email}' already exists in the system. Please use a different email address.",
                    "DUPLICATE_EMAIL"
                )
            
            # Check for employee_id duplicate
            if self.employee_repository.employee_id_exists(employee_create.employee_id):
                logger.warning(f"Employee creation failed: Employee ID '{employee_create.employee_id}' already exists")
                raise ConflictException(
                    f"Employee ID '{employee_create.employee_id}' already exists in the system. Please use a different Employee ID.",
                    "DUPLICATE_EMPLOYEE_ID"
                )
            
            # Check for phone duplicate if provided
            if employee_create.phone and self.employee_repository.phone_exists(employee_create.phone):
                logger.warning(f"Employee creation failed: Phone '{employee_create.phone}' already exists")
                raise ConflictException(
                    f"Phone number '{employee_create.phone}' already exists in the system. Please use a different phone number.",
                    "DUPLICATE_PHONE"
                )
            
            # Prepare Employee data
            employee_data = {
                "employee_id": employee_create.employee_id,  # Business ID
                "email": employee_create.email,
                "full_name": employee_create.full_name,
                "phone": employee_create.phone,
                "gender": employee_create.gender.value if employee_create.gender else None,
                "date_of_birth": employee_create.date_of_birth,
                "marital_status": employee_create.marital_status.value if employee_create.marital_status else None,
                "join_date": employee_create.join_date,
                "current_position": employee_create.current_position,
                "permanent_address": employee_create.permanent_address,
                "current_address": employee_create.current_address,
                "status": employee_create.status.value if employee_create.status else None
            }
            
            # Create Employee using repository
            employee = self.employee_repository.create_employee(employee_data)
            logger.info(f"Employee created successfully: {employee.id} ({employee.employee_id}) for {employee.email}")
            
            return Employee.model_validate(employee)
            
        except ValidationException:
            raise
        except ConflictException:
            raise
        except IntegrityError as e:
            logger.error(f"Database integrity error during Employee creation: {str(e)}")
            error_str = str(e).lower()
            
            if 'email' in error_str and 'unique' in error_str:
                raise ConflictException(
                    f"Email '{employee_create.email}' already exists in the system.",
                    "DUPLICATE_EMAIL"
                )
            elif 'employee_id' in error_str and 'unique' in error_str:
                raise ConflictException(
                    f"Employee ID '{employee_create.employee_id}' already exists in the system.",
                    "DUPLICATE_EMPLOYEE_ID"
                )
            elif 'phone' in error_str and 'unique' in error_str:
                raise ConflictException(
                    f"Phone number '{employee_create.phone}' already exists in the system.",
                    "DUPLICATE_PHONE"
                )
            else:
                raise ConflictException(
                    f"Data conflict: {str(e)[:100]}...",
                    "DATABASE_CONSTRAINT_ERROR"
                )
        except Exception as e:
            logger.error(f"Unexpected error during Employee creation: {str(e)}")
            raise InternalServerException(
                f"Employee creation failed due to server error: {str(e)}",
                "EMPLOYEE_CREATION_ERROR"
            )

    def create_employee_detail(self, employee_detail_create: EmployeeDetailCreate) -> EmployeeWithDetails:
        """Create a new Employee with all related data"""
        logger.info(f"Starting Employee detail creation process for: {employee_detail_create.email}")
        
        try:
            # First create the basic employee
            employee_create = EmployeeCreate(
                employee_id=employee_detail_create.employee_id,
                full_name=employee_detail_create.full_name,
                email=employee_detail_create.email,
                phone=employee_detail_create.phone,
                gender=employee_detail_create.gender,
                date_of_birth=employee_detail_create.date_of_birth,
                marital_status=employee_detail_create.marital_status,
                join_date=employee_detail_create.join_date,
                current_position=employee_detail_create.current_position,
                permanent_address=employee_detail_create.permanent_address,
                current_address=employee_detail_create.current_address,
                status=employee_detail_create.status
            )
            
            employee = self.create_employee(employee_create)
            employee_tech_id = employee.id
            
            # Create related components if provided
            if any([employee_detail_create.contacts, employee_detail_create.documents, 
                   employee_detail_create.languages, employee_detail_create.technical_skills, 
                   employee_detail_create.projects]):
                try:
                    self._create_employee_components(employee_tech_id, employee_detail_create)
                    logger.info(f"Employee components created for Employee: {employee_tech_id}")
                except Exception as comp_error:
                    logger.error(f"Failed to create Employee components for {employee_tech_id}: {str(comp_error)}")
                    # Rollback Employee creation if components fail
                    try:
                        self.employee_repository.delete_employee(employee_tech_id)
                        logger.info(f"Rolled back Employee {employee_tech_id} due to component creation failure")
                    except:
                        pass
                    raise ValidationException(f"Employee components creation failed: {str(comp_error)}", "EMPLOYEE_COMPONENTS_ERROR")
            
            # Return the employee with all details
            return self.get_employee_with_details(employee_tech_id)
            
        except ValidationException:
            raise
        except ConflictException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Employee detail creation: {str(e)}")
            raise InternalServerException(
                f"Employee detail creation failed due to server error: {str(e)}",
                "EMPLOYEE_DETAIL_CREATION_ERROR"
            )

    def get_employee(self, employee_tech_id: int) -> Employee:
        """Get an Employee by technical ID"""
        logger.info(f"Getting Employee: {employee_tech_id}")
        
        employee = self.employee_repository.get_employee_by_id(employee_tech_id)
        if not employee:
            logger.warning(f"Employee with ID {employee_tech_id} not found")
            raise NotFoundException(f"Employee with ID '{employee_tech_id}' not found", "EMPLOYEE_NOT_FOUND")
        
        return Employee.model_validate(employee)

    def get_employee_with_details(self, employee_tech_id: int) -> EmployeeWithDetails:
        """Get Employee with all related components"""
        logger.info(f"Getting Employee with details: {employee_tech_id}")
        
        # Get Employee
        employee = self.employee_repository.get_employee_by_id(employee_tech_id)
        if not employee:
            logger.warning(f"Employee with ID {employee_tech_id} not found")
            raise NotFoundException(f"Employee with ID '{employee_tech_id}' not found", "EMPLOYEE_NOT_FOUND")
        
        # Get all components
        components = self.bulk_operations.get_all_employee_components(employee_tech_id)
        
        # Convert to response model
        employee_dict = Employee.model_validate(employee).model_dump()
        employee_dict.update({
            'contacts': [contact.__dict__ for contact in components['contacts']],
            'documents': [doc.__dict__ for doc in components['documents']],
            'languages': [lang.__dict__ for lang in components['languages']],
            'technical_skills': [skill.__dict__ for skill in components['technical_skills']],
            'projects': [proj.__dict__ for proj in components['projects']]
        })
        
        return EmployeeWithDetails(**employee_dict)

    def get_employees(self, page: int = 1, page_size: int = 10) -> EmployeePaginationResponse:
        """Get Employees with pagination and full details"""
        logger.info(f"Getting Employees with details: page={page}, page_size={page_size}")
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get Employees and total count
        employees = self.employee_repository.get_all_employees(skip, page_size)
        total = self.employee_repository.count_total_employees()
        
        # Convert each employee to EmployeeWithDetails by loading components
        employees_with_details = []
        for employee in employees:
            # Get all components for this employee
            components = self.bulk_operations.get_all_employee_components(employee.id)
            
            # Convert to EmployeeWithDetails
            employee_dict = Employee.model_validate(employee).model_dump()
            employee_dict.update({
                'contacts': [contact.__dict__ for contact in components['contacts']],
                'documents': [doc.__dict__ for doc in components['documents']],
                'languages': [lang.__dict__ for lang in components['languages']],
                'technical_skills': [skill.__dict__ for skill in components['technical_skills']],
                'projects': [proj.__dict__ for proj in components['projects']]
            })
            
            employees_with_details.append(EmployeeWithDetails(**employee_dict))
        
        return EmployeePaginationResponse(
            employees=employees_with_details,
            total=total,
            page=page,
            page_size=page_size,
        )

    def filter_employees_with_details(self, filter_request: EmployeeFilterRequest) -> EmployeePaginationResponse:
        """Filter employees with advanced criteria and return with full details"""
        logger.info(f"Filtering employees with criteria: {filter_request.model_dump()}")
        
        try:
            # Convert request to filter dict
            filters = filter_request.model_dump(exclude_unset=True, exclude={'page', 'page_size'})
            
            # Add pagination info back
            filters['sort_by'] = filter_request.sort_by
            filters['sort_order'] = filter_request.sort_order
            
            # Calculate skip
            skip = (filter_request.page - 1) * filter_request.page_size
            
            # Get filtered employees
            employees = self.employee_repository.filter_employees_with_details(
                filters, skip, filter_request.page_size
            )
            
            # Get total count of filtered results
            total = self.employee_repository.count_filtered_employees(filters)
            
            # Convert each employee to EmployeeWithDetails by loading components
            employees_with_details = []
            for employee in employees:
                # Get all components for this employee
                components = self.bulk_operations.get_all_employee_components(employee.id)
                
                # Convert to EmployeeWithDetails
                employee_dict = Employee.model_validate(employee).model_dump()
                employee_dict.update({
                    'contacts': [contact.__dict__ for contact in components['contacts']],
                    'documents': [doc.__dict__ for doc in components['documents']],
                    'languages': [lang.__dict__ for lang in components['languages']],
                    'technical_skills': [skill.__dict__ for skill in components['technical_skills']],
                    'projects': [proj.__dict__ for proj in components['projects']]
                })
                
                employees_with_details.append(EmployeeWithDetails(**employee_dict))
            
            logger.info(f"Filter found {len(employees_with_details)} employees (total: {total})")
            
            return EmployeePaginationResponse(
                employees=employees_with_details,
                total=total,
                page=filter_request.page,
                page_size=filter_request.page_size,
            )
            
        except Exception as e:
            logger.error(f"Error filtering employees: {str(e)}")
            raise InternalServerException(
                f"Employee filtering failed: {str(e)}",
                "EMPLOYEE_FILTER_ERROR"
            )

    def _create_employee_components(self, employee_tech_id: int, employee_detail_create: EmployeeDetailCreate) -> None:
        """Create Employee related components"""
        try:
            components_data = {}
            
            if employee_detail_create.contacts:
                components_data['contacts'] = [contact.model_dump() for contact in employee_detail_create.contacts]
            
            if employee_detail_create.documents:
                components_data['documents'] = [doc.model_dump() for doc in employee_detail_create.documents]
            
            if employee_detail_create.languages:
                components_data['languages'] = [
                    {**lang.model_dump(), 'proficiency': lang.proficiency.value}
                    for lang in employee_detail_create.languages
                ]
            
            if employee_detail_create.technical_skills:
                components_data['technical_skills'] = [
                    {**skill.model_dump(), 'category': skill.category.value}
                    for skill in employee_detail_create.technical_skills
                ]
            
            if employee_detail_create.projects:
                components_data['projects'] = [proj.model_dump() for proj in employee_detail_create.projects]
            
            self.bulk_operations.bulk_create_employee_components(employee_tech_id, components_data)
            
        except Exception as e:
            logger.error(f"Failed to create Employee components for {employee_tech_id}: {str(e)}")
            raise
