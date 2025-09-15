# src/present/controllers/cv_related_controller.py
import logging
from typing import List, Dict

from src.core.services.cv_related_service import CVRelatedService
from src.present.request.cv_related import (
    LanguageCreateRequest, LanguageUpdateRequest, LanguageResponse,
    TechnicalSkillCreateRequest, TechnicalSkillUpdateRequest, TechnicalSkillResponse,
    SoftSkillCreateRequest, SoftSkillUpdateRequest, SoftSkillResponse,
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse,
    BulkComponentCreateRequest, BulkComponentResponse
)

logger = logging.getLogger(__name__)


class CVRelatedController:
    """Controller for CV related entities (Languages, Skills, Projects)"""
    
    def __init__(self, cv_related_service: CVRelatedService):
        self.cv_related_service = cv_related_service

    # ===================== LANGUAGE OPERATIONS =====================
    
    def create_language(self, request: LanguageCreateRequest) -> LanguageResponse:
        """Create a new language"""
        logger.info(f"Controller: Creating language {request.language_name} for CV {request.cv_id}")
        
        try:
            language = self.cv_related_service.create_language(request)
            logger.info(f"Controller: Language created successfully - {language.language_name} (ID: {language.id})")
            return language
        except Exception as e:
            logger.error(f"Controller: Language creation failed: {str(e)}")
            raise

    def get_language(self, lang_id: int) -> LanguageResponse:
        """Get language by ID"""
        logger.info(f"Controller: Getting language {lang_id}")
        
        try:
            language = self.cv_related_service.get_language(lang_id)
            logger.info(f"Controller: Retrieved language {lang_id}")
            return language
        except Exception as e:
            logger.error(f"Controller: Failed to get language {lang_id}: {str(e)}")
            raise

    def get_languages_by_cv(self, cv_id: str) -> List[LanguageResponse]:
        """Get all languages for a CV"""
        logger.info(f"Controller: Getting languages for CV {cv_id}")
        
        try:
            languages = self.cv_related_service.get_languages_by_cv(cv_id)
            logger.info(f"Controller: Retrieved {len(languages)} languages for CV {cv_id}")
            return languages
        except Exception as e:
            logger.error(f"Controller: Failed to get languages for CV {cv_id}: {str(e)}")
            raise

    def update_language(self, lang_id: int, request: LanguageUpdateRequest) -> LanguageResponse:
        """Update language"""
        logger.info(f"Controller: Updating language {lang_id}")
        
        try:
            language = self.cv_related_service.update_language(lang_id, request)
            logger.info(f"Controller: Language updated successfully {lang_id}")
            return language
        except Exception as e:
            logger.error(f"Controller: Failed to update language {lang_id}: {str(e)}")
            raise

    def delete_language(self, lang_id: int) -> Dict[str, str]:
        """Delete language"""
        logger.info(f"Controller: Deleting language {lang_id}")
        
        try:
            self.cv_related_service.delete_language(lang_id)
            logger.info(f"Controller: Language deleted successfully {lang_id}")
            return {"message": f"Language {lang_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete language {lang_id}: {str(e)}")
            raise

    # ===================== TECHNICAL SKILL OPERATIONS =====================
    
    def create_technical_skill(self, request: TechnicalSkillCreateRequest) -> TechnicalSkillResponse:
        """Create a new technical skill"""
        logger.info(f"Controller: Creating technical skill {request.skill_name} for CV {request.cv_id}")
        
        try:
            skill = self.cv_related_service.create_technical_skill(request)
            logger.info(f"Controller: Technical skill created successfully - {skill.skill_name} (ID: {skill.id})")
            return skill
        except Exception as e:
            logger.error(f"Controller: Technical skill creation failed: {str(e)}")
            raise

    def get_technical_skill(self, skill_id: int) -> TechnicalSkillResponse:
        """Get technical skill by ID"""
        logger.info(f"Controller: Getting technical skill {skill_id}")
        
        try:
            skill = self.cv_related_service.get_technical_skill(skill_id)
            logger.info(f"Controller: Retrieved technical skill {skill_id}")
            return skill
        except Exception as e:
            logger.error(f"Controller: Failed to get technical skill {skill_id}: {str(e)}")
            raise

    def get_technical_skills_by_cv(self, cv_id: str) -> List[TechnicalSkillResponse]:
        """Get all technical skills for a CV"""
        logger.info(f"Controller: Getting technical skills for CV {cv_id}")
        
        try:
            skills = self.cv_related_service.get_technical_skills_by_cv(cv_id)
            logger.info(f"Controller: Retrieved {len(skills)} technical skills for CV {cv_id}")
            return skills
        except Exception as e:
            logger.error(f"Controller: Failed to get technical skills for CV {cv_id}: {str(e)}")
            raise

    def update_technical_skill(self, skill_id: int, request: TechnicalSkillUpdateRequest) -> TechnicalSkillResponse:
        """Update technical skill"""
        logger.info(f"Controller: Updating technical skill {skill_id}")
        
        try:
            skill = self.cv_related_service.update_technical_skill(skill_id, request)
            logger.info(f"Controller: Technical skill updated successfully {skill_id}")
            return skill
        except Exception as e:
            logger.error(f"Controller: Failed to update technical skill {skill_id}: {str(e)}")
            raise

    def delete_technical_skill(self, skill_id: int) -> Dict[str, str]:
        """Delete technical skill"""
        logger.info(f"Controller: Deleting technical skill {skill_id}")
        
        try:
            self.cv_related_service.delete_technical_skill(skill_id)
            logger.info(f"Controller: Technical skill deleted successfully {skill_id}")
            return {"message": f"Technical skill {skill_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete technical skill {skill_id}: {str(e)}")
            raise

    # ===================== SOFT SKILL OPERATIONS =====================
    
    def create_soft_skill(self, request: SoftSkillCreateRequest) -> SoftSkillResponse:
        """Create a new soft skill"""
        logger.info(f"Controller: Creating soft skill {request.skill_name} for CV {request.cv_id}")
        
        try:
            skill = self.cv_related_service.create_soft_skill(request)
            logger.info(f"Controller: Soft skill created successfully - {skill.skill_name} (ID: {skill.id})")
            return skill
        except Exception as e:
            logger.error(f"Controller: Soft skill creation failed: {str(e)}")
            raise

    def get_soft_skill(self, skill_id: int) -> SoftSkillResponse:
        """Get soft skill by ID"""
        logger.info(f"Controller: Getting soft skill {skill_id}")
        
        try:
            skill = self.cv_related_service.get_soft_skill(skill_id)
            logger.info(f"Controller: Retrieved soft skill {skill_id}")
            return skill
        except Exception as e:
            logger.error(f"Controller: Failed to get soft skill {skill_id}: {str(e)}")
            raise

    def get_soft_skills_by_cv(self, cv_id: str) -> List[SoftSkillResponse]:
        """Get all soft skills for a CV"""
        logger.info(f"Controller: Getting soft skills for CV {cv_id}")
        
        try:
            skills = self.cv_related_service.get_soft_skills_by_cv(cv_id)
            logger.info(f"Controller: Retrieved {len(skills)} soft skills for CV {cv_id}")
            return skills
        except Exception as e:
            logger.error(f"Controller: Failed to get soft skills for CV {cv_id}: {str(e)}")
            raise

    def update_soft_skill(self, skill_id: int, request: SoftSkillUpdateRequest) -> SoftSkillResponse:
        """Update soft skill"""
        logger.info(f"Controller: Updating soft skill {skill_id}")
        
        try:
            skill = self.cv_related_service.update_soft_skill(skill_id, request)
            logger.info(f"Controller: Soft skill updated successfully {skill_id}")
            return skill
        except Exception as e:
            logger.error(f"Controller: Failed to update soft skill {skill_id}: {str(e)}")
            raise

    def delete_soft_skill(self, skill_id: int) -> Dict[str, str]:
        """Delete soft skill"""
        logger.info(f"Controller: Deleting soft skill {skill_id}")
        
        try:
            self.cv_related_service.delete_soft_skill(skill_id)
            logger.info(f"Controller: Soft skill deleted successfully {skill_id}")
            return {"message": f"Soft skill {skill_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete soft skill {skill_id}: {str(e)}")
            raise

    # ===================== PROJECT OPERATIONS =====================
    
    def create_project(self, request: ProjectCreateRequest) -> ProjectResponse:
        """Create a new project"""
        logger.info(f"Controller: Creating project {request.project_name} for CV {request.cv_id}")
        
        try:
            project = self.cv_related_service.create_project(request)
            logger.info(f"Controller: Project created successfully - {project.project_name} (ID: {project.id})")
            return project
        except Exception as e:
            logger.error(f"Controller: Project creation failed: {str(e)}")
            raise

    def get_project(self, project_id: int) -> ProjectResponse:
        """Get project by ID"""
        logger.info(f"Controller: Getting project {project_id}")
        
        try:
            project = self.cv_related_service.get_project(project_id)
            logger.info(f"Controller: Retrieved project {project_id}")
            return project
        except Exception as e:
            logger.error(f"Controller: Failed to get project {project_id}: {str(e)}")
            raise

    def get_projects_by_cv(self, cv_id: str) -> List[ProjectResponse]:
        """Get all projects for a CV"""
        logger.info(f"Controller: Getting projects for CV {cv_id}")
        
        try:
            projects = self.cv_related_service.get_projects_by_cv(cv_id)
            logger.info(f"Controller: Retrieved {len(projects)} projects for CV {cv_id}")
            return projects
        except Exception as e:
            logger.error(f"Controller: Failed to get projects for CV {cv_id}: {str(e)}")
            raise

    def update_project(self, project_id: int, request: ProjectUpdateRequest) -> ProjectResponse:
        """Update project"""
        logger.info(f"Controller: Updating project {project_id}")
        
        try:
            project = self.cv_related_service.update_project(project_id, request)
            logger.info(f"Controller: Project updated successfully {project_id}")
            return project
        except Exception as e:
            logger.error(f"Controller: Failed to update project {project_id}: {str(e)}")
            raise

    def delete_project(self, project_id: int) -> Dict[str, str]:
        """Delete project"""
        logger.info(f"Controller: Deleting project {project_id}")
        
        try:
            self.cv_related_service.delete_project(project_id)
            logger.info(f"Controller: Project deleted successfully {project_id}")
            return {"message": f"Project {project_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete project {project_id}: {str(e)}")
            raise

    # ===================== BULK OPERATIONS =====================
    
    def get_cv_components(self, cv_id: str) -> Dict[str, List]:
        """Get all components for a CV"""
        logger.info(f"Controller: Getting all components for CV {cv_id}")
        
        try:
            components = self.cv_related_service.get_cv_components(cv_id)
            logger.info(f"Controller: Retrieved all components for CV {cv_id}")
            return components
        except Exception as e:
            logger.error(f"Controller: Failed to get components for CV {cv_id}: {str(e)}")
            raise

    def bulk_create_components(self, request: BulkComponentCreateRequest) -> BulkComponentResponse:
        """Bulk create components for a CV"""
        logger.info(f"Controller: Bulk creating components for CV {request.cv_id}")
        
        try:
            result = self.cv_related_service.bulk_create_components(request)
            logger.info(f"Controller: Bulk component creation completed for CV {request.cv_id}")
            return result
        except Exception as e:
            logger.error(f"Controller: Bulk component creation failed for CV {request.cv_id}: {str(e)}")
            raise
