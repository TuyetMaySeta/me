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
            languages = self.cv_related_service
