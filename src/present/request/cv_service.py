from typing import List, Optional, Dict, Any
import logging
import random
import string
from sqlalchemy.exc import IntegrityError
from src.core.models.cv import CV
from src.present.request.cv import CVCreate, CVUpdate, CVWithDetails
from src.common.exception.exceptions import ValidationException, ConflictException, NotFoundException, InternalServerException
from src.repository.cv_repository import CVRepository
from src.repository.cv_related_repository import CVRelatedBulkOperations

logger = logging.getLogger(__name__)


class CVService:
    """CV service with business logic for CV operations"""
    
    def __init__(self, cv_repository: CVRepository, db_session):
        self.cv_repository = cv_repository
        self.db_session = db_session
        self.bulk_operations = CVRelatedBulkOperations(db_session)
    
    def _generate_cv_id(self, length: int = 6) -> str:
        """Generate random CV ID"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    def create_cv(self, cv_create: CVCreate) -> CV:
        """Create a new CV with optional related data"""
        logger.info(f"Starting CV creation process for: {cv_create.email}")
        
        try:
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
                self._create_cv_components(cv_id, cv_create)
                logger.info(f"CV components created for CV: {cv_id}")
            
            return cv
            
        except ValidationException:
            raise
        except ConflictException:
            raise
        except IntegrityError as e:
            logger.error(f"Database integrity error during CV creation: {str(e)}")
            raise ConflictException("CV creation failed due to duplicate data", "CV_DUPLICATE_ERROR")
        except Exception as e:
            logger.error(f"Unexpected error during CV creation: {str(e)}")
            raise InternalServerException("CV creation failed", "CV_CREATION_ERROR")
    
    def _create_cv_components(self, cv_id: str, cv_create: CVCreate) -> None:
        """Create CV related components"""
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
            raise ValidationException(f"CV components validation failed: {validation_errors}")
        
        # Create all components
        try:
            self.bulk_operations.bulk_create_cv_components(cv_id, components)
        except Exception as e:
            logger.error(f"Failed to create CV components for {cv_id}: {str(e)}")
            raise InternalServerException("Failed to create CV components", "CV_COMPONENTS_ERROR")
    
    def get_cv(self, cv_id: str) -> CV:
        """Get a CV by ID"""
        cv = self.db_session.query(CV).filter(CV.id == cv_id).first()
        if not cv:
            logger.warning(f"CV with ID {cv_id} not found")
            raise NotFoundException(f"CV with ID {cv_id} not found", "CV_NOT_FOUND")
        return cv
    
    def get_cv_with_details(self, cv_id: str) -> CVWithDetails:
        """Get CV with all related details"""
        cv = self.get_cv(cv_id)
        
        # Get related data
        from src.core.models.cv import Language, TechnicalSkill, SoftSkill, Project
        
        languages = self.db_session.query(Language).filter(Language.cv_id == cv_id).all()
        technical_skills = self.db_session.query(TechnicalSkill).filter(TechnicalSkill.cv_id == cv_id).all()
        soft_skills = self.db_session.query(SoftSkill).filter(SoftSkill.cv_id == cv_id).all()
        projects = self.db_session.query(Project).filter(Project.cv_id == cv_id).all()
        
        # Create response with details
        cv_dict = {
            "id": cv.id,
            "id_seta": cv.id_seta,
            "email": cv.email,
            "full_name": cv.full_name,
            "gender": cv.gender,
            "current_position": cv.current_position,
            "summary": cv.summary,
            "created_at": cv.created_at,
            "updated_at": cv.updated_at,
            "languages": languages,
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "projects": projects
        }
        
        return CVWithDetails(**cv_dict)
    
    def get_cvs(self, skip: int = 0, limit: int = 100) -> List[CV]:
        """Get multiple CVs with pagination"""
        logger.info(f"Getting CVs with pagination: skip={skip}, limit={limit}")
        return self.db_session.query(CV).offset(skip).limit(limit).all()
    
    def get_cv_by_email(self, email: str) -> Optional[CV]:
        """Get CV by email"""
        return self.db_session.query(CV).filter(CV.email == email).first()
    
    def get_cv_by_seta_id(self, seta_id: str) -> Optional[CV]:
        """Get CV by SETA ID"""
        return self.db_session.query(CV).filter(CV.id_seta == seta_id).first()
    
    def update_cv(self, cv_id: str, cv_update: CVUpdate) -> CV:
        """Update a CV"""
        logger.info(f"Starting CV update process for CV ID: {cv_id}")
        
        cv = self.get_cv(cv_id)
        
        # Check for email conflicts if email is being updated
        if cv_update.email and cv_update.email != cv.email:
            existing_cv = self.get_cv_by_email(cv_update.email)
            if existing_cv:
                logger.warning(f"CV update failed: Email {cv_update.email} already exists")
                raise ConflictException("Email already exists", "EMAIL_EXISTS")
        
        # Check for SETA ID conflicts if SETA ID is being updated
        if cv_update.id_seta and cv_update.id_seta != cv.id_seta:
            existing_cv = self.get_cv_by_seta_id(cv_update.id_seta)
            if existing_cv:
                logger.warning(f"CV update failed: SETA ID {cv_update.id_seta} already exists")
                raise ConflictException("SETA ID already exists", "SETA_ID_EXISTS")
        
        # Update CV data
        update_data = cv_update.model_dump(exclude_unset=True)
        
        try:
            for field, value in update_data.items():
                if hasattr(cv, field):
                    setattr(cv, field, value)
            
            self.db_session.commit()
            self.db_session.refresh(cv)
            
            logger.info(f"CV updated successfully: {cv.id}")
            return cv
            
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Database integrity error during CV update: {str(e)}")
            raise ConflictException("CV update failed due to database constraints", "CV_UPDATE_CONFLICT")
    
    def delete_cv(self, cv_id: str) -> None:
        """Delete a CV and all related data"""
        logger.info(f"Starting CV deletion process for CV ID: {cv_id}")
        
        cv = self.get_cv(cv_id)
        
        try:
            # Delete related data first (due to foreign key constraints)
            from src.core.models.cv import Language, TechnicalSkill, SoftSkill, Project
            
            self.db_session.query(Language).filter(Language.cv_id == cv_id).delete()
            self.db_session.query(TechnicalSkill).filter(TechnicalSkill.cv_id == cv_id).delete()
            self.db_session.query(SoftSkill).filter(SoftSkill.cv_id == cv_id).delete()
            self.db_session.query(Project).filter(Project.cv_id == cv_id).delete()
            
            # Delete CV
            self.db_session.delete(cv)
            self.db_session.commit()
            
            logger.info(f"CV deleted successfully: {cv_id}")
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"CV deletion failed for CV ID: {cv_id}: {str(e)}")
            raise InternalServerException("Failed to delete CV", "CV_DELETE_FAILED")
    
    def bulk_create_cvs(self, cvs_data: List[CVCreate]) -> Dict[str, Any]:
        """Bulk create multiple CVs"""
        logger.info(f"Starting bulk CV creation for {len(cvs_data)} CVs")
        
        created_cvs = []
        errors = []
        
        for i, cv_data in enumerate(cvs_data):
            try:
                cv = self.create_cv(cv_data)
                created_cvs.append(cv)
            except Exception as e:
                error_msg = f"CV {i+1}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Failed to create CV {i+1}: {str(e)}")
        
        result = {
            "created_count": len(created_cvs),
            "created_cvs": created_cvs,
            "errors": errors
        }
        
        logger.info(f"Bulk CV creation completed: {len(created_cvs)} created, {len(errors)} errors")
        return result
    
    def search_cvs(self, 
                   email: Optional[str] = None,
                   seta_id: Optional[str] = None,
                   position: Optional[str] = None,
                   skill: Optional[str] = None,
                   skip: int = 0,
                   limit: int = 100) -> List[CV]:
        """Search CVs by various criteria"""
        query = self.db_session.query(CV)
        
        if email:
            query = query.filter(CV.email.ilike(f"%{email}%"))
        
        if seta_id:
            query = query.filter(CV.id_seta.ilike(f"%{seta_id}%"))
        
        if position:
            query = query.filter(CV.current_position.ilike(f"%{position}%"))
        
        if skill:
            # Search in technical skills
            from src.core.models.cv import TechnicalSkill
            cv_ids_with_skill = self.db_session.query(TechnicalSkill.cv_id).filter(
                TechnicalSkill.skill_name.ilike(f"%{skill}%")
            ).subquery()
            query = query.filter(CV.id.in_(cv_ids_with_skill))
        
        return query.offset(skip).limit(limit).all()
    
    def _cv_id_exists(self, cv_id: str) -> bool:
        """Check if CV ID already exists"""
        return self.db_session.query(CV).filter(CV.id == cv_id).first() is not None