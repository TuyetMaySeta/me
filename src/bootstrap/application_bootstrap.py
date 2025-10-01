import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from src.bootstrap.llm_bootstrap import llm_bootstrap
from src.config.config import settings
from src.core.mapper.employee import EmployeeMapper
from src.core.services.auth_service import AuthService
from src.core.services.cv_service import CVService
from src.core.services.employee_service import EmployeeService
from src.core.services.jwt_service import JWTService
from src.core.services.project_service import ProjectService
from src.core.services.role_service import RoleService
from src.present.controllers.auth_controller import AuthController
from src.present.controllers.cv_controller import CVController
from src.present.controllers.employee_controller import EmployeeController
from src.present.controllers.project_controller import ProjectController
from src.present.controllers.role_controller import RoleController
from src.repository.employee_repository import EmployeeRepository
from src.repository.project_repository import ProjectRepository
from src.repository.role import RoleRepository
from src.repository.session_repository import SessionRepository
from src.repository.verification_repository import VerificationRepository
from src.sdk.microsoft.client import MicrosoftClient

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

        # Initialize sdk
        self.microsoft_client = MicrosoftClient()

        # init llm
        self._llm_instances = llm_bootstrap.get_llm_instances()
        logger.info("LLM instances initialized")

        # Initialize repositories
        self.employee_repository = EmployeeRepository(self._app_session)
        self.session_repository = SessionRepository(self._app_session)
        self.role_repository = RoleRepository(self._app_session)
        self.verification_repository = VerificationRepository(self._app_session)
        self.project_repository = ProjectRepository(self._app_session)

        # Initialize mappers
        self.employee_mapper = EmployeeMapper()

        # Initialize services
        self.employee_service = EmployeeService(
            self.employee_repository, self.employee_mapper, self.role_repository
        )
        self.cv_service = CVService(self.employee_repository, self._llm_instances)
        self.role_service = RoleService(self.role_repository)
        self.project_service = ProjectService(self.project_repository)
        self._jwt_service = JWTService()
        self.auth_service = AuthService(
            self.employee_repository,
            self.session_repository,
            self._jwt_service,
            self.microsoft_client,
            self.verification_repository,
        )

        # Initialize controllers
        self.employee_controller = EmployeeController(self.employee_service)
        self.cv_controller = CVController(self.cv_service)
        self.auth_controller = AuthController(self.auth_service)
        self.role_controller = RoleController(self.role_service)
        self.project_controller = ProjectController(self.project_service)

        logger.info("Employee system initialized successfully!")

    def shutdown(self):
        """Cleanup resources"""
        self.engine.dispose()
        logger.info("Application bootstrap shutdown complete")


def get_auth_service():
    return app_bootstrap.auth_service


def get_auth_controller():
    return app_bootstrap.auth_controller


def get_employee_controller():
    return app_bootstrap.employee_controller


def get_cv_controller():
    return app_bootstrap.cv_controller


def get_role_controller():
    return app_bootstrap.role_controller


def get_project_controller():
    return app_bootstrap.project_controller


# Global application bootstrap instance
app_bootstrap = ApplicationBootstrap()
