from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.user import UserCreate, UserUpdate, User as UserSchema
from app.services.user_service import UserService
from app.core.dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    """Create a new user"""
    try:
        return user_service.create(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[UserSchema])
def get_users(skip: int = 0, limit: int = 100, user_service: UserService = Depends(get_user_service)):
    """Get all users with pagination"""
    return user_service.get_multi(skip, limit)


@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    """Get a specific user by ID"""
    user = user_service.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: int, user_update: UserUpdate, user_service: UserService = Depends(get_user_service)):
    """Update a user"""
    try:
        user = user_service.update(user_id, user_update)
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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    """Delete a user"""
    success = user_service.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None


@router.get("/active/", response_model=List[UserSchema])
def get_active_users(skip: int = 0, limit: int = 100, user_service: UserService = Depends(get_user_service)):
    """Get all active users"""
    return user_service.get_active_users(skip, limit)


@router.patch("/{user_id}/deactivate", response_model=UserSchema)
def deactivate_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    """Deactivate a user (soft delete)"""
    success = user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user_service.get(user_id)


@router.patch("/{user_id}/activate", response_model=UserSchema)
def activate_user(user_id: int, user_service: UserService = Depends(get_user_service)):
    """Activate a user"""
    success = user_service.activate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user_service.get(user_id)
