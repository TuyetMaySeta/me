from fastapi import APIRouter, Depends, Request, Response, Cookie
from typing import Optional

from src.bootstrap.dependencies import get_auth_controller
from src.present.controllers.auth_controller import AuthController
from src.present.dto.auth.auth_dto import (
    LoginRequestDTO,
    LoginResponseDTO,
    RefreshTokenRequestDTO,
    RefreshTokenResponseDTO,
    TokenVerificationDTO
)
from src.bootstrap.auth_dependencies import require_authentication, AuthenticationResult, optional_authentication

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponseDTO)
def login(
    login_request: LoginRequestDTO,
    request: Request,
    response: Response,
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Employee login with ID/email and password
    
    - **employee_id**: Employee ID or email address
    - **password**: Employee password
    - **remember_me**: Extend session duration if true
    
    Returns JWT tokens and employee information
    """
    return controller.login(login_request, request, response)

@router.post("/refresh", response_model=RefreshTokenResponseDTO)
def refresh_token(
    refresh_request: RefreshTokenRequestDTO,
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Refresh access token using refresh token
    
    Returns new access token
    """
    return controller.refresh_token(refresh_request)

@router.post("/verify", response_model=TokenVerificationDTO)
def verify_token(
    access_token: Optional[str] = Cookie(None),
    controller: AuthController = Depends(get_auth_controller)
):
    """
    Verify access token validity
    
    Returns token verification result
    """
    if not access_token:
        return TokenVerificationDTO(valid=False)
    
    try:
        result = controller.verify_token(access_token)
        return TokenVerificationDTO(
            valid=result["valid"],
            employee_id=result.get("employee_id"),
            email=result.get("email"),
            expires_at=result.get("expires_at")
        )
    except Exception:
        return TokenVerificationDTO(valid=False)

@router.get("/token-info")
def get_token_info(
    auth: Optional[AuthenticationResult] = Depends(optional_authentication)
):
    """
    Get token information (works with expired tokens)
    """
    if not auth:
        return {
            "authenticated": False,
            "message": "No valid token found",
            "action": "Login required"
        }
    
    return {
        "authenticated": True,
        "employee_id": auth.employee_id,
        "email": auth.email,
        "token_info": auth.token_info,
        "is_near_expiry": auth.is_near_expiry
    }
