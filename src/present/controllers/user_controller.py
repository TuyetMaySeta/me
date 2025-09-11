from typing import List
import logging
from src.core.services.user_service import UserService
from src.present.request.user import UserCreate, UserUpdate, User as UserSchema

logger = logging.getLogger(__name__)


class UserController:
    """User controller - handles HTTP requests and responses"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def create_user(self, user_create: UserCreate) -> UserSchema:
        """Create a new user"""
        logger.info(f"Creating user: {user_create.email}")
        user = self.user_service.create(user_create)
        logger.info(f"User created successfully: {user.email} (ID: {user.id})")
        return user
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserSchema]:
        """Get all users with pagination"""
        return self.user_service.get_multi(skip, limit)
    
    def get_user(self, user_id: int) -> UserSchema:
        """Get a specific user by ID"""
        return self.user_service.get(user_id)
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> UserSchema:
        """Update a user"""
        return self.user_service.update(user_id, user_update)
    
    def delete_user(self, user_id: int) -> None:
        """Delete a user"""
        self.user_service.delete(user_id)
        return None
