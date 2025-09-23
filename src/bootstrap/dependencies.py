# src/bootstrap/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session

from src.bootstrap.database_bootstrap import database_bootstrap


# Database dependency
def get_db() -> Session:
    """Dependency to get database session"""
    db = database_bootstrap.SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Employee Repository dependency
def get_employee_repository(db: Session = Depends(get_db)):
    """Get employee repository instance"""
    from src.repository.employee_repository import EmployeeRepository
    return EmployeeRepository(db)


# Employee Service dependency
def get_employee_service(
    db: Session = Depends(get_db),
    employee_repository = Depends(get_employee_repository)
):
    """Get employee service instance"""
    from src.core.services.employee_service import EmployeeService
    return EmployeeService(employee_repository, db)


# Employee Controller dependency
def get_employee_controller(employee_service = Depends(get_employee_service)):
    """Get employee controller instance"""
    from src.present.controllers.employee_controller import EmployeeController
    return EmployeeController(employee_service)


# Session Repository dependency
def get_session_repository(db: Session = Depends(get_db)):
    """Get session repository instance"""
    from src.repository.session_repository import SessionRepository
    return SessionRepository(db)


# Auth Service dependency
def get_auth_service(
    employee_repository = Depends(get_employee_repository),
    session_repository = Depends(get_session_repository)
):
    """Get auth service instance"""
    from src.core.services.auth_service import AuthService
    return AuthService(employee_repository, session_repository)


# Auth Controller dependency
def get_auth_controller(auth_service = Depends(get_auth_service)):
    """Get auth controller instance"""
    from src.present.controllers.auth_controller import AuthController
    return AuthController(auth_service)

def get_session_repository(db: Session = Depends(get_db)):
    from src.repository.session_repository import SessionRepository
    return SessionRepository(db)

def get_auth_service(
    employee_repository = Depends(get_employee_repository),
    session_repository = Depends(get_session_repository)
):
    from src.core.services.auth_service import AuthService
    return AuthService(employee_repository, session_repository)

def get_auth_controller(auth_service = Depends(get_auth_service)):
    from src.present.controllers.auth_controller import AuthController
    return AuthController(auth_service)
