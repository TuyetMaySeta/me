from typing import TypeVar, Generic, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.bootstrap.database_bootstrap import database_bootstrap

ModelType = TypeVar("ModelType", bound=database_bootstrap.get_base())


class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations"""
    
    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """Get a single record by a specific field"""
        field = getattr(self.model, field_name)
        return self.db.query(self.model).filter(field == value).first()
    
    def get_multi_by_field(self, field_name: str, value: Any) -> List[ModelType]:
        """Get multiple records by a specific field"""
        field = getattr(self.model, field_name)
        return self.db.query(self.model).filter(field == value).all()
    
    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """Update an existing record"""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: Any) -> bool:
        """Delete a record by ID"""
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
    
    def exists(self, id: Any) -> bool:
        """Check if a record exists by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
