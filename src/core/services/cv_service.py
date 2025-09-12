# src/core/services/cv_service.py (Improved Error Handling)
from typing import List, Optional, Dict, Any
import logging
import random
import string
from sqlalchemy.exc import IntegrityError
from src.present.request.cv import CVCreate, CVUpdate, CVWithDetails
from src.common.exception.exceptions import ValidationException, ConflictException, NotFoundException, InternalServerException
from src.repository.cv_repository import CVRepository

logger = logging.getLogger(__name__)


class CVService:
    """CV service with business logic for CV operations"""
    
    def __init__(self, cv_repository: CVRepository, db_session):
        self.cv_repository = cv_repository
        self.db_session = db_session
    
    def _generate_cv_id(self, length: int = 6) -> str:
        """Generate random CV ID"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    def create_cv(self, cv_create: CVCreate):
        """Create a new CV with optional related data"""
        logger.info(f"Starting CV creation process for: {cv_create.email}")
        
        try:
            # Check for duplicates BEFORE creating
            existing_email = self.get_cv_by_email(cv_create.email)
            if existing_email:
                logger.warning(f"CV creation failed: Email '{cv_create.email}' already exists")
                raise ConflictException(
                    f"Email '{cv_create.email}' already exists in the system. Please use a different email address.",
                    "DUPLICATE_EMAIL"
                )
            
            existing_seta = self.get_cv_by_seta_id(cv_create.id_seta) 
            if existing_seta:
                logger.warning(f"CV creation failed: SETA ID '{cv_create.id_seta}' already exists")
                raise ConflictException(
                    f"SETA ID '{cv_create.id_seta}' already exists in the system. Please use a different SETA ID.",
                    "DUPLICATE_SETA_ID"
                )
            
            # Generate unique CV ID
            cv_id = self._generate_cv_id()
            while self._cv_id_exists(cv_id):
                cv_id = self._generate_cv_id()
            
            # Prepare CV data
            cv_data = {
                "id": cv_id,
                "id_seta": cv_create.id_seta,
                "email": cv_create.email,
                "full_name": cv_create.full_name,
                "gender": cv_create.gender.value if cv_create.gender else None,
                "current_position": cv_create.current_position,
                "summary": cv_create.summary
            }
            
            # Create CV using repository
            cv = self.cv_repository.create_cv(cv_data)
            logger.info(f"CV created successfully: {cv.id} for {cv.email}")
            
            # Create related data if provided
            if any([cv_create.languages, cv_create.technical_skills, 
                   cv_create.soft_skills, cv_create.projects]):
                try:
                    self._create_cv_components(cv_id, cv_create)
                    logger.info(f"CV components created for CV: {cv_id}")
                except Exception as comp_error:
                    logger.error(f"Failed to create CV components for {cv_id}: {str(comp_error)}")
                    # Rollback CV creation if components fail
                    try:
                        self.db_session.delete(cv)
                        self.db_session.commit()
                        logger.info(f"Rolled back CV {cv_id} due to component creation failure")
                    except:
                        pass
                    raise ValidationException(f"CV components creation failed: {str(comp_error)}", "CV_COMPONENTS_ERROR")
            
            return cv
            
        except ValidationException:
            raise
        except ConflictException:
            raise
        except IntegrityError as e:
            logger.error(f"Database integrity error during CV creation: {str(e)}")
            error_str = str(e).lower()
            
            # Parse specific constraint violations
            if 'email' in error_str and 'unique' in error_str:
                raise ConflictException(
                    f"Email '{cv_create.email}' already exists in the system. Please use a different email address.",
                    "DUPLICATE_EMAIL"
                )
            elif 'id_seta' in error_str and 'unique' in error_str:
                raise ConflictException(
                    f"SETA ID '{cv_create.id_seta}' already exists in the system. Please use a different SETA ID.", 
                    "DUPLICATE_SETA_ID"
                )
            elif 'primary key' in error_str:
                raise ConflictException(
                    "CV ID conflict occurred. Please try again.",
                    "DUPLICATE_CV_ID"
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
    
    def _create_cv_components(self, cv_id: str, cv_create: CVCreate) -> None:
        """Create CV related components with detailed error messages"""
        components = {}
        
        # Prepare components data
        if cv_create.languages:
            components['languages'] = [lang.model_dump() for lang in cv_create.languages]
        
        if cv_create.technical_skills:
            components['technical_skills'] = [skill.model_dump() for skill in cv_create.technical_skills]
        
        if cv_create.soft_skills:
            components['soft_skills'] = [skill.model_dump() for skill in cv_create.soft_skills]
        
        if cv_create.projects:
            components['projects'] = [proj.model_dump() for proj in cv_create.projects]
        
        # Validate all components before creation
        validation_errors = self.bulk_operations.validate_all_components(components)
        if validation_errors:
            logger.error(f"CV components validation failed: {validation_errors}")
            
            # Format validation errors nicely
            error_messages = []
            for component_type, component_errors in validation_errors.items():
                for component_name, field_errors in component_errors.items():
                    for field, messages in field_errors.items():
                        error_messages.append(f"{component_type}.{component_name}.{field}: {'; '.join(messages)}")
            
            formatted_error = "Validation failed: " + " | ".join(error_messages)
            raise ValidationException(formatted_error, "CV_COMPONENTS_VALIDATION_ERROR")
        
        # Create all components
        try:
            self.bulk_operations.bulk_create_cv_components(cv_id, components)
        except Exception as e:
            logger.error(f"Failed to create CV components for {cv_id}: {str(e)}")
            raise InternalServerException(
                f"Failed to create CV components: {str(e)}",
                "CV_COMPONENTS_CREATION_ERROR"
            )
    
    def get_cv(self, cv_id: str):
        """Get a CV by ID"""
        from src.core.models.cv import CV
        cv = self.db_session.query(CV).filter(CV.id == cv_id).first()
        if not cv:
            logger.warning(f"CV with ID {cv_id} not found")
            raise NotFoundException(f"CV with ID '{cv_id}' not found", "CV_NOT_FOUND")
        return cv
    
    def get_cv_by_email(self, email: str):
        """Get CV by email"""
        from src.core.models.cv import CV
        return self.db_session.query(CV).filter(CV.email == email).first()
    
    def get_cv_by_seta_id(self, seta_id: str):
        """Get CV by SETA ID"""
        from src.core.models.cv import CV
        return self.db_session.query(CV).filter(CV.id_seta == seta_id).first()
    
    def _cv_id_exists(self, cv_id: str) -> bool:
        """Check if CV ID already exists"""
        from src.core.models.cv import CV
        return self.db_session.query(CV).filter(CV.id == cv_id).first() is not None
    
    # ... rest of the methods remain the same ...