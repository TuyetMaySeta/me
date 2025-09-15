# src/core/services/employee_service.py
from typing import List, Optional, Dict, Any
import logging
import random
import string
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.present.request.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeWithDetails, Employee, 
    EmployeeBulkCreate, EmployeeBulkResponse, EmployeeSearchRequest, 
    EmployeePaginationResponse, EmployeeComponentCreateRequest, EmployeeComponentsResponse
)
from src.common.exception.exceptions import (
    ValidationException, ConflictException, NotFoundException, InternalServerException
)
from src.repository.employee_repository import EmployeeRepository
from src.repository.employee_related_repository import EmployeeRelatedBulkOperations
from src.core.models.employee import Employee as EmployeeModel

logger = logging.getLogger(__name__)


class EmployeeService:
    """Employee service with business logic for Employee operations"""
    
    def __init__(self, employee_repository: EmployeeRepository, db_session: Session):
        self.employee_repository = employee_repository
        self.db_session = db_session
        self.bulk_operations = EmployeeRelatedBulkOperations(db_session)
    
    def _generate_employee_tech_id(self, length: int = 6) -> str:
        """Generate random Employee technical ID"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    def _ensure_unique_employee_tech_id(self) -> str:
        """Generate unique Employee technical ID"""
        tech_id = self._generate_employee_tech_id()
        while self.employee_repository.employee_exists(tech_id):
            tech_id = self._generate_employee_tech_id()
        return tech_id

    def create_employee(self, employee_create: EmployeeCreate) -> Employee:
        """Create a new Employee with optional related data"""
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
            
            # Generate unique technical ID
            tech_id = self._ensure_unique_employee_tech_id()
            
            # Prepare Employee data
            employee_data = {
                "id": tech_id,  # Technical ID (6-char)
                "employee_id": employee_create.employee_id,  # Business ID
                "email": employee_create.email,
                "full_name": employee_create.full_name,
                "gender": employee_create.gender.value if employee_create.gender else None,
                "current_position": employee_create.current_position,
                "summary": employee_create.summary
            }
            
            # Create Employee using repository
            employee = self.employee_repository.create_employee(employee_data)
            logger.info(f"Employee created successfully: {employee.id} for {employee.email}")
            
            # Create related components if provided
            if any([employee_create.languages, employee_create.technical_skills, 
                   employee_create.soft_skills, employee_create.projects]):
                try:
                    self._create_employee_components(tech_id, employee_create)
                    logger.info(f"Employee components created for Employee: {tech_id}")
                except Exception as comp_error:
                    logger.error(f"Failed to create Employee components for {tech_id}: {str(comp_error)}")
                    # Rollback Employee creation if components fail
                    try:
                        self.employee_repository.delete_employee(tech_id)
                        logger.info(f"Rolled back Employee {tech_id} due to component creation failure")
                    except:
                        pass
                    raise ValidationException(f"Employee components creation failed: {str(comp_error)}", "EMPLOYEE_COMPONENTS_ERROR")
            
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

    def get_employee(self, employee_tech_id: str) -> Employee:
        """Get an Employee by technical ID"""
        logger.info(f"Getting Employee: {employee_tech_id}")
        
        employee = self.employee_repository.get_employee_by_id(employee_tech_id)
        if not employee:
            logger.warning(f"Employee with ID {employee_tech_id} not found")
            raise NotFoundException(f"Employee with ID '{employee_tech_id}' not found", "EMPLOYEE_NOT_FOUND")
        
        return Employee.model_validate(employee)

    def get_employee_by_employee_id(self, employee_id: str) -> Employee:
        """Get an Employee by business employee_id"""
        logger.info(f"Getting Employee by employee_id: {employee_id}")
        
        employee = self.employee_repository.get_employee_by_employee_id(employee_id)
        if not employee:
            logger.warning(f"Employee with employee_id {employee_id} not found")
            raise NotFoundException(f"Employee with employee_id '{employee_id}' not found", "EMPLOYEE_NOT_FOUND")
        
        return Employee.model_validate(employee)

    def get_employee_with_details(self, employee_tech_id: str) -> EmployeeWithDetails:
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
            'languages': [lang.__dict__ for lang in components['languages']],
            'technical_skills': [skill.__dict__ for skill in components['technical_skills']],
            'soft_skills': [skill.__dict__ for skill in components['soft_skills']],
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
                'languages': [lang.__dict__ for lang in components['languages']],
                'technical_skills': [skill.__dict__ for skill in components['technical_skills']],
                'soft_skills': [skill.__dict__ for skill in components['soft_skills']],
                'projects': [proj.__dict__ for proj in components['projects']]
            })
            
            employees_with_details.append(EmployeeWithDetails(**employee_dict))
        
        return EmployeePaginationResponse(
            employees=employees_with_details,
            total=total,
            page=page,
            page_size=page_size,
        )

    def update_employee(self, employee_tech_id: str, employee_update: EmployeeUpdate) -> Employee:
        """Update an Employee"""
        logger.info(f"Starting Employee update process for Employee ID: {employee_tech_id}")
        
        # Check if Employee exists
        existing_employee = self.employee_repository.get_employee_by_id(employee_tech_id)
        if not existing_employee:
            raise NotFoundException(f"Employee with ID '{employee_tech_id}' not found", "EMPLOYEE_NOT_FOUND")
        
        # Check for email conflicts if email is being updated
        if employee_update.email and employee_update.email != existing_employee.email:
            if self.employee_repository.email_exists(employee_update.email, exclude_tech_id=employee_tech_id):
                logger.warning(f"Employee update failed: Email {employee_update.email} already exists")
                raise ConflictException(
                    f"Email '{employee_update.email}' already exists in the system",
                    "EMAIL_EXISTS"
                )
        
        # Check for employee_id conflicts if employee_id is being updated
        if employee_update.employee_id and employee_update.employee_id != existing_employee.employee_id:
            if self.employee_repository.employee_id_exists(employee_update.employee_id, exclude_tech_id=employee_tech_id):
                logger.warning(f"Employee update failed: Employee ID {employee_update.employee_id} already exists")
                raise ConflictException(
                    f"Employee ID '{employee_update.employee_id}' already exists in the system",
                    "EMPLOYEE_ID_EXISTS"
                )
        
        # Prepare update data
        update_data = employee_update.model_dump(exclude_unset=True)
        if 'gender' in update_data and update_data['gender']:
            update_data['gender'] = update_data['gender'].value
        
        try:
            updated_employee = self.employee_repository.update_employee(employee_tech_id, update_data)
            logger.info(f"Employee updated successfully: {employee_tech_id}")
            return Employee.model_validate(updated_employee)
            
        except IntegrityError as e:
            logger.error(f"Database integrity error during Employee update: {str(e)}")
            raise ConflictException("Employee update failed due to database constraints", "EMPLOYEE_UPDATE_CONFLICT")
        except Exception as e:
            logger.error(f"Unexpected error during Employee update: {str(e)}")
            raise InternalServerException(f"Employee update failed: {str(e)}", "EMPLOYEE_UPDATE_ERROR")

    def delete_employee(self, employee_tech_id: str) -> None:
        """Delete an Employee and all related data"""
        logger.info(f"Starting Employee deletion process for Employee ID: {employee_tech_id}")
        
        # Check if Employee exists
        if not self.employee_repository.employee_exists(employee_tech_id):
            raise NotFoundException(f"Employee with ID '{employee_tech_id}' not found", "EMPLOYEE_NOT_FOUND")
        
        try:
            # Delete related components first
            deleted_counts = self.bulk_operations.delete_all_employee_components(employee_tech_id)
            logger.info(f"Deleted Employee components: {deleted_counts}")
            
            # Delete Employee
            if self.employee_repository.delete_employee(employee_tech_id):
                logger.info(f"Employee deleted successfully: {employee_tech_id}")
            else:
                raise InternalServerException("Failed to delete Employee", "EMPLOYEE_DELETE_FAILED")
            
        except Exception as e:
            logger.error(f"Employee deletion failed for Employee ID: {employee_tech_id}: {str(e)}")
            raise InternalServerException("Failed to delete Employee", "EMPLOYEE_DELETE_FAILED")

    def search_employees(self, search_request: EmployeeSearchRequest) -> EmployeePaginationResponse:
        """Search Employees by various criteria"""
        logger.info(f"Searching Employees with criteria: {search_request.model_dump()}")
        
        # Calculate skip
        skip = (search_request.page - 1) * search_request.page_size
        
        # Search Employees
        employees = self.employee_repository.search_employees(
            email=search_request.email,
            position=search_request.position,
            employee_id=search_request.employee_id,
            skip=skip,
            limit=search_request.page_size
        )
        
        # For now, use len(employees) as total (in production, would need separate count query)
        total = len(employees)        
        return EmployeePaginationResponse(
            employees=[Employee.model_validate(employee) for employee in employees],
            total=total,
            page=search_request.page,
            page_size=search_request.page_size,
        )

    def bulk_create_employees(self, bulk_request: EmployeeBulkCreate) -> EmployeeBulkResponse:
        """Bulk create multiple Employees"""
        logger.info(f"Starting bulk Employee creation for {len(bulk_request.employees)} Employees")
        
        created_employees = []
        errors = []
        
        for i, employee_create in enumerate(bulk_request.employees):
            try:
                employee = self.create_employee(employee_create)
                created_employees.append(employee)
                logger.debug(f"Bulk created Employee {i+1}: {employee.id}")
            except Exception as e:
                error_msg = f"Employee {i+1} (email: {employee_create.email}): {str(e)}"
                errors.append(error_msg)
                logger.error(f"Bulk creation failed for Employee {i+1}: {str(e)}")
        
        logger.info(f"Bulk creation completed: {len(created_employees)} success, {len(errors)} errors")
        
        return EmployeeBulkResponse(
            created_count=len(created_employees),
            created_employees=created_employees,
            errors=errors if errors else None
        )

    def create_employee_components(self, request: EmployeeComponentCreateRequest) -> EmployeeComponentsResponse:
        """Create components for existing Employee"""
        logger.info(f"Creating components for Employee: {request.employee_id}")
        
        # Check if Employee exists
        if not self.employee_repository.employee_exists(request.employee_id):
            raise NotFoundException(f"Employee with ID '{request.employee_id}' not found", "EMPLOYEE_NOT_FOUND")
        
        try:
            # Prepare components data
            components_data = {}
            
            if request.languages:
                components_data['languages'] = [lang.model_dump() for lang in request.languages]
            
            if request.technical_skills:
                components_data['technical_skills'] = [skill.model_dump() for skill in request.technical_skills]
            
            if request.soft_skills:
                components_data['soft_skills'] = [skill.model_dump() for skill in request.soft_skills]
            
            if request.projects:
                components_data['projects'] = [proj.model_dump() for proj in request.projects]
            
            # Create components
            created_components = self.bulk_operations.bulk_create_employee_components(request.employee_id, components_data)
            
            # Convert to response
            return EmployeeComponentsResponse(
                employee_id=request.employee_id,
                languages=[lang.__dict__ for lang in created_components.get('languages', [])],
                technical_skills=[skill.__dict__ for skill in created_components.get('technical_skills', [])],
                soft_skills=[skill.__dict__ for skill in created_components.get('soft_skills', [])],
                projects=[proj.__dict__ for proj in created_components.get('projects', [])]
            )
            
        except Exception as e:
            logger.error(f"Failed to create Employee components: {str(e)}")
            raise InternalServerException(f"Component creation failed: {str(e)}", "COMPONENT_CREATION_ERROR")

    def get_employee_components(self, employee_tech_id: str) -> EmployeeComponentsResponse:
        """Get all components for an Employee"""
        logger.info(f"Getting components for Employee: {employee_tech_id}")
        
        # Check if Employee exists
        if not self.employee_repository.employee_exists(employee_tech_id):
            raise NotFoundException(f"Employee with ID '{employee_tech_id}' not found", "EMPLOYEE_NOT_FOUND")
        
        # Get components
        components = self.bulk_operations.get_all_employee_components(employee_tech_id)
        
        return EmployeeComponentsResponse(
            employee_id=employee_tech_id,
            languages=[lang.__dict__ for lang in components['languages']],
            technical_skills=[skill.__dict__ for skill in components['technical_skills']],
            soft_skills=[skill.__dict__ for skill in components['soft_skills']],
            projects=[proj.__dict__ for proj in components['projects']]
        )

    def _create_employee_components(self, employee_tech_id: str, employee_create: EmployeeCreate) -> None:
        """Create Employee related components"""
        try:
            components_data = {}
            
            if employee_create.languages:
                components_data['languages'] = [
                    {**lang.model_dump(), 'proficiency': lang.proficiency.value}
                    for lang in employee_create.languages
                ]
            
            if employee_create.technical_skills:
                components_data['technical_skills'] = [
                    {**skill.model_dump(), 'category': skill.category.value}
                    for skill in employee_create.technical_skills
                ]
            
            if employee_create.soft_skills:
                components_data['soft_skills'] = [
                    {**skill.model_dump(), 'skill_name': skill.skill_name.value}
                    for skill in employee_create.soft_skills
                ]
            
            if employee_create.projects:
                components_data['projects'] = [proj.model_dump() for proj in employee_create.projects]
            
            self.bulk_operations.bulk_create_employee_components(employee_tech_id, components_data)
            
        except Exception as e:
            logger.error(f"Failed to create Employee components for {employee_tech_id}: {str(e)}")
            raise