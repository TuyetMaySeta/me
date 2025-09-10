from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends
from src.bootstrap.database_bootstrap import database_bootstrap
from src.core.services.user_service import UserService
from src.present.controllers.user_controller import UserController
from src.present.controllers.auth_controller import AuthController


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    yield from database_bootstrap.get_session()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service"""
    return UserService(db)


def get_user_controller(user_service: UserService = Depends(get_user_service)) -> UserController:
    """Dependency to get user controller"""
    return UserController(user_service)


def get_auth_controller(user_service: UserService = Depends(get_user_service)) -> AuthController:
    """Dependency to get auth controller"""
    return AuthController(user_service)
