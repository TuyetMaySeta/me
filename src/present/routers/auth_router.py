from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
)
from fastapi.responses import RedirectResponse
from typing import Optional
from src.bootstrap.application_bootstrap import get_auth_controller
from src.present.controllers.auth_controller import AuthController
from src.present.dto.auth.auth_request_dto import (
    LoginRequestDTO,
    RefreshTokenRequestDTO,
)
from src.bootstrap.application_bootstrap import get_current_user, get_current_user_optional

from src.present.dto.auth.auth_response_dto import (
    LoginResponseDTO,
    RefreshTokenResponseDTO,
)
from src.present.middleware.jwt_middleware import get_current_user,get_current_user_optional

from fastapi.responses import RedirectResponse, JSONResponse
from src.present.dto.auth.oauth_dto import CallbackDTO

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponseDTO)
def login(
    login_request: LoginRequestDTO,
    request: Request,
    response: Response,
    controller: AuthController = Depends(get_auth_controller),
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
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Refresh access token using refresh token

    Returns new access token
    """
    return controller.renew_token(refresh_request)


@router.get("/login/microsoft")
async def login_microsoft(controller: AuthController = Depends(get_auth_controller)):
    """Redirect người dùng sang Microsoft login"""
    auth_url = controller.get_auth_url()
    return RedirectResponse(auth_url)


@router.post("/microsoft/callback")
async def microsoft_callback(
    callbackDTO: CallbackDTO, controller: AuthController = Depends(get_auth_controller)
):
    return controller.handle_callback(callbackDTO.code, callbackDTO.state)

@router.get("/protected")
def get_profile(user: dict = Depends(get_current_user)):
    return {
        "user": user,
        "message": "Profile retrieved successfully"
    }
@router.get("/public")
def public_endpoint(user: Optional[dict] = Depends(get_current_user_optional)):
    if user:
        return {"message": "Authenticated", "user": user}
    return {"message": "Public access"}
