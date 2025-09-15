# src/repository/employee_related_repository.py
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from src.core.models.employee import EmployeeLanguage, EmployeeTechnicalSkill, EmployeeSoftSkill, EmployeeProject

logger = logging.getLogger(__name__)


class EmployeeLanguageRepository(BaseRepository[EmployeeLanguage]):
    """Repository for Employee Language operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, EmployeeLanguage)

    def create_language(self, data: Dict[str, Any]) -> EmployeeLanguage:
        """Create an employee language."""
        try:
            language = self.create(data)
            logger.info(f"Successfully created language: {language.language_name} for Employee: {language.employee_id}")
            return language
        except SQLAlchemyError as e:
            logger.error(f"Language creation failed: {str(e)}")
            raise

    def get_language_by_id(self, lang_id: int) -> Optional[EmployeeLanguage]:
        """Get language by ID."""
        try:
            return self.db.query(EmployeeLanguage).filter(EmployeeLanguage.id == lang_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting language {lang_id}: {str(e)}")
            raise

    def get_languages_by_employee_id(self, employee_id: str) -> List[EmployeeLanguage]:
        """Get all languages for an employee."""
        try:
            languages = self.db.query(EmployeeLanguage).filter(EmployeeLanguage.employee_id == employee_id).all()
            logger.debug(f"Found {len(languages)} languages for Employee: {employee_id}")
            return languages
        except SQLAlchemyError as e:
            logger.error(f"Error getting languages for Employee {employee_id}: {str(e)}")
            raise

    def update_language(self, lang_id: int, data: Dict[str, Any]) -> Optional[EmployeeLanguage]:
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

    def delete_languages_by_employee_id(self, employee_id: str) -> int:
        """Delete all languages for an employee."""
        try:
            count = self.db.query(EmployeeLanguage).filter(EmployeeLanguage.employee_id == employee_id).delete()
            self.db.commit()
            logger.info(f"Deleted {count} languages for Employee: {employee_id}")
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting languages for Employee {employee_id}: {str(e)}")
            raise


class EmployeeTechnicalSkillRepository(BaseRepository[EmployeeTechnicalSkill]):
    """Repository for Employee Technical Skill operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, EmployeeTechnicalSkill)

    def create_skill(self, data: Dict[str, Any]) -> EmployeeTechnicalSkill:
        """Create an employee technical skill."""
        try:
            skill = self.create(data)
            logger.info(f"Successfully created technical skill: {skill.skill_name} for Employee: {skill.employee_id}")
            return skill
        except SQLAlchemyError as e:
            logger.error(f"Technical skill creation failed: {str(e)}")
            raise

    def get_skill_by_id(self, skill_id: int) -> Optional[EmployeeTechnicalSkill]:
        """Get technical skill by ID."""
        try:
            return self.db.query(EmployeeTechnicalSkill).filter(EmployeeTechnicalSkill.id == skill_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting technical skill {skill_id}: {str(e)}")
            raise

    def get_skills_by_employee_id(self, employee_id: str) -> List[EmployeeTechnicalSkill]:
        """Get all technical skills for an employee."""
        try:
            skills = self.db.query(EmployeeTechnicalSkill).filter(EmployeeTechnicalSkill.employee_id == employee_id).all()
            logger.debug(f"Found {len(skills)} technical skills for Employee: {employee_id}")
            return skills
        except SQLAlchemyError as e:
            logger.error(f"Error getting technical skills for Employee {employee_id}: {str(e)}")
            raise

    def update_skill(self, skill_id: int, data: Dict[str, Any]) -> Optional[EmployeeTechnicalSkill]:
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

    def delete_skills_by_employee_id(self, employee_id: str) -> int:
        """Delete all technical skills for an employee."""
        try:
            count = self.db.query(EmployeeTechnicalSkill).filter(EmployeeTechnicalSkill.employee_id == employee_id).delete()
            self.db.commit()
            logger.info(f"Deleted {count} technical skills for Employee: {employee_id}")
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting technical skills for Employee {employee_id}: {str(e)}")
            raise


class EmployeeSoftSkillRepository(BaseRepository[EmployeeSoftSkill]):
    """Repository for Employee Soft Skill operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, EmployeeSoftSkill)

    def create_soft_skill(self, data: Dict[str, Any]) -> EmployeeSoftSkill:
        """Create an employee soft skill."""
        try:
            skill = self.create(data)
            logger.info(f"Successfully created soft skill: {skill.skill_name} for Employee: {skill.employee_id}")
            return skill
        except SQLAlchemyError as e:
            logger.error(f"Soft skill creation failed: {str(e)}")
            raise

    def get_soft_skill_by_id(self, skill_id: int) -> Optional[EmployeeSoftSkill]:
        """Get soft skill by ID."""
        try:
            return self.db.query(EmployeeSoftSkill).filter(EmployeeSoftSkill.id == skill_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting soft skill {skill_id}: {str(e)}")
            raise

    def get_soft_skills_by_employee_id(self, employee_id: str) -> List[EmployeeSoftSkill]:
        """Get all soft skills for an employee."""
        try:
            skills = self.db.query(EmployeeSoftSkill).filter(EmployeeSoftSkill.employee_id == employee_id).all()
            logger.debug(f"Found {len(skills)} soft skills for Employee: {employee_id}")
            return skills
        except SQLAlchemyError as e:
            logger.error(f"Error getting soft skills for Employee {employee_id}: {str(e)}")
            raise

    def update_soft_skill(self, skill_id: int, data: Dict[str, Any]) -> Optional[EmployeeSoftSkill]:
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

    def delete_soft_skills_by_employee_id(self, employee_id: str) -> int:
        """Delete all soft skills for an employee."""
        try:
            count = self.db.query(EmployeeSoftSkill).filter(EmployeeSoftSkill.employee_id == employee_id).delete()
            self.db.commit()
            logger.info(f"Deleted {count} soft skills for Employee: {employee_id}")
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting soft skills for Employee {employee_id}: {str(e)}")
            raise


class EmployeeProjectRepository(BaseRepository[EmployeeProject]):
    """Repository for Employee Project operations."""
    
    def __init__(self, db: Session):
        super().__init__(db, EmployeeProject)

    def create_project(self, data: Dict[str, Any]) -> EmployeeProject:
        """Create an employee project."""
        try:
            project = self.create(data)
            logger.info(f"Successfully created project: {project.project_name} for Employee: {project.employee_id}")
            return project
        except SQLAlchemyError as e:
            logger.error(f"Project creation failed: {str(e)}")
            raise

    def get_project_by_id(self, project_id: int) -> Optional[EmployeeProject]:
        """Get project by ID."""
        try:
            return self.db.query(EmployeeProject).filter(EmployeeProject.id == project_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting project {project_id}: {str(e)}")
            raise

    def get_projects_by_employee_id(self, employee_id: str) -> List[EmployeeProject]:
        """Get all projects for an employee."""
        try:
            projects = self.db.query(EmployeeProject).filter(EmployeeProject.employee_id == employee_id).all()
            logger.debug(f"Found {len(projects)} projects for Employee: {employee_id}")
            return projects
        except SQLAlchemyError as e:
            logger.error(f"Error getting projects for Employee {employee_id}: {str(e)}")
            raise

    def update_project(self, project_id: int, data: Dict[str, Any]) -> Optional[EmployeeProject]:
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

    def delete_projects_by_employee_id(self, employee_id: str) -> int:
        """Delete all projects for an employee."""
        try:
            count = self.db.query(EmployeeProject).filter(EmployeeProject.employee_id == employee_id).delete()
            self.db.commit()
            logger.info(f"Deleted {count} projects for Employee: {employee_id}")
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting projects for Employee {employee_id}: {str(e)}")
            raise


# Helper class for bulk operations across all Employee-related repositories
class EmployeeRelatedBulkOperations:
    """Helper class for bulk operations across all Employee-related repositories."""
    
    def __init__(self, db: Session):
        self.db = db
        self.language_repo = EmployeeLanguageRepository(db)
        self.tech_skill_repo = EmployeeTechnicalSkillRepository(db)
        self.soft_skill_repo = EmployeeSoftSkillRepository(db)
        self.project_repo = EmployeeProjectRepository(db)
    
    def get_all_employee_components(self, employee_id: str) -> Dict[str, List]:
        """Get all components for an employee."""
        try:
            return {
                'languages': self.language_repo.get_languages_by_employee_id(employee_id),
                'technical_skills': self.tech_skill_repo.get_skills_by_employee_id(employee_id),
                'soft_skills': self.soft_skill_repo.get_soft_skills_by_employee_id(employee_id),
                'projects': self.project_repo.get_projects_by_employee_id(employee_id)
            }
        except SQLAlchemyError as e:
            logger.error(f"Error getting Employee components for {employee_id}: {str(e)}")
            raise

    def delete_all_employee_components(self, employee_id: str) -> Dict[str, int]:
        """Delete all components for an employee."""
        try:
            deleted_counts = {}
            deleted_counts['languages'] = self.language_repo.delete_languages_by_employee_id(employee_id)
            deleted_counts['technical_skills'] = self.tech_skill_repo.delete_skills_by_employee_id(employee_id)
            deleted_counts['soft_skills'] = self.soft_skill_repo.delete_soft_skills_by_employee_id(employee_id)
            deleted_counts['projects'] = self.project_repo.delete_projects_by_employee_id(employee_id)
            
            logger.info(f"Deleted all components for Employee {employee_id}: {deleted_counts}")
            return deleted_counts
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting Employee components for {employee_id}: {str(e)}")
            raise

    def bulk_create_employee_components(self, employee_id: str, components: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List]:
        """Bulk create all Employee components."""
        results = {
            'languages': [],
            'technical_skills': [],
            'soft_skills': [],
            'projects': []
        }
        
        try:
            if 'languages' in components:
                for lang_data in components['languages']:
                    lang_data['employee_id'] = employee_id
                    results['languages'].append(self.language_repo.create_language(lang_data))
            
            if 'technical_skills' in components:
                for skill_data in components['technical_skills']:
                    skill_data['employee_id'] = employee_id
                    results['technical_skills'].append(self.tech_skill_repo.create_skill(skill_data))
            
            if 'soft_skills' in components:
                for skill_data in components['soft_skills']:
                    skill_data['employee_id'] = employee_id
                    results['soft_skills'].append(self.soft_skill_repo.create_soft_skill(skill_data))
            
            if 'projects' in components:
                for proj_data in components['projects']:
                    proj_data['employee_id'] = employee_id
                    results['projects'].append(self.project_repo.create_project(proj_data))
            
            logger.info(f"Successfully bulk created Employee components for Employee: {employee_id}")
            return results
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Bulk Employee components creation failed for Employee {employee_id}: {str(e)}")
            raise