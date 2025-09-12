# src/present/controllers/cv_controller.py
from typing import List, Optional, Dict, Any
import logging
from src.core.services.cv_service import CVService
from src.present.request.cv import CVCreate, CVUpdate, CV, CVWithDetails, CVBulkCreate, CVBulkResponse

logger = logging.getLogger(__name__)


class CVController:
    """CV controller - handles HTTP requests and responses for CV operations"""
    
    def __init__(self, cv_service: CVService):
        self.cv_service = cv_service
    
    def create_cv(self, cv_create: CVCreate) -> CV:
        """Create a new CV"""
        logger.info(f"Creating CV: {cv_create.email}")
        cv = self.cv_service.create_cv(cv_create)
        logger.info(f"CV created successfully: {cv.email} (ID: {cv.id})")
        return cv
    
    def get_cvs(self, skip: int = 0, limit: int = 100) -> List[CV]:
        """Get all CVs with pagination"""
        logger.info(f"Getting CVs: skip={skip}, limit={limit}")
        return self.cv_service.get_cvs(skip, limit)
    
    def get_cv(self, cv_id: str) -> CV:
        """Get a specific CV by ID"""
        logger.info(f"Getting CV: {cv_id}")
        return self.cv_service.get_cv(cv_id)
    
    def get_cv_with_details(self, cv_id: str) -> CVWithDetails:
        """Get CV with all related details"""
        logger.info(f"Getting CV with details: {cv_id}")
        return self.cv_service.get_cv_with_details(cv_id)
    
    def update_cv(self, cv_id: str, cv_update: CVUpdate) -> CV:
        """Update a CV"""
        logger.info(f"Updating CV: {cv_id}")
        return self.cv_service.update_cv(cv_id, cv_update)
    
    def delete_cv(self, cv_id: str) -> Dict[str, str]:
        """Delete a CV"""
        logger.info(f"Deleting CV: {cv_id}")
        self.cv_service.delete_cv(cv_id)
        return {"message": f"CV {cv_id} deleted successfully"}
    
    def bulk_create_cvs(self, bulk_request: CVBulkCreate) -> CVBulkResponse:
        """Bulk create multiple CVs"""
        logger.info(f"Bulk creating {len(bulk_request.cvs)} CVs")
        result = self.cv_service.bulk_create_cvs(bulk_request.cvs)
        
        return CVBulkResponse(
            created_count=result["created_count"],
            created_cvs=result["created_cvs"],
            errors=result["errors"]
        )
    
    def search_cvs(self, 
                   email: Optional[str] = None,
                   seta_id: Optional[str] = None,
                   position: Optional[str] = None,
                   skill: Optional[str] = None,
                   skip: int = 0,
                   limit: int = 100) -> List[CV]:
        """Search CVs by various criteria"""
        logger.info(f"Searching CVs with filters: email={email}, seta_id={seta_id}, position={position}, skill={skill}")
        return self.cv_service.search_cvs(
            email=email,
            seta_id=seta_id,
            position=position,
            skill=skill,
            skip=skip,
            limit=limit
        )
    
    def get_cv_by_email(self, email: str) -> CV:
        """Get CV by email"""
        logger.info(f"Getting CV by email: {email}")
        cv = self.cv_service.get_cv_by_email(email)
        if not cv:
            from src.common.exception.exceptions import NotFoundException
            raise NotFoundException(f"CV with email {email} not found", "CV_NOT_FOUND")
        return cv
    
    def get_cv_by_seta_id(self, seta_id: str) -> CV:
        """Get CV by SETA ID"""
        logger.info(f"Getting CV by SETA ID: {seta_id}")
        cv = self.cv_service.get_cv_by_seta_id(seta_id)
        if not cv:
            from src.common.exception.exceptions import NotFoundException
            raise NotFoundException(f"CV with SETA ID {seta_id} not found", "CV_NOT_FOUND")
        return cv