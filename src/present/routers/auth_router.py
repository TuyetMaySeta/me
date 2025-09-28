from fastapi import (
    APIRouter,
    Depends,
    Request,
    Response,
)
from fastapi.responses import RedirectResponse

from src.bootstrap.application_bootstrap import get_auth_controller
from src.present.controllers.auth_controller import AuthController
from src.present.dto.auth.auth_request_dto import (
    LoginRequestDTO,
    RefreshTokenRequestDTO,
)
from src.present.dto.auth.auth_response_dto import (
    LoginResponseDTO,
    RefreshTokenResponseDTO,
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
