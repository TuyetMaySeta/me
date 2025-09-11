from fastapi import APIRouter, Depends
from src.present.request.auth import LoginRequest, Token, ChangePasswordRequest
from src.present.controllers.auth_controller import AuthController
from src.bootstrap.dependencies import get_auth_controller

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    login_request: LoginRequest, 
    controller: AuthController = Depends(get_auth_controller)
):
    """Authenticate user and return access token"""
    return controller.login(login_request)


@router.post("/change-password/{user_id}")
def change_password(
    user_id: int, 
    password_request: ChangePasswordRequest,
    controller: AuthController = Depends(get_auth_controller)
):
    """Change user password"""
    return controller.change_password(user_id, password_request)
