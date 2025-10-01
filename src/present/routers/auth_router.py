from fastapi import APIRouter, Depends, Path, Request, Response, status
from fastapi.responses import RedirectResponse

from src.bootstrap.application_bootstrap import get_auth_controller
from src.present.controllers.auth_controller import AuthController
from src.present.dto.auth.auth_request_dto import (
    ChangePasswordDTO,
    LoginRequestDTO,
    RefreshTokenRequestDTO,
    VerifyOldPasswordDTO,
    ChangePasswordDTO
)
from src.present.dto.auth.auth_response_dto import (
    ChangePasswordResponse,
    LoginResponseDTO,
    RefreshTokenResponseDTO,
    VerifyOldPasswordResponse,
    ChangePasswordResponse
)
from src.present.dto.auth.oauth_dto import CallbackDTO

router = APIRouter(prefix="/auth", tags=["Authentication"])

controller: AuthController = get_auth_controller()


@router.post("/login", response_model=LoginResponseDTO)
def login(login_request: LoginRequestDTO, request: Request, response: Response):
    return controller.login(login_request, request, response)


@router.post("/refresh", response_model=RefreshTokenResponseDTO)
def refresh_token(refresh_request: RefreshTokenRequestDTO):
    return controller.renew_token(refresh_request)


@router.get("/login/microsoft")
async def login_microsoft():
    auth_url = controller.get_auth_url()
    return RedirectResponse(auth_url)


@router.post("/microsoft/callback")
async def microsoft_callback(callbackDTO: CallbackDTO, request: Request):
    return controller.handle_callback(callbackDTO.code, callbackDTO.state, request)


@router.delete("/logout")
def logout(request: Request):
    return controller.logout(request)


@router.post(
    "/verify-old-password", response_model=VerifyOldPasswordResponse
)
async def verify_old_password(
    request: Request,
    verify_data: VerifyOldPasswordDTO = ...,
):
    return await controller.verify_old_password(verify_data, request)


@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(change_data: ChangePasswordDTO, request: Request ):
    """Change password with OTP verification"""
    return await controller.change_password(request, change_data)  
