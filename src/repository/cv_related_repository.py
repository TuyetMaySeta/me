from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

from .base_repository import BaseRepository
from src.core.models.cv import Language, TechnicalSkill, SoftSkill, Project

logger = logging.getLogger(__name__)


class LanguageRepository(BaseRepository[Language]):
    """Repository for Language operations (CRUD only)."""
    
    def __init__(self, db: Session):
        super().__init__(db, Language)

    def create_language(self, data: Dict[str, Any]) -> Language:
        """Create a language (no validation here)."""
        try:
            language = self.create(data)
            logger.info(f"Successfully created language: {language.language_name} for CV: {language.cv_id}")
            return language
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Language creation failed - integrity error: {str(e)}")
            raise ValueError(f"Language creation failed: CV ID {data.get('cv_id')} may not exist")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Language creation failed - database error: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")


class TechnicalSkillRepository(BaseRepository[TechnicalSkill]):
    """Repository for Technical Skill operations (CRUD only)."""
    
    def __init__(self, db: Session):
        super().__init__(db, TechnicalSkill)

    def create_skill(self, data: Dict[str, Any]) -> TechnicalSkill:
        """Create a technical skill (no validation here)."""
        try:
            skill = self.create(data)
            logger.info(f"Successfully created technical skill: {skill.skill_name} for CV: {skill.cv_id}")
            return skill
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Technical skill creation failed - integrity error: {str(e)}")
            raise ValueError(f"Technical skill creation failed: CV ID {data.get('cv_id')} may not exist")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Technical skill creation failed - database error: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")


class SoftSkillRepository(BaseRepository[SoftSkill]):
    """Repository for Soft Skill operations (CRUD only)."""
    
    def __init__(self, db: Session):
        super().__init__(db, SoftSkill)

    def create_soft_skill(self, data: Dict[str, Any]) -> SoftSkill:
        """Create a soft skill (no validation here)."""
        try:
            skill = self.create(data)
            logger.info(f"Successfully created soft skill: {skill.skill_name} for CV: {skill.cv_id}")
            return skill
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Soft skill creation failed - integrity error: {str(e)}")
            raise ValueError(f"Soft skill creation failed: CV ID {data.get('cv_id')} may not exist")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Soft skill creation failed - database error: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project operations (CRUD only)."""
    
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def create_project(self, data: Dict[str, Any]) -> Project:
        """Create a project (no validation here)."""
        try:
            project = self.create(data)
            logger.info(f"Successfully created project: {project.project_name} for CV: {project.cv_id}")
            return project
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Project creation failed - integrity error: {str(e)}")
            raise ValueError(f"Project creation failed: CV ID {data.get('cv_id')} may not exist")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Project creation failed - database error: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")


# Bulk operations for all repositories
# Bulk operations for all repositories
class CVRelatedBulkOperations:
    """Helper class for bulk operations across all CV-related repositories (CRUD only)."""
    
    def __init__(self, db: Session):
        self.db = db
        self.language_repo = LanguageRepository(db)
        self.tech_skill_repo = TechnicalSkillRepository(db)
        self.soft_skill_repo = SoftSkillRepository(db)
        self.project_repo = ProjectRepository(db)
    
    def bulk_create_cv_components(self, cv_id: str, components: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List]:
        """
        Bulk create all CV components (languages, skills, projects) for a CV.
        Assumes validation is already done at the service/schema layer.
        """
        results = {
            'languages': [],
            'technical_skills': [],
            'soft_skills': [],
            'projects': []
        }
        
        try:
            if 'languages' in components:
                for lang_data in components['languages']:
                    lang_data['cv_id'] = cv_id
                results['languages'] = [
                    self.language_repo.create_language(lang_data) 
                    for lang_data in components['languages']
                ]
            
            if 'technical_skills' in components:
                for skill_data in components['technical_skills']:
                    skill_data['cv_id'] = cv_id
                results['technical_skills'] = [
                    self.tech_skill_repo.create_skill(skill_data) 
                    for skill_data in components['technical_skills']
                ]
            
            if 'soft_skills' in components:
                for skill_data in components['soft_skills']:
                    skill_data['cv_id'] = cv_id
                results['soft_skills'] = [
                    self.soft_skill_repo.create_soft_skill(skill_data) 
                    for skill_data in components['soft_skills']
                ]
            
            if 'projects' in components:
                for proj_data in components['projects']:
                    proj_data['cv_id'] = cv_id
                results['projects'] = [
                    self.project_repo.create_project(proj_data) 
                    for proj_data in components['projects']
                ]
            
            logger.info(f"Successfully bulk created CV components for CV: {cv_id}")
            return results
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Bulk CV components creation failed for CV {cv_id}: {str(e)}")
            raise ValueError(f"Bulk creation failed: {str(e)}")