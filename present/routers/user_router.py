from fastapi import APIRouter, Depends, status
from typing import List
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from present.controllers.user_controller import UserController
from core.services.user_service import UserService
from app.core.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


def get_user_controller(user_service: UserService = Depends(get_user_service)) -> UserController:
    """Dependency to get user controller"""
    return UserController(user_service)


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate, 
    controller: UserController = Depends(get_user_controller)
):
    """Create a new user"""
    return controller.create_user(user)


@router.get("/", response_model=List[UserSchema])
def get_users(
    skip: int = 0, 
    limit: int = 100, 
    controller: UserController = Depends(get_user_controller)
):
    """Get all users with pagination"""
    return controller.get_users(skip, limit)


@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: int, 
    controller: UserController = Depends(get_user_controller)
):
    """Get a specific user by ID"""
    return controller.get_user(user_id)


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int, 
    user_update: UserUpdate, 
    controller: UserController = Depends(get_user_controller)
):
    """Update a user"""
    return controller.update_user(user_id, user_update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, 
    controller: UserController = Depends(get_user_controller)
):
    """Delete a user"""
    return controller.delete_user(user_id)


@router.get("/active/", response_model=List[UserSchema])
def get_active_users(
    skip: int = 0, 
    limit: int = 100, 
    controller: UserController = Depends(get_user_controller)
):
    """Get all active users"""
    return controller.get_active_users(skip, limit)


@router.patch("/{user_id}/deactivate", response_model=UserSchema)
def deactivate_user(
    user_id: int, 
    controller: UserController = Depends(get_user_controller)
):
    """Deactivate a user (soft delete)"""
    return controller.deactivate_user(user_id)


@router.patch("/{user_id}/activate", response_model=UserSchema)
def activate_user(
    user_id: int, 
    controller: UserController = Depends(get_user_controller)
):
    """Activate a user"""
    return controller.activate_user(user_id)
