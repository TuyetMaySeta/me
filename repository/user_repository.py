from typing import Optional, List
from sqlalchemy.orm import Session
from app.core.models.user import User
from repository.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository with specific user operations"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.get_by_field("email", email)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.get_by_field("username", username)
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all active users"""
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def get_superusers(self) -> List[User]:
        """Get all superusers"""
        return self.db.query(User).filter(User.is_superuser == True).all()
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user"""
        user = self.get(user_id)
        if user:
            user.is_active = False
            self.db.commit()
            return True
        return False
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user"""
        user = self.get(user_id)
        if user:
            user.is_active = True
            self.db.commit()
            return True
        return False
