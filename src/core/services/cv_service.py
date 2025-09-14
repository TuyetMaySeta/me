# src/core/services/cv_service.py
from typing import List, Optional, Dict, Any
import logging
import random
import string
from sqlalchemy.exc import IntegrityError
from src.present.request.cv import CVCreate, CVUpdate, CVWithDetails
from src.common.exception.exceptions import ValidationException, ConflictException, NotFoundException, InternalServerException
from src.repository.cv_repository import CVRepository
from src.core.models.cv import CV

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
            # Check for email duplicate BEFORE creating
            existing_email = self.get_cv_by_email(cv_create.email)
            if existing_email:
                logger.warning(f"CV creation failed: Email '{cv_create.email}' already exists")
                raise ConflictException(
                    f"Email '{cv_create.email}' already exists in the system. Please use a different email address.",
                    "DUPLICATE_EMAIL"
                )
            
            # Generate unique CV ID
            cv_id = self._generate_cv_id()
            while self._cv_id_exists(cv_id):
                cv_id = self._generate_cv_id()
            
            # Prepare CV data (removed id_seta)
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
            
            # Create related data if provided (link dữ liệu tới các bảng con)
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
    
    def _cv_id_exists(self, cv_id: str) -> bool:
        """Check if CV ID already exists"""
        from src.core.models.cv import CV
        return self.db_session.query(CV).filter(CV.id == cv_id).first() is not None
    
    def get_cvs(self, page: int = 1, page_size: int = 10):
        """Get CVs with pagination"""
        from src.core.models.cv import CV
        offset = (page - 1) * page_size
        return (
            self.db_session.query(CV)
            .offset(offset)
            .limit(page_size)
            .all()
        )
    
    def update_cv(self, cv_id: str, cv_update: CVUpdate) -> CV:
        """Update a CV"""
        logger.info(f"Starting CV update process for CV ID: {cv_id}")
        
        cv = self.get_cv(cv_id)
        
        # Check for email conflicts if email is being updated
        if cv_update.email and cv_update.email != cv.email:
            existing_cv = self.get_cv_by_email(cv_update.email)
            if existing_cv:
                logger.warning(f"CV update failed: Email {cv_update.email} already exists")
                raise ConflictException(
                    f"Email '{cv_update.email}' already exists in the system",
                    "EMAIL_EXISTS"
                )
        
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
    
    def search_cvs(self, 
                   email: Optional[str] = None,
                   position: Optional[str] = None,
                   skill: Optional[str] = None,
                   skip: int = 0,
                   limit: int = 100) -> List[CV]:
        """Search CVs by various criteria"""
        query = self.db_session.query(CV)
        
        if email:
            query = query.filter(CV.email.ilike(f"%{email}%"))
        
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
    
    def _create_cv_components(self, cv_id: str, cv_create: CVCreate) -> None:
        """Create CV related components - implementation tùy thuộc vào cấu trúc repository"""
        # TODO: Implement component creation logic
        # This will depend on your repository structure for related entities
        pass
