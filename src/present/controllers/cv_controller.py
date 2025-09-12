from typing import List
import logging
from src.core.services.cv_service import CVService
from src.present.request.cv import CVCreate, CV

logger = logging.getLogger(__name__)


class CVController:
    """CV controller - handles HTTP requests for CV operations"""
    
    def __init__(self, cv_service: CVService):
        self.cv_service = cv_service
    
    def create_cv(self, cv_create: CVCreate) -> CV:
        """Create a new CV"""
        logger.info(f"Creating CV: {cv_create.email}")
        cv = self.cv_service.create_cv(cv_create)
        logger.info(f"CV created successfully: {cv.email} (ID: {cv.id})")
        return cv
    
    def get_cvs(self, page: int = 1, page_size: int = 10) -> List[CV]:
        """Get all CVs with pagination (page & page_size)"""
        logger.info(f"Getting CVs: page={page}, page_size={page_size}")
        cvs = self.cv_service.get_cvs(page, page_size)
        return [CV.model_validate(cv) for cv in cvs]



