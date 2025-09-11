from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import re

from .base_repository import BaseRepository
from src.core.models.cv import Language, TechnicalSkill, SoftSkill, Project

logger = logging.getLogger(__name__)


class LanguageRepository(BaseRepository[Language]):
    """Repository for Language operations with validation."""
    
    def __init__(self, db: Session):
        super().__init__(db, Language)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate language data."""
        errors = {}
        
        # CV ID validation
        cv_id = data.get("cv_id")
        if not cv_id or len(str(cv_id)) != 6:
            errors["cv_id"] = ["CV ID must be exactly 6 characters"]
        
        # Language name validation
        language_name = data.get("language_name")
        if not language_name:
            errors["language_name"] = ["Language name is required"]
        elif len(language_name) > 100:
            errors["language_name"] = ["Language name must not exceed 100 characters"]
        
        # Proficiency validation (optional but if provided must be valid)
        proficiency = data.get("proficiency")
        if proficiency and proficiency not in ["Native", "Fluent", "Intermediate", "Basic"]:
            errors["proficiency"] = ["Proficiency must be one of: Native, Fluent, Intermediate, Basic"]
        
        # Description validation (optional)
        description = data.get("description")
        if description and len(description) > 1000:
            errors["description"] = ["Description must not exceed 1000 characters"]
        
        return errors

    def create_language(self, data: Dict[str, Any]) -> Language:
        """Create a language with validation."""
        try:
            errors = self.validate(data)
            if errors:
                error_msg = f"Language validation failed: {errors}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            language = self.create(data)
            logger.info(f"Successfully created language: {language.language_name} for CV: {language.cv_id}")
            return language
            
        except ValueError:
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Language creation failed - integrity error: {str(e)}")
            raise ValueError(f"Language creation failed: CV ID {data.get('cv_id')} may not exist")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Language creation failed - database error: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")


class TechnicalSkillRepository(BaseRepository[TechnicalSkill]):
    """Repository for Technical Skill operations with validation."""
    
    def __init__(self, db: Session):
        super().__init__(db, TechnicalSkill)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate technical skill data."""
        errors = {}
        
        # CV ID validation
        cv_id = data.get("cv_id")
        if not cv_id or len(str(cv_id)) != 6:
            errors["cv_id"] = ["CV ID must be exactly 6 characters"]
        
        # Skill name validation
        skill_name = data.get("skill_name")
        if not skill_name:
            errors["skill_name"] = ["Skill name is required"]
        elif len(skill_name) > 255:
            errors["skill_name"] = ["Skill name must not exceed 255 characters"]
        
        # Category validation (optional but if provided must be valid)
        category = data.get("category")
        valid_categories = ["Programming Language", "Database", "Framework", "Tool", "Hardware"]
        if category and category not in valid_categories:
            errors["category"] = [f"Category must be one of: {', '.join(valid_categories)}"]
        
        # Description validation (optional)
        description = data.get("description")
        if description and len(description) > 1000:
            errors["description"] = ["Description must not exceed 1000 characters"]
        
        return errors

    def create_skill(self, data: Dict[str, Any]) -> TechnicalSkill:
        """Create a technical skill with validation."""
        try:
            errors = self.validate(data)
            if errors:
                error_msg = f"Technical skill validation failed: {errors}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            skill = self.create(data)
            logger.info(f"Successfully created technical skill: {skill.skill_name} for CV: {skill.cv_id}")
            return skill
            
        except ValueError:
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Technical skill creation failed - integrity error: {str(e)}")
            raise ValueError(f"Technical skill creation failed: CV ID {data.get('cv_id')} may not exist")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Technical skill creation failed - database error: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")


