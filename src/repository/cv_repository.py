from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from .base_repository import BaseRepository
from ..core.models.cv import CV

logger = logging.getLogger(__name__)


class CVRepository(BaseRepository[CV]):
    """
    Repository for CV entity.
    Only handles pure CRUD operations (no validation or business rules).
    """

    def __init__(self, db: Session):
        """Initialize CV repository with CV model."""
        super().__init__(db, CV)

    def create_cv(self, cv_data: Dict[str, Any]) -> CV:
       try:
            cv = self.create(cv_data)
            logger.info(f"Successfully created CV: {cv.id}")
            return cv
       except SQLAlchemyError as e:
            logger.error(f"Failed to create CV: {str(e)}")
            raise
    def get_cv_by_id(self, cv_id: str) -> Optional[CV]:
        try:
            cv = self.db.query(CV).filter(CV.id == cv_id).first()
            if cv:
                logger.debug(f"Found CV: {cv_id}")
            else:
                logger.debug(f"CV not found: {cv_id}")
            return cv
        except SQLAlchemyError as e:
            logger.error(f"Error getting CV {cv_id}: {str(e)}")
            raise
    def get_cv_by_email(self, email: str) -> Optional[CV]:
        try:
            cv = self.db.query(CV).filter(CV.email == email).first()
            return cv
        except SQLAlchemyError as e:
            logger.error(f"Error getting CV by email {email}: {str(e)}")
            raise
    def get_all_cvs(self, skip: int = 0, limit: int = 100) -> List[CV]:
        try:
            cvs = (
                self.db.query(CV)
                .offset(skip)
                .limit(limit)
                .all()
            )
            logger.debug(f"Retrieved {len(cvs)} CVs (skip={skip}, limit={limit})")
            return cvs
        except SQLAlchemyError as e:
            logger.error(f"Error getting CVs: {str(e)}")
            raise
    def update_cv(self, cv_id: str, update_data: Dict[str, Any]) -> Optional[CV]:
        """
        Update CV by ID.
        """
        try:
            cv = self.get_cv_by_id(cv_id)
            if not cv:
                return None

            # Update fields
            for field, value in update_data.items():
                if hasattr(cv, field) and value is not None:
                    setattr(cv, field, value)

            self.db.commit()
            self.db.refresh(cv)
            logger.info(f"Successfully updated CV: {cv_id}")
            return cv
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating CV {cv_id}: {str(e)}")
            raise
    def delete_cv(self, cv_id: str) -> bool:
        try:
            cv = self.get_cv_by_id(cv_id)
            if not cv:
                return False

            self.db.delete(cv)
            self.db.commit()
            logger.info(f"Successfully deleted CV: {cv_id}")
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting CV {cv_id}: {str(e)}")
            raise
    def count_total_cvs(self) -> int:
        try:
            count = self.db.query(CV).count()
            logger.debug(f"Total CVs count: {count}")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Error counting CVs: {str(e)}")
            raise
    def search_cvs(self, 
                   email: Optional[str] = None,
                   position: Optional[str] = None,
                   skip: int = 0,
                   limit: int = 100) -> List[CV]:
        try:
            query = self.db.query(CV)

            if email:
                query = query.filter(CV.email.ilike(f"%{email}%"))

            if position:
                query = query.filter(CV.current_position.ilike(f"%{position}%"))

            cvs = query.offset(skip).limit(limit).all()
            logger.debug(f"Search found {len(cvs)} CVs")
            return cvs
        except SQLAlchemyError as e:
            logger.error(f"Error searching CVs: {str(e)}")
            raise
    def bulk_create_cvs(self, cvs_data: List[Dict[str, Any]]) -> List[CV]:
        try:
            cvs = []
            for cv_data in cvs_data:
                cv = CV(**cv_data)
                self.db.add(cv)
                cvs.append(cv)

            self.db.commit()
            
            # Refresh all instances
            for cv in cvs:
                self.db.refresh(cv)

            logger.info(f"Successfully bulk created {len(cvs)} CVs")
            return cvs
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error bulk creating CVs: {str(e)}")
            raise
    def cv_exists(self, cv_id: str) -> bool:
        """
        Check if CV exists by ID.
        """
        try:
            exists = self.db.query(CV).filter(CV.id == cv_id).first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking CV existence {cv_id}: {str(e)}")
            raise
    def email_exists(self, email: str, exclude_id: Optional[str] = None) -> bool:
        try:
            query = self.db.query(CV).filter(CV.email == email)
            if exclude_id:
                query = query.filter(CV.id != exclude_id)
            
            exists = query.first() is not None
            return exists
        except SQLAlchemyError as e:
            logger.error(f"Error checking email existence {email}: {str(e)}")
            raise
            
    

    

    

            

    

        
       
