# src/repository/cv_related_repository.py
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from src.core.models.cv import Language, TechnicalSkill, SoftSkill, Project

logger = logging.getLogger(__name__)


class LanguageRepository(BaseRepository[Language]):
    """Repository for Language operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, Language)

    def create_language(self, data: Dict[str, Any]) -> Language:
        """Create a language."""
        try:
            language = self.create(data)
            logger.info(f"Successfully created language: {language.language_name} for CV: {language.cv_id}")
            return language
        except SQLAlchemyError as e:
            logger.error(f"Language creation failed: {str(e)}")
            raise

    def get_language_by_id(self, lang_id: int) -> Optional[Language]:
        """Get language by ID."""
        try:
            return self.db.query(Language).filter(Language.id == lang_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting language {lang_id}: {str(e)}")
            raise

    def get_languages_by_cv_id(self, cv_id: str) -> List[Language]:
        """Get all languages for a CV."""
        try:
            languages = self.db.query(Language).filter(Language.cv_id == cv_id).all()
            logger.debug(f"Found {len(languages)} languages for CV: {cv_id}")
            return languages
        except SQLAlchemyError as e:
            logger.error(f"Error getting languages for CV {cv_id}: {str(e)}")
            raise

    def update_language(self, lang_id: int, data: Dict[str, Any]) -> Optional[Language]:
        """Update language by ID."""
        try:
            language = self.get_language_by_id(lang_id)
            if not language:
                return None

            for field, value in data.items():
                if hasattr(language, field) and value is not None:
                    setattr(language, field, value)

            self.db.commit()
            self.db.refresh(language)
            logger.info(f"Successfully updated language: {lang_id}")
            return language
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating language {lang_id}: {str(e)}")
            raise

    def delete_language(self, lang_id: int) -> bool:
        """Delete language by ID."""
        try:
            language = self.get_language_by_id(lang_id)
            if not language:
                return False

            self.db.delete(language)
            self.db.commit()
            logger.info(f"Successfully deleted language: {lang_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting language {lang_id}: {str(e)}")
            raise

    def delete_languages_by_cv_id(self, cv_id: str) -> int:
        """Delete all languages for a CV."""
        try:
            count = self.db.query(Language).filter(Language.cv_id == cv_id).delete()
            self.db.commit()
            logger.info(f"Deleted {count} languages for CV: {cv_id}")
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting languages for CV {cv_id}: {str(e)}")
            raise


class TechnicalSkillRepository(BaseRepository[TechnicalSkill]):
    """Repository for Technical Skill operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, TechnicalSkill)

    def create_skill(self, data: Dict[str, Any]) -> TechnicalSkill:
        """Create a technical skill."""
        try:
            skill = self.create(data)
            logger.info(f"Successfully created technical skill: {skill.skill_name} for CV: {skill.cv_id}")
            return skill
        except SQLAlchemyError as e:
            logger.error(f"Technical skill creation failed: {str(e)}")
            raise

    def get_skill_by_id(self, skill_id: int) -> Optional[TechnicalSkill]:
        """Get technical skill by ID."""
        try:
            return self.db.query(TechnicalSkill).filter(TechnicalSkill.id == skill_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting technical skill {skill_id}: {str(e)}")
            raise

    def get_skills_by_cv_id(self, cv_id: str) -> List[TechnicalSkill]:
        """Get all technical skills for a CV."""
        try:
            skills = self.db.query(TechnicalSkill).filter(TechnicalSkill.cv_id == cv_id).all()
            logger.debug(f"Found {len(skills)} technical skills for CV: {cv_id}")
            return skills
        except SQLAlchemyError as e:
            logger.error(f"Error getting technical skills for CV {cv_id}: {str(e)}")
            raise

    def update_skill(self, skill_id: int, data: Dict[str, Any]) -> Optional[TechnicalSkill]:
        """Update technical skill by ID."""
        try:
            skill = self.get_skill_by_id(skill_id)
            if not skill:
                return None

            for field, value in data.items():
                if hasattr(skill, field) and value is not None:
                    setattr(skill, field, value)

            self.db.commit()
            self.db.refresh(skill)
            logger.info(f"Successfully updated technical skill: {skill_id}")
            return skill
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating technical skill {skill_id}: {str(e)}")
            raise

    def delete_skill(self, skill_id: int) -> bool:
        """Delete technical skill by ID."""
        try:
            skill = self.get_skill_by_id(skill_id)
            if not skill:
                return False

            self.db.delete(skill)
            self.db.commit()
            logger.info(f"Successfully deleted technical skill: {skill_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting technical skill {skill_id}: {str(e)}")
            raise

    def delete_skills_by_cv_id(self, cv_id: str) -> int:
        """Delete all technical skills for a CV."""
        try:
            count = self.db.query(TechnicalSkill).filter(TechnicalSkill.cv_id == cv_id).delete()
            self.db.commit()
            logger.info(f"Deleted {count} technical skills for CV: {cv_id}")
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting technical skills for CV {cv_id}: {str(e)}")
            raise


class SoftSkillRepository(BaseRepository[SoftSkill]):
    """Repository for Soft Skill operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, SoftSkill)

    def create_soft_skill(self, data: Dict[str, Any]) -> SoftSkill:
        """Create a soft skill."""
        try:
            skill = self.create(data)
            logger.info(f"Successfully created soft skill: {skill.skill_name} for CV: {skill.cv_id}")
            return skill
        except SQLAlchemyError as e:
            logger.error(f"Soft skill creation failed: {str(e)}")
            raise

    def get_soft_skill_by_id(self, skill_id: int) -> Optional[SoftSkill]:
        """Get soft skill by ID."""
        try:
            return self.db.query(SoftSkill).filter(SoftSkill.id == skill_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting soft skill {skill_id}: {str(e)}")
            raise

    def get_soft_skills_by_cv_id(self, cv_id: str) -> List[SoftSkill]:
        """Get all soft skills for a CV."""
        try:
            skills = self.db.query(SoftSkill).filter(SoftSkill.cv_id == cv_id).all()
            logger.debug(f"Found {len(skills)} soft skills for CV: {cv_id}")
            return skills
        except SQLAlchemyError as e:
            logger.error(f"Error getting soft skills for CV {cv_id}: {str(e)}")
            raise

    def update_soft_skill(self, skill_id: int, data: Dict[str, Any]) -> Optional[SoftSkill]:
        """Update soft skill by ID."""
        try:
            skill = self.get_soft_skill_by_id(skill_id)
            if not skill:
                return None

            for field, value in data.items():
                if hasattr(skill, field) and value is not None:
                    setattr(skill, field, value)

            self.db.commit()
            self.db.refresh(skill)
            logger.info(f"Successfully updated soft skill: {skill_id}")
            return skill
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating soft skill {skill_id}: {str(e)}")
            raise

    def delete_soft_skill(self, skill_id: int) -> bool:
        """Delete soft skill by ID."""
        try:
            skill = self.get_soft_skill_by_id(skill_id)
            if not skill:
                return False

            self.db.delete(skill)
            self.db.commit()
            logger.info(f"Successfully deleted soft skill: {skill_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting soft skill {skill_id}: {str(e)}")
            raise

    def delete_soft_skills_by_cv_id(self, cv_id: str) -> int:
        """Delete all soft skills for a CV."""
        try:
            count = self.db.query(SoftSkill).filter(SoftSkill.cv_id == cv_id).delete()
            self.db.commit()
            logger.info(f"Deleted {count} soft skills for CV: {cv_id}")
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting soft skills for CV {cv_id}: {str(e)}")
            raise


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def create_project(self, data: Dict[str, Any]) -> Project:
        """Create a project."""
        try:
            project = self.create(data)
            logger.info(f"Successfully created project: {project.project_name} for CV: {project.cv_id}")
            return project
        except SQLAlchemyError as e:
            logger.error(f"Project creation failed: {str(e)}")
            raise

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        try:
            return self.db.query(Project).filter(Project.id == project_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting project {project_id}: {str(e)}")
            raise

    def get_projects_by_cv_id(self, cv_id: str) -> List[Project]:
        """Get all projects for a CV."""
        try:
            projects = self.db.query(Project).filter(Project.cv_id == cv_id).all()
            logger.debug(f"Found {len(projects)} projects for CV: {cv_id}")
            return projects
        except SQLAlchemyError as e:
            logger.error(f"Error getting projects for CV {cv_id}: {str(e)}")
            raise

    def update_project(self, project_id: int, data: Dict[str, Any]) -> Optional[Project]:
        """Update project by ID."""
        try:
            project = self.get_project_by_id(project_id)
            if not project:
                return None

            for field, value in data.items():
                if hasattr(project, field) and value is not None:
                    setattr(project, field, value)

            self.db.commit()
            self.db.refresh(project)
            logger.info(f"Successfully updated project: {project_id}")
            return project
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating project {project_id}: {str(e)}")
            raise

    def delete_project(self, project_id: int) -> bool:
        """Delete project by ID."""
        try:
            project = self.get_project_by_id(project_id)
            if not project:
                return False

            self.db.delete(project)
            self.db.commit()
            logger.info(f"Successfully deleted project: {project_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting project {project_id}: {str(e)}")
            raise

    def delete_projects_by_cv_id(self, cv_id: str) -> int:
        """Delete all projects for a CV."""
        try:
            count = self.db.query(Project).filter(Project.cv_id == cv_id).delete()
            self.db.commit()
            logger.info(f"Deleted {count} projects for CV: {cv_id}")
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting projects for CV {cv_id}: {str(e)}")
            raise


# Helper class for bulk operations across all CV-related repositories
class CVRelatedBulkOperations:
    """Helper class for bulk operations across all CV-related repositories."""
    
    def __init__(self, db: Session):
        self.db = db
        self.language_repo = LanguageRepository(db)
        self.tech_skill_repo = TechnicalSkillRepository(db)
        self.soft_skill_repo = SoftSkillRepository(db)
        self.project_repo = ProjectRepository(db)
    
    def get_all_cv_components(self, cv_id: str) -> Dict[str, List]:
        """Get all components for a CV."""
        try:
            return {
                'languages': self.language_repo.get_languages_by_cv_id(cv_id),
                'technical_skills': self.tech_skill_repo.get_skills_by_cv_id(cv_id),
                'soft_skills': self.soft_skill_repo.get_soft_skills_by_cv_id(cv_id),
                'projects': self.project_repo.get_projects_by_cv_id(cv_id)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting CV components for {cv_id}: {str(e)}")
            raise

    def delete_all_cv_components(self, cv_id: str) -> Dict[str, int]:
        """Delete all components for a CV."""
        try:
            deleted_counts = {}
            deleted_counts['languages'] = self.language_repo.delete_languages_by_cv_id(cv_id)
            deleted_counts['technical_skills'] = self.tech_skill_repo.delete_skills_by_cv_id(cv_id)
            deleted_counts['soft_skills'] = self.soft_skill_repo.delete_soft_skills_by_cv_id(cv_id)
            deleted_counts['projects'] = self.project_repo.delete_projects_by_cv_id(cv_id)
            
            logger.info(f"Deleted all components for CV {cv_id}: {deleted_counts}")
            return deleted_counts
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting CV components for {cv_id}: {str(e)}")
            raise

    def bulk_create_cv_components(self, cv_id: str, components: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List]:
        """Bulk create all CV components."""
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
                    results['languages'].append(self.language_repo.create_language(lang_data))
            
            if 'technical_skills' in components:
                for skill_data in components['technical_skills']:
                    skill_data['cv_id'] = cv_id
                    results['technical_skills'].append(self.tech_skill_repo.create_skill(skill_data))
            
            if 'soft_skills' in components:
                for skill_data in components['soft_skills']:
                    skill_data['cv_id'] = cv_id
                    results['soft_skills'].append(self.soft_skill_repo.create_soft_skill(skill_data))
            
            if 'projects' in components:
                for proj_data in components['projects']:
                    proj_data['cv_id'] = cv_id
                    results['projects'].append(self.project_repo.create_project(proj_data))
            
            logger.info(f"Successfully bulk created CV components for CV: {cv_id}")
            return results
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Bulk CV components creation failed for CV {cv_id}: {str(e)}")
            raise