class SoftSkillRepository(BaseRepository[SoftSkill]):
    """Repository for Soft Skill operations with validation."""
    
    def __init__(self, db: Session):
        super().__init__(db, SoftSkill)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate soft skill data."""
        errors = {}
        
        # CV ID validation
        cv_id = data.get("cv_id")
        if not cv_id or len(str(cv_id)) != 6:
            errors["cv_id"] = ["CV ID must be exactly 6 characters"]
        
        # Skill name validation
        skill_name = data.get("skill_name")
        valid_skills = [
            "Communication", "Teamwork", "Problem Solving", "Decision Making",
            "Leadership", "Time Management", "Adaptability", "Other"
        ]
        if not skill_name:
            errors["skill_name"] = ["Skill name is required"]
        elif skill_name not in valid_skills:
            errors["skill_name"] = [f"Skill name must be one of: {', '.join(valid_skills)}"]
        
        # Description validation (optional)
        description = data.get("description")
        if description and len(description) > 1000:
            errors["description"] = ["Description must not exceed 1000 characters"]
        
        return errors

    def create_soft_skill(self, data: Dict[str, Any]) -> SoftSkill:
        """Create a soft skill with validation."""
        try:
            errors = self.validate(data)
            if errors:
                error_msg = f"Soft skill validation failed: {errors}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            skill = self.create(data)
            logger.info(f"Successfully created soft skill: {skill.skill_name} for CV: {skill.cv_id}")
            return skill
            
        except ValueError:
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Soft skill creation failed - integrity error: {str(e)}")
            raise ValueError(f"Soft skill creation failed: CV ID {data.get('cv_id')} may not exist")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Soft skill creation failed - database error: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project operations with validation."""
    
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate project data."""
        errors = {}
        
        # CV ID validation
        cv_id = data.get("cv_id")
        if not cv_id or len(str(cv_id)) != 6:
            errors["cv_id"] = ["CV ID must be exactly 6 characters"]
        
        # Project name validation
        project_name = data.get("project_name")
        if not project_name:
            errors["project_name"] = ["Project name is required"]
        elif len(project_name) > 255:
            errors["project_name"] = ["Project name must not exceed 255 characters"]
        
        # Project description validation (optional)
        project_description = data.get("project_description")
        if project_description and len(project_description) > 2000:
            errors["project_description"] = ["Project description must not exceed 2000 characters"]
        
        # Position validation (optional)
        position = data.get("position")
        if position and len(position) > 255:
            errors["position"] = ["Position must not exceed 255 characters"]
        
        # Responsibilities validation (optional)
        responsibilities = data.get("responsibilities")
        if responsibilities and len(responsibilities) > 2000:
            errors["responsibilities"] = ["Responsibilities must not exceed 2000 characters"]
        
        # Programming languages validation (optional)
        programming_languages = data.get("programming_languages")
        if programming_languages and len(programming_languages) > 500:
            errors["programming_languages"] = ["Programming languages must not exceed 500 characters"]
        
        return errors

    def create_project(self, data: Dict[str, Any]) -> Project:
        """Create a project with validation."""
        try:
            errors = self.validate(data)
            if errors:
                error_msg = f"Project validation failed: {errors}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            project = self.create(data)
            logger.info(f"Successfully created project: {project.project_name} for CV: {project.cv_id}")
            return project
            
        except ValueError:
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Project creation failed - integrity error: {str(e)}")
            raise ValueError(f"Project creation failed: CV ID {data.get('cv_id')} may not exist")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Project creation failed - database error: {str(e)}")
            raise ValueError(f"Database error: {str(e)}")


# Bulk operations for all repositories
class CVRelatedBulkOperations:
    """Helper class for bulk operations across all CV-related repositories."""
    
    def __init__(self, db: Session):
        self.db = db
        self.language_repo = LanguageRepository(db)
        self.tech_skill_repo = TechnicalSkillRepository(db)
        self.soft_skill_repo = SoftSkillRepository(db)
        self.project_repo = ProjectRepository(db)
    
    def bulk_create_cv_components(self, cv_id: str, components: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List]:
        """
        Bulk create all CV components (languages, skills, projects) for a CV.
        
        Args:
            cv_id: The CV ID to create components for
            components: Dictionary with keys 'languages', 'technical_skills', 'soft_skills', 'projects'
        
        Returns:
            Dictionary with created entities for each component type
        """
        results = {
            'languages': [],
            'technical_skills': [],
            'soft_skills': [],
            'projects': []
        }
        
        try:
            # Add cv_id to all component data
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
    
    def validate_all_components(self, components: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, List[str]]]:
        """
        Validate all CV components before creation.
        
        Args:
            components: Dictionary with component data
            
        Returns:
            Dictionary with validation errors for each component type
        """
        all_errors = {}
        
        # Validate languages
        if 'languages' in components:
            lang_errors = {}
            for i, lang_data in enumerate(components['languages']):
                errors = self.language_repo.validate(lang_data)
                if errors:
                    lang_errors[f"language_{i+1}"] = errors
            if lang_errors:
                all_errors['languages'] = lang_errors
        
        # Validate technical skills
        if 'technical_skills' in components:
            tech_errors = {}
            for i, skill_data in enumerate(components['technical_skills']):
                errors = self.tech_skill_repo.validate(skill_data)
                if errors:
                    tech_errors[f"technical_skill_{i+1}"] = errors
            if tech_errors:
                all_errors['technical_skills'] = tech_errors
        
        # Validate soft skills
        if 'soft_skills' in components:
            soft_errors = {}
            for i, skill_data in enumerate(components['soft_skills']):
                errors = self.soft_skill_repo.validate(skill_data)
                if errors:
                    soft_errors[f"soft_skill_{i+1}"] = errors
            if soft_errors:
                all_errors['soft_skills'] = soft_errors
        
        # Validate projects
        if 'projects' in components:
            proj_errors = {}
            for i, proj_data in enumerate(components['projects']):
                errors = self.project_repo.validate(proj_data)
                if errors:
                    proj_errors[f"project_{i+1}"] = errors
            if proj_errors:
                all_errors['projects'] = proj_errors
        
        return all_errors