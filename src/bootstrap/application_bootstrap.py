import logging
from typing import Iterator
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


from src.config.config import settings
from src.core.services.auth_service import AuthService
from src.core.services.employee_service import EmployeeService
from src.core.services.jwt_service import JWTService
from src.present.controllers.auth_controller import AuthController
from src.present.controllers.employee_controller import EmployeeController
from src.repository.employee_repository import EmployeeRepository
from src.repository.session_repository import SessionRepository

logger = logging.getLogger(__name__)


class ApplicationBootstrap:
    """Simplified Application Bootstrap chỉ cho Employee Management"""

    def __init__(self):
        load_dotenv()
        logger.info("Initializing Employee Management System layers...")

        # Initialize database engine and session factory
        self.engine: Engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
            pool_size=20,
            max_overflow=0,
        )

        self.SessionLocal: sessionmaker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        logger.info("Database connection initialized")

        # Create a long-lived application session for singleton services
        self._app_session: Session = self.SessionLocal()

        # Initialize repositories
        self.employee_repository = EmployeeRepository(self._app_session)
        self.session_repository = SessionRepository(self._app_session)

        # Initialize services
        self.employee_service = EmployeeService(self.employee_repository)
        self._jwt_service = JWTService()
        self.auth_service = AuthService(
            self.employee_repository,
            self.session_repository,
            self._jwt_service,
        )

        # Initialize controllers
        self.employee_controller = EmployeeController(self.employee_service)
        self.auth_controller = AuthController(self.auth_service)

        logger.info("Employee system initialized successfully!")

    def shutdown(self):
        """Cleanup resources"""
        logger.info("Application bootstrap shutdown complete")

    # Database helpers
    def get_session(self) -> Iterator[Session]:
        assert self.SessionLocal is not None, "SessionLocal is not initialized"
        db: Session = self.SessionLocal()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


def get_auth_controller():
    return app_bootstrap.auth_controller


def get_employee_controller():
    return app_bootstrap.employee_controller
# Auth dependency functions
def get_current_user(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency để lấy user hiện tại (required authentication)
    """
    if not hasattr(request.state, "authenticated") or not request.state.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "NOT_AUTHENTICATED",
                    "message": "Authentication required",
                    "suggestion": "Include JWT token in Authorization header",
                    "format": "Authorization: Bearer <your-jwt-token>"
                }
            }
        )
    return request.state.current_user


def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency để lấy user hiện tại (optional authentication)
    """
    if hasattr(request.state, "authenticated") and request.state.authenticated:
        return request.state.current_user
    return None


# Global application bootstrap instance
app_bootstrap = ApplicationBootstrap()
