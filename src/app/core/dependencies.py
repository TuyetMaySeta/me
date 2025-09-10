from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends
from src.app.db.database import get_db
from src.core.services.user_service import UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service"""
    return UserService(db)
