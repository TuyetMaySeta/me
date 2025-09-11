from fastapi import APIRouter, Depends, status
from typing import List
from src.present.request.user import UserCreate, UserUpdate, User as UserSchema
from src.present.controllers.user_controller import UserController
from src.bootstrap.dependencies import get_user_controller

router = APIRouter(prefix="/users", tags=["Users"])


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
