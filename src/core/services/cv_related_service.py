# src/core/services/cv_related_service.py
import logging
from typing import Dict, Any
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.present.request.cv_related import (
    LanguageCreateRequest, LanguageResponse,
    TechnicalSkillCreateRequest, TechnicalSkillResponse,
    SoftSkillCreateRequest, SoftSkillResponse,
    ProjectCreateRequest, ProjectResponse
)
from src.repository.cv_related_repository import (
    LanguageRepository, TechnicalSkillRepository,
    SoftSkillRepository, ProjectRepository
)
from src.core.models.cv import CV
from src.common.exception.exceptions import (
    ValidationException, ConflictException, 
    NotFoundException, InternalServerException
)

logger = logging.getLogger(__name__)


class CVRelatedService:
    """Service for CV related entities (Languages, Skills, Projects)"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.language_repo = LanguageRepository(db_session)
        self.tech_skill_repo = TechnicalSkillRepository(db_session)
        self.soft_skill_repo = SoftSkillRepository(db_session)
        self.project_repo = ProjectRepository(db_session)
    
    def _check_cv_exists(self, cv_id: str) -> None:
        """Check if CV exists, raise NotFoundException if not"""
        cv = self.db_session.query(CV).filter(CV.id == cv_id).first()
        if not cv:
            logger.warning(f"CV with ID {cv_id} not found")
            raise NotFoundException(
                f"CV with ID '{cv_id}' not found. Cannot create related data.",
                "CV_NOT_FOUND"
            )
    
    # Language operations
    def create_language(self, request: LanguageCreateRequest) -> LanguageResponse:
        """Create a new language for a CV"""
        logger.info(f"Creating language '{request.language_name}' for CV: {request.cv_id}")
        
        try:
            # Check if CV exists
            self._check_cv_exists(request.cv_id)
            
            # Convert request to dict
            language_data = {
                "cv_id": request.cv_id,
                "language_name": request.language_name,
                "proficiency": request.proficiency.value,
                "description": request.description
            }
            
            # Create language using repository
            language = self.language_repo.create_language(language_data)
            
            logger.info(f"Language created successfully: {language.language_name} (ID: {language.id})")
            
            # Return response model
            return LanguageResponse(
                id=language.id,
                cv_id=language.cv_id,
                language_name=language.language_name,
                proficiency=language.proficiency,
                description=language.description,
                created_at=language.created_at
            )
            
        except ValidationException:
            raise
        except NotFoundException:
            raise
        except ValueError as e:
            logger.error(f"Language validation error: {str(e)}")
            raise ValidationException(f"Language validation failed: {str(e)}", "LANGUAGE_VALIDATION_ERROR")
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Language creation failed - integrity error: {str(e)}")
            raise ConflictException(
                f"Language creation failed: CV ID '{request.cv_id}' may not exist or data conflict occurred",
                "LANGUAGE_INTEGRITY_ERROR"
            )
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Unexpected error creating language: {str(e)}")
            raise InternalServerException(
                f"Language creation failed: {str(e)}",
                "LANGUAGE_CREATION_ERROR"
            )
    
    # Technical Skill operations
    def create_technical_skill(self, request: TechnicalSkillCreateRequest) -> TechnicalSkillResponse:
        """Create a new technical skill for a CV"""
        logger.info(f"Creating technical skill '{request.skill_name}' for CV: {request.cv_id}")
        
        try:
            # Check if CV exists
            self._check_cv_exists(request.cv_id)
            
            # Convert request to dict
            skill_data = {
                "cv_id": request.cv_id,
                "category": request.category.value,
                "skill_name": request.skill_name,
                "description": request.description
            }
            
            # Create skill using repository
            skill = self.tech_skill_repo.create_skill(skill_data)
            
            logger.info(f"Technical skill created successfully: {skill.skill_name} (ID: {skill.id})")
            
            # Return response model
            return TechnicalSkillResponse(
                id=skill.id,
                cv_id=skill.cv_id,
                category=skill.category,
                skill_name=skill.skill_name,
                description=skill.description,
                created_at=skill.created_at
            )
            
        except ValidationException:
            raise
        except NotFoundException:
            raise
        except ValueError as e:
            logger.error(f"Technical skill validation error: {str(e)}")
            raise ValidationException(f"Technical skill validation failed: {str(e)}", "TECHNICAL_SKILL_VALIDATION_ERROR")
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Technical skill creation failed - integrity error: {str(e)}")
            raise ConflictException(
                f"Technical skill creation failed: CV ID '{request.cv_id}' may not exist or data conflict occurred",
                "TECHNICAL_SKILL_INTEGRITY_ERROR"
            )
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Unexpected error creating technical skill: {str(e)}")
            raise InternalServerException(
                f"Technical skill creation failed: {str(e)}",
                "TECHNICAL_SKILL_CREATION_ERROR"
            )
    
    # Soft Skill operations
    def create_soft_skill(self, request: SoftSkillCreateRequest) -> SoftSkillResponse:
        """Create a new soft skill for a CV"""
        logger.info(f"Creating soft skill '{request.skill_name}' for CV: {request.cv_id}")
        
        try:
            # Check if CV exists
            self._check_cv_exists(request.cv_id)
            
            # Convert request to dict
            skill_data = {
                "cv_id": request.cv_id,
                "skill_name": request.skill_name.value,
                "description": request.description
            }
            
            # Create skill using repository
            skill = self.soft_skill_repo.create_soft_skill(skill_data)
            
            logger.info(f"Soft skill created successfully: {skill.skill_name} (ID: {skill.id})")
            
            # Return response model
            return SoftSkillResponse(
                id=skill.id,
                cv_id=skill.cv_id,
                skill_name=skill.skill_name,
                description=skill.description,
                created_at=skill.created_at
            )
            
        except ValidationException:
            raise
        except NotFoundException:
            raise
        except ValueError as e:
            logger.error(f"Soft skill validation error: {str(e)}")
            raise ValidationException(f"Soft skill validation failed: {str(e)}", "SOFT_SKILL_VALIDATION_ERROR")
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Soft skill creation failed - integrity error: {str(e)}")
            raise ConflictException(
                f"Soft skill creation failed: CV ID '{request.cv_id}' may not exist or data conflict occurred",
                "SOFT_SKILL_INTEGRITY_ERROR"
            )
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Unexpected error creating soft skill: {str(e)}")
            raise InternalServerException(
                f"Soft skill creation failed: {str(e)}",
                "SOFT_SKILL_CREATION_ERROR"
            )
    
    # Project operations
    def create_project(self, request: ProjectCreateRequest) -> ProjectResponse:
        """Create a new project for a CV"""
        logger.info(f"Creating project '{request.project_name}' for CV: {request.cv_id}")
        
        try:
            # Check if CV exists
            self._check_cv_exists(request.cv_id)
            
            # Convert request to dict
            project_data = {
                "cv_id": request.cv_id,
                "project_name": request.project_name,
                "project_description": request.project_description,
                "position": request.position,
                "responsibilities": request.responsibilities,
                "programming_languages": request.programming_languages
            }
            
            # Create project using repository
            project = self.project_repo.create_project(project_data)
            
            logger.info(f"Project created successfully: {project.project_name} (ID: {project.id})")
            
            # Return response model
            return ProjectResponse(
                id=project.id,
                cv_id=project.cv_id,
                project_name=project.project_name,
                project_description=project.project_description,
                position=project.position,
                responsibilities=project.responsibilities,
                programming_languages=project.programming_languages,
                created_at=project.created_at
            )
            
        except ValidationException:
            raise
        except NotFoundException:
            raise
        except ValueError as e:
            logger.error(f"Project validation error: {str(e)}")
            raise ValidationException(f"Project validation failed: {str(e)}", "PROJECT_VALIDATION_ERROR")
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"Project creation failed - integrity error: {str(e)}")
            raise ConflictException(
                f"Project creation failed: CV ID '{request.cv_id}' may not exist or data conflict occurred",
                "PROJECT_INTEGRITY_ERROR"
            )
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Unexpected error creating project: {str(e)}")
            raise InternalServerException(
                f"Project creation failed: {str(e)}",
                "PROJECT_CREATION_ERROR"
            )