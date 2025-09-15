# src/core/services/cv_service.py
from typing import List, Optional, Dict, Any
import logging
import random
import string
import math
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.present.request.cv import (
    CVCreate, CVUpdate, CVWithDetails, CV, 
    CVBulkCreate, CVBulkResponse, CVSearchRequest, 
    CVPaginationResponse, CVComponentCreateRequest, CVComponentsResponse
)
from src.common.exception.exceptions import (
    ValidationException, ConflictException, NotFoundException, InternalServerException
)
from src.repository.cv_repository import CVRepository
from src.repository.cv_related_repository import CVRelatedBulkOperations
from src.core.models.cv import CV as CVModel

logger = logging.getLogger(__name__)


class CVService:
    """CV service with business logic for CV operations"""
    
    def __init__(self, cv_repository: CVRepository, db_session: Session):
        self.cv_repository = cv_repository
        self.db_session = db_session
        self.bulk_operations = CVRelatedBulkOperations(db_session)
    
    def _generate_cv_id(self, length: int = 6) -> str:
        """Generate random CV ID"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    def _ensure_unique_cv_id(self) -> str:
        """Generate unique CV ID"""
        cv_id = self._generate_cv_id()
        while self.cv_repository.cv_exists(cv_id):
            cv_id = self._generate_cv_id()
        return cv_id

    def create_cv(self, cv_create: CVCreate) -> CV:
        """Create a new CV with optional related data"""
        logger.info(f"Starting CV creation process for: {cv_create.email}")
        
        try:
            # Check for email duplicate
            if self.cv_repository.email_exists(cv_create.email):
                logger.warning(f"CV creation failed: Email '{cv_create.email}' already exists")
                raise ConflictException(
                    f"Email '{cv_create.email}' already exists in the system. Please use a different email address.",
                    "DUPLICATE_EMAIL"
                )
            
            # Generate unique CV ID
            cv_id = self._ensure_unique_cv_id()
            
            # Prepare CV data
            cv_data = {
                "id": cv_id,
                "email": cv_create.email,
                "full_name": cv_create.full_name,
                "gender": cv_create.gender.value if cv_create.gender else None,
                "current_position": cv_create.current_position,
                "summary": cv_create.summary
            }
            
            # Create CV using repository
            cv = self.cv_repository.create_cv(cv_data)
            logger.info(f"CV created successfully: {cv.id} for {cv.email}")
            
            # Create related components if provided
            if any([cv_create.languages, cv_create.technical_skills, 
                   cv_create.soft_skills, cv_create.projects]):
                try:
                    self._create_cv_components(cv_id, cv_create)
                    logger.info(f"CV components created for CV: {cv_id}")
                except Exception as comp_error:
                    logger.error(f"Failed to create CV components for {cv_id}: {str(comp_error)}")
                    # Rollback CV creation if components fail
                    try:
                        self.cv_repository.delete_cv(cv_id)
                        logger.info(f"Rolled back CV {cv_id} due to component creation failure")
                    except:
                        pass
                    raise ValidationException(f"CV components creation failed: {str(comp_error)}", "CV_COMPONENTS_ERROR")
            
            return CV.model_validate(cv)
            
        except ValidationException:
            raise
        except ConflictException:
            raise
        except IntegrityError as e:
            logger.error(f"Database integrity error during CV creation: {str(e)}")
            error_str = str(e).lower()
            
            if 'email' in error_str and 'unique' in error_str:
                raise ConflictException(
                    f"Email '{cv_create.email}' already exists in the system.",
                    "DUPLICATE_EMAIL"
                )
            else:
                raise ConflictException(
                    f"Data conflict: {str(e)[:100]}...",
                    "DATABASE_CONSTRAINT_ERROR"
                )
        except Exception as e:
            logger.error(f"Unexpected error during CV creation: {str(e)}")
            raise InternalServerException(
                f"CV creation failed due to server error: {str(e)}",
                "CV_CREATION_ERROR"
            )

    def get_cv(self, cv_id: str) -> CV:
        """Get a CV by ID"""
        logger.info(f"Getting CV: {cv_id}")
        
        cv = self.cv_repository.get_cv_by_id(cv_id)
        if not cv:
            logger.warning(f"CV with ID {cv_id} not found")
            raise NotFoundException(f"CV with ID '{cv_id}' not found", "CV_NOT_FOUND")
        
        return CV.model_validate(cv)

    def get_cv_with_details(self, cv_id: str) -> CVWithDetails:
        """Get CV with all related components"""
        logger.info(f"Getting CV with details: {cv_id}")
        
        # Get CV
        cv = self.cv_repository.get_cv_by_id(cv_id)
        if not cv:
            logger.warning(f"CV with ID {cv_id} not found")
            raise NotFoundException(f"CV with ID '{cv_id}' not found", "CV_NOT_FOUND")
        
        # Get all components
        components = self.bulk_operations.get_all_cv_components(cv_id)
        
        # Convert to response model
        cv_dict = CV.model_validate(cv).model_dump()
        cv_dict.update({
            'languages': [lang.__dict__ for lang in components['languages']],
            'technical_skills': [skill.__dict__ for skill in components['technical_skills']],
            'soft_skills': [skill.__dict__ for skill in components['soft_skills']],
            'projects': [proj.__dict__ for proj in components['projects']]
        })
        
        return CVWithDetails(**cv_dict)

    def get_cvs(self, page: int = 1, page_size: int = 10) -> CVPaginationResponse:
        """Get CVs with pagination"""
        logger.info(f"Getting CVs: page={page}, page_size={page_size}")
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get CVs and total count
        cvs = self.cv_repository.get_all_cvs(skip, page_size)
        total = self.cv_repository.count_total_cvs()
        
        # Calculate total pages
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        return CVPaginationResponse(
            cvs=[CV.model_validate(cv) for cv in cvs],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    def update_cv(self, cv_id: str, cv_update: CVUpdate) -> CV:
        """Update a CV"""
        logger.info(f"Starting CV update process for CV ID: {cv_id}")
        
        # Check if CV exists
        existing_cv = self.cv_repository.get_cv_by_id(cv_id)
        if not existing_cv:
            raise NotFoundException(f"CV with ID '{cv_id}' not found", "CV_NOT_FOUND")
        
        # Check for email conflicts if email is being updated
        if cv_update.email and cv_update.email != existing_cv.email:
            if self.cv_repository.email_exists(cv_update.email, exclude_id=cv_id):
                logger.warning(f"CV update failed: Email {cv_update.email} already exists")
                raise ConflictException(
                    f"Email '{cv_update.email}' already exists in the system",
                    "EMAIL_EXISTS"
                )
        
        # Prepare update data
        update_data = cv_update.model_dump(exclude_unset=True)
        if 'gender' in update_data and update_data['gender']:
            update_data['gender'] = update_data['gender'].value
        
        try:
            updated_cv = self.cv_repository.update_cv(cv_id, update_data)
            logger.info(f"CV updated successfully: {cv_id}")
            return CV.model_validate(updated_cv)
            
        except IntegrityError as e:
            logger.error(f"Database integrity error during CV update: {str(e)}")
            raise ConflictException("CV update failed due to database constraints", "CV_UPDATE_CONFLICT")
        except Exception as e:
            logger.error(f"Unexpected error during CV update: {str(e)}")
            raise InternalServerException(f"CV update failed: {str(e)}", "CV_UPDATE_ERROR")

    def delete_cv(self, cv_id: str) -> None:
        """Delete a CV and all related data"""
        logger.info(f"Starting CV deletion process for CV ID: {cv_id}")
        
        # Check if CV exists
        if not self.cv_repository.cv_exists(cv_id):
            raise NotFoundException(f"CV with ID '{cv_id}' not found", "CV_NOT_FOUND")
        
        try:
            # Delete related components first
            deleted_counts = self.bulk_operations.delete_all_cv_components(cv_id)
            logger.info(f"Deleted CV components: {deleted_counts}")
            
            # Delete CV
            if self.cv_repository.delete_cv(cv_id):
                logger.info(f"CV deleted successfully: {cv_id}")
            else:
                raise InternalServerException("Failed to delete CV", "CV_DELETE_FAILED")
            
        except Exception as e:
            logger.error(f"CV deletion failed for CV ID: {cv_id}: {str(e)}")
            raise InternalServerException("Failed to delete CV", "CV_DELETE_FAILED")

    def search_cvs(self, search_request: CVSearchRequest) -> CVPaginationResponse:
        """Search CVs by various criteria"""
        logger.info(f"Searching CVs with criteria: {search_request.model_dump()}")
        
        # Calculate skip
        skip = (search_request.page - 1) * search_request.page_size
        
        # Search CVs
        cvs = self.cv_repository.search_cvs(
            email=search_request.email,
            position=search_request.position,
            skip=skip,
            limit=search_request.page_size
        )
        
        # For now, use len(cvs) as total (in production, would need separate count query)
        total = len(cvs)
        total_pages = math.ceil(total / search_request.page_size) if total > 0 else 0
        
        return CVPaginationResponse(
            cvs=[CV.model_validate(cv) for cv in cvs],
            total=total,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=total_pages
        )

    def bulk_create_cvs(self, bulk_request: CVBulkCreate) -> CVBulkResponse:
        """Bulk create multiple CVs"""
        logger.info(f"Starting bulk CV creation for {len(bulk_request.cvs)} CVs")
        
        created_cvs = []
        errors = []
        
        for i, cv_create in enumerate(bulk_request.cvs):
            try:
                cv = self.create_cv(cv_create)
                created_cvs.append(cv)
                logger.debug(f"Bulk created CV {i+1}: {cv.id}")
            except Exception as e:
                error_msg = f"CV {i+1} (email: {cv_create.email}): {str(e)}"
                errors.append(error_msg)
                logger.error(f"Bulk creation failed for CV {i+1}: {str(e)}")
        
        logger.info(f"Bulk creation completed: {len(created_cvs)} success, {len(errors)} errors")
        
        return CVBulkResponse(
            created_count=len(created_cvs),
            created_cvs=created_cvs,
            errors=errors if errors else None
        )

    def create_cv_components(self, request: CVComponentCreateRequest) -> CVComponentsResponse:
        """Create components for existing CV"""
        logger.info(f"Creating components for CV: {request.cv_id}")
        
        # Check if CV exists
        if not self.cv_repository.cv_exists(request.cv_id):
            raise NotFoundException(f"CV with ID '{request.cv_id}' not found", "CV_NOT_FOUND")
        
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
            created_components = self.bulk_operations.bulk_create_cv_components(request.cv_id, components_data)
            
            # Convert to response
            return CVComponentsResponse(
                cv_id=request.cv_id,
                languages=[lang.__dict__ for lang in created_components.get('languages', [])],
                technical_skills=[skill.__dict__ for skill in created_components.get('technical_skills', [])],
                soft_skills=[skill.__dict__ for skill in created_components.get('soft_skills', [])],
                projects=[proj.__dict__ for proj in created_components.get('projects', [])]
            )
            
        except Exception as e:
            logger.error(f"Failed to create CV components: {str(e)}")
            raise InternalServerException(f"Component creation failed: {str(e)}", "COMPONENT_CREATION_ERROR")

    def get_cv_components(self, cv_id: str) -> CVComponentsResponse:
        """Get all components for a CV"""
        logger.info(f"Getting components for CV: {cv_id}")
        
        # Check if CV exists
        if not self.cv_repository.cv_exists(cv_id):
            raise NotFoundException(f"CV with ID '{cv_id}' not found", "CV_NOT_FOUND")
        
        # Get components
        components = self.bulk_operations.get_all_cv_components(cv_id)
        
        return CVComponentsResponse(
            cv_id=cv_id,
            languages=[lang.__dict__ for lang in components['languages']],
            technical_skills=[skill.__dict__ for skill in components['technical_skills']],
            soft_skills=[skill.__dict__ for skill in components['soft_skills']],
            projects=[proj.__dict__ for proj in components['projects']]
        )

    def _create_cv_components(self, cv_id: str, cv_create: CVCreate) -> None:
        """Create CV related components"""
        try:
            components_data = {}
            
            if cv_create.languages:
                components_data['languages'] = [
                    {**lang.model_dump(), 'proficiency': lang.proficiency.value}
                    for lang in cv_create.languages
                ]
            
            if cv_create.technical_skills:
                components_data['technical_skills'] = [
                    {**skill.model_dump(), 'category': skill.category.value}
                    for skill in cv_create.technical_skills
                ]
            
            if cv_create.soft_skills:
                components_data['soft_skills'] = [
                    {**skill.model_dump(), 'skill_name': skill.skill_name.value}
                    for skill in cv_create.soft_skills
                ]
            
            if cv_create.projects:
                components_data['projects'] = [proj.model_dump() for proj in cv_create.projects]
            
            self.bulk_operations.bulk_create_cv_components(cv_id, components_data)
            
        except Exception as e:
            logger.error(f"Failed to create CV components for {cv_id}: {str(e)}")
            raise
