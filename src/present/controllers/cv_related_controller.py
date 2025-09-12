import logging
from src.core.services.cv_related_service import CVRelatedService
from src.present.request.cv_related import (
    LanguageCreateRequest, LanguageResponse,
    TechnicalSkillCreateRequest, TechnicalSkillResponse,
    SoftSkillCreateRequest, SoftSkillResponse,
    ProjectCreateRequest, ProjectResponse
)

logger = logging.getLogger(__name__)


class CVRelatedController:
    """Controller for CV related entities (Languages, Skills, Projects)"""
    
    def __init__(self, cv_related_service: CVRelatedService):
        self.cv_related_service = cv_related_service
    
    # Language operations
    def create_language(self, request: LanguageCreateRequest) -> LanguageResponse:
        """Create a new language"""
        logger.info(f"Creating language: {request.language_name} for CV: {request.cv_id}")
        language = self.cv_related_service.create_language(request)
        logger.info(f"Language created successfully: {language.language_name} (ID: {language.id})")
        return language
    
    # Technical Skill operations
    def create_technical_skill(self, request: TechnicalSkillCreateRequest) -> TechnicalSkillResponse:
        """Create a new technical skill"""
        logger.info(f"Creating technical skill: {request.skill_name} for CV: {request.cv_id}")
        skill = self.cv_related_service.create_technical_skill(request)
        logger.info(f"Technical skill created successfully: {skill.skill_name} (ID: {skill.id})")
        return skill
    
    # Soft Skill operations
    def create_soft_skill(self, request: SoftSkillCreateRequest) -> SoftSkillResponse:
        """Create a new soft skill"""
        logger.info(f"Creating soft skill: {request.skill_name} for CV: {request.cv_id}")
        skill = self.cv_related_service.create_soft_skill(request)
        logger.info(f"Soft skill created successfully: {skill.skill_name} (ID: {skill.id})")
        return skill
    
    # Project operations
    def create_project(self, request: ProjectCreateRequest) -> ProjectResponse:
        """Create a new project"""
        logger.info(f"Creating project: {request.project_name} for CV: {request.cv_id}")
        project = self.cv_related_service.create_project(request)
        logger.info(f"Project created successfully: {project.project_name} (ID: {project.id})")
        return project