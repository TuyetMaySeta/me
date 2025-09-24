import logging
from typing import Any, Dict, Generic, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: T):
        """
        Initialize repository with database session and model class.

        Args:
            db: SQLAlchemy database session
            model: SQLAlchemy model class (e.g., Employee, Language, etc.)
        """
        self.db = db
        self.model = model

    def create(self, entity_data: Dict[str, Any]) -> T:
        """
        Create a new entity in the database.
        """
        try:
            entity = self.model(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            logger.info(f"Created new {self.model.__name__} with data: {entity_data}")
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to create {self.model.__name__}: {str(e)}")
            raise
