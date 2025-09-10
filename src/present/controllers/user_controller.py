from typing import List
from fastapi import HTTPException, status
from src.core.services.user_service import UserService
from src.present.request.user import UserCreate, UserUpdate, User as UserSchema


class UserController:
    """User controller - handles HTTP requests and responses"""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def create_user(self, user_create: UserCreate) -> UserSchema:
        """Create a new user"""
        try:
            return self.user_service.create(user_create)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserSchema]:
        """Get all users with pagination"""
        return self.user_service.get_multi(skip, limit)
    
    def get_user(self, user_id: int) -> UserSchema:
        """Get a specific user by ID"""
        user = self.user_service.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> UserSchema:
        """Update a user"""
        try:
            user = self.user_service.update(user_id, user_update)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    def delete_user(self, user_id: int) -> None:
        """Delete a user"""
        success = self.user_service.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return None
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[UserSchema]:
        """Get all active users"""
        return self.user_service.get_active_users(skip, limit)
    
    def deactivate_user(self, user_id: int) -> UserSchema:
        """Deactivate a user (soft delete)"""
        success = self.user_service.deactivate_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return self.user_service.get(user_id)
    
    def activate_user(self, user_id: int) -> UserSchema:
        """Activate a user"""
        success = self.user_service.activate_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return self.user_service.get(user_id)
