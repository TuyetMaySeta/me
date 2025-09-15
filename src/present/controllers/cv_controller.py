# src/present/controllers/cv_controller.py
import logging
from typing import List, Dict, Any

from src.core.services.cv_service import CVService
from src.present.request.cv import (
    CVCreate, CVUpdate, CV, CVWithDetails,
    CVBulkCreate, CVBulkResponse, CVSearchRequest, 
    CVPaginationResponse, CVComponentCreateRequest, CVComponentsResponse
)

logger = logging.getLogger(__name__)


class CVController:
    """CV controller - handles HTTP requests for CV operations"""
    
    def __init__(self, cv_service: CVService):
        self.cv_service = cv_service
    
    def create_cv(self, cv_create: CVCreate) -> CV:
        """Create a new CV"""
        logger.info(f"Controller: Creating CV for {cv_create.email}")
        
        try:
            cv = self.cv_service.create_cv(cv_create)
            logger.info(f"Controller: CV created successfully - {cv.email} (ID: {cv.id})")
            return cv
        except Exception as e:
            logger.error(f"Controller: CV creation failed for {cv_create.email}: {str(e)}")
            raise

    def get_cv(self, cv_id: str) -> CV:
        """Get CV by ID"""
        logger.info(f"Controller: Getting CV {cv_id}")
        
        try:
            cv = self.cv_service.get_cv(cv_id)
            logger.info(f"Controller: Retrieved CV {cv_id}")
            return cv
        except Exception as e:
            logger.error(f"Controller: Failed to get CV {cv_id}: {str(e)}")
            raise

    def get_cv_with_details(self, cv_id: str) -> CVWithDetails:
        """Get CV with all related components"""
        logger.info(f"Controller: Getting CV with details {cv_id}")
        
        try:
            cv_details = self.cv_service.get_cv_with_details(cv_id)
            logger.info(f"Controller: Retrieved CV details {cv_id}")
            return cv_details
        except Exception as e:
            logger.error(f"Controller: Failed to get CV details {cv_id}: {str(e)}")
            raise

    def get_cvs(self, page: int = 1, page_size: int = 10) -> CVPaginationResponse:
        """Get all CVs with pagination"""
        logger.info(f"Controller: Getting CVs - page={page}, page_size={page_size}")
        
        try:
            result = self.cv_service.get_cvs(page, page_size)
            logger.info(f"Controller: Retrieved {len(result.cvs)} CVs (page {page})")
            return result
        except Exception as e:
            logger.error(f"Controller: Failed to get CVs: {str(e)}")
            raise

    def update_cv(self, cv_id: str, cv_update: CVUpdate) -> CV:
        """Update CV"""
        logger.info(f"Controller: Updating CV {cv_id}")
        
        try:
            cv = self.cv_service.update_cv(cv_id, cv_update)
            logger.info(f"Controller: CV updated successfully {cv_id}")
            return cv
        except Exception as e:
            logger.error(f"Controller: Failed to update CV {cv_id}: {str(e)}")
            raise

    def delete_cv(self, cv_id: str) -> Dict[str, str]:
        """Delete CV"""
        logger.info(f"Controller: Deleting CV {cv_id}")
        
        try:
            self.cv_service.delete_cv(cv_id)
            logger.info(f"Controller: CV deleted successfully {cv_id}")
            return {"message": f"CV {cv_id} deleted successfully"}
        except Exception as e:
            logger.error(f"Controller: Failed to delete CV {cv_id}: {str(e)}")
            raise

    def search_cvs(self, search_request: CVSearchRequest) -> CVPaginationResponse:
        """Search CVs"""
        logger.info(f"Controller: Searching CVs with criteria: {search_request.model_dump()}")
        
        try:
            result = self.cv_service.search_cvs(search_request)
            logger.info(f"Controller: Search found {len(result.cvs)} CVs")
            return result
        except Exception as e:
            logger.error(f"Controller: Search failed: {str(e)}")
            raise

    def bulk_create_cvs(self, bulk_request: CVBulkCreate) -> CVBulkResponse:
        """Bulk create CVs"""
        logger.info(f"Controller: Bulk creating {len(bulk_request.cvs)} CVs")
        
        try:
            result = self.cv_service.bulk_create_cvs(bulk_request)
            logger.info(f"Controller: Bulk creation completed - {result.created_count} success, {len(result.errors or [])} errors")
            return result
        except Exception as e:
            logger.error(f"Controller: Bulk creation failed: {str(e)}")
            raise

    def create_cv_components(self, request: CVComponentCreateRequest) -> CVComponentsResponse:
        """Create components for existing CV"""
        logger.info(f"Controller: Creating components for CV {request.cv_id}")
        
        try:
            result = self.cv_service.create_cv_components(request)
            logger.info(f"Controller: Components created for CV {request.cv_id}")
            return result
        except Exception as e:
            logger.error(f"Controller: Failed to create components for CV {request.cv_id}: {str(e)}")
            raise

    def get_cv_components(self, cv_id: str) -> CVComponentsResponse:
        """Get all components for a CV"""
        logger.info(f"Controller: Getting components for CV {cv_id}")
        
        try:
            result = self.cv_service.get_cv_components(cv_id)
            logger.info(f"Controller: Retrieved components for CV {cv_id}")
            return result
        except Exception as e:
            logger.error(f"Controller: Failed to get components for CV {cv_id}: {str(e)}")
            raise
