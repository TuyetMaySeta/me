from typing import Any, Dict
from sqlalchemy.orm import Session
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
        """
        Create a new CV (no validation here, just DB insert).
        Args:
            cv_data: Dictionary containing CV fields
        Returns:
            Created CV instance
        """
        cv = self.create(cv_data)
        logger.info(f"Successfully created CV: {cv.id}")
        return cv
