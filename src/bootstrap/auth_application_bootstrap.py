from fastapi import FastAPI
from sqlalchemy.orm import Session
import asyncio
from datetime import timedelta
from src.repository.employee_repository import EmployeeRepository
from src.repository.session_repository import SessionRepository
from src.core.services.auth_service import AuthService
from src.core.services.jwt_service import JWTService
from src.core.services.session_service import SessionService
from src.core.utils.password_utils import hash_password, verify_password, generate_default_password
from src.present.controllers.auth_controller import AuthController
from src.present.middleware.auth_middleware import AuthMiddleware, auth_middleware_handler
from src.present.routers.auth_router import router as auth_router
from src.config.auth_config import auth_config, validate_auth_config
from src.bootstrap.database_bootstrap import get_db_session


class AuthApplicationBootstrap:
    """Bootstrap class for authentication system initialization"""
    
    def __init__(self, app: FastAPI, db_session: Session):
        """
        Initialize authentication bootstrap
        
        """
        self.app = app
        self.db_session = db_session
        self._repositories = {}
        self._services = {}
        self._controllers = {}
        self._middleware = None
    
    def initialize(self):
        """
        Initialize complete authentication system
        
        """
        print(" Initializing Authentication System...")
        
        # Step 1: Validate configuration
        self._validate_configuration()
        
        # Step 2: Initialize repositories
        self._initialize_repositories()
        
        # Step 3: Initialize services
        self._initialize_services()
        
        # Step 4: Initialize controllers
        self._initialize_controllers()
        
        # Step 5: Setup middleware
        self._setup_middleware()
        
        # Step 6: Register routes
        self._register_routes()
        
        # Step 7: Setup background tasks
        self._setup_background_tasks()
        
        print(" Authentication System initialized successfully!")
    
    def _validate_configuration(self):
        """Validate authentication configuration"""
        print(" Validating authentication configuration...")
        try:
            validate_auth_config()
            print(f"   JWT Algorithm: {auth_config.jwt_algorithm}")
            print(f"   Access Token Expiry: {auth_config.access_token_expire_minutes} minutes")
            print(f"   Session Expiry: {auth_config.session_expire_days} days")
            print(f"   Cookie Secure: {auth_config.get_cookie_secure()}")
            print(f"   Environment: {'Production' if auth_config.is_production else 'Development'}")
        except ValueError as e:
            print(f" Configuration validation failed: {e}")
            raise
    
    def _initialize_repositories(self):
        """Initialize authentication repositories"""
        print(" Initializing repositories...")
        
        # Employee Repository
        self._repositories['employee'] = EmployeeRepository(self.db_session)
        print(" EmployeeRepository initialized")
        
        # Session Repository  
        self._repositories['session'] = SessionRepository(self.db_session)
        print(" SessionRepository initialized")
    
    def _initialize_services(self):
        """Initialize authentication services"""
        print(" Initializing services...")
        
        # JWT Service (stateless)
        self._services['jwt'] = JWTService()
        print(" JWTService initialized")
        
        # Session Service  
        self._services['session'] = SessionService()
        print(" SessionService initialized")
        
        # Authentication Service (main service)
        self._services['auth'] = AuthService(
            employee_repository=self._repositories['employee'],
            session_repository=self._repositories['session']
        )
        print(" AuthService initialized")
        
        # Password utilities are imported functions, not services
        print(" Password utilities available")
    
    def _initialize_controllers(self):
        """Initialize authentication controllers"""
        print(" Initializing controllers...")
        
        # Authentication Controller
        self._controllers['auth'] = AuthController(
            auth_service=self._services['auth']
        )
        print(" AuthController initialized")
    
    def _setup_middleware(self):
        """Setup authentication middleware"""
        print(" Setting up authentication middleware...")
        
        # Initialize middleware
        self._middleware = AuthMiddleware(
            session_repository=self._repositories['session'],
            employee_repository=self._repositories['employee']
        )
        
        # Add middleware to app state for dependency injection
        self.app.state.auth_middleware = self._middleware
        
        # Add ASGI middleware for automatic request processing
        self.app.middleware("http")(auth_middleware_handler)
        
        print(" Authentication middleware configured")
    
    def _register_routes(self):
        """Register authentication routes"""
        print(" Registering authentication routes...")
        
        # Setup dependency injection for auth controller in router
        def get_auth_controller():
            return self._controllers['auth']
        
        # Override the dependency in auth_router
        auth_router.dependency_overrides = {}
        from src.present.routers.auth_router import get_auth_controller as router_get_auth_controller
        auth_router.dependency_overrides[router_get_auth_controller] = get_auth_controller
        
        # Include authentication router
        self.app.include_router(auth_router)
        
        print(" Authentication routes registered:")
        print("      - POST /auth/login")
        print("      - POST /auth/refresh") 
        print("      - GET /auth/me")
        print("      - GET /auth/health")
    
    def _setup_background_tasks(self):
        """Setup background tasks for session cleanup"""
        print("⏰ Setting up background tasks...")
        
        async def cleanup_expired_sessions():
            """Background task to cleanup expired sessions"""
            try:
                cleaned_count = self._repositories['session'].cleanup_expired_sessions()
                if cleaned_count > 0:
                    print(f" Cleaned up {cleaned_count} expired sessions")
            except Exception as e:
                print(f" Session cleanup failed: {e}")
        
        # Setup periodic cleanup task
        async def session_cleanup_scheduler():
            """Schedule session cleanup every hour"""
            while True:
                await asyncio.sleep(3600)  # Run every hour
                await cleanup_expired_sessions()
        
        # Add cleanup task to app startup
        @self.app.on_event("startup")
        async def startup_tasks():
            """Tasks to run on application startup"""
            print(" Starting authentication background tasks...")
            # Run initial cleanup
            await cleanup_expired_sessions()
            # Start scheduler
            asyncio.create_task(session_cleanup_scheduler())
        
        print(" Session cleanup task configured (runs every hour)")
    
    def get_auth_service(self) -> AuthService:
        """Get authentication service instance"""
        return self._services['auth']
    
    def get_auth_controller(self) -> AuthController:
        """Get authentication controller instance"""
        return self._controllers['auth']
    
    def get_auth_middleware(self) -> AuthMiddleware:
        """Get authentication middleware instance"""
        return self._middleware
    
    def get_session_repository(self) -> SessionRepository:
        """Get session repository instance"""
        return self._repositories['session']
    
    def get_employee_repository(self) -> EmployeeRepository:
        """Get employee repository instance"""
        return self._repositories['employee']


def setup_authentication(app: FastAPI, db_session: Session = None) -> AuthApplicationBootstrap:
    """
    Setup authentication system for FastAPI application
    
    Args:
        app: FastAPI application instance
        db_session: Optional database session (will get from bootstrap if None)
        
    Returns:
        AuthApplicationBootstrap instance for further configuration
    """
    # Get database session if not provided
    if db_session is None:
        db_session = next(get_db_session())
    
    # Create and initialize authentication bootstrap
    auth_bootstrap = AuthApplicationBootstrap(app, db_session)
    auth_bootstrap.initialize()
    
    return auth_bootstrap


# Convenience function for quick setup
def quick_auth_setup(app: FastAPI) -> AuthApplicationBootstrap:
    """
    Quick authentication setup with default configuration
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Initialized AuthApplicationBootstrap
    """
    print(" Quick authentication setup...")
    return setup_authentication(app)


# Example usage in main application
"""
# In your main FastAPI app file:

from fastapi import FastAPI
from src.bootstrap.auth_application_bootstrap import quick_auth_setup

app = FastAPI()

# Setup authentication system
auth_bootstrap = quick_auth_setup(app)

# Optional: Access authentication components
auth_service = auth_bootstrap.get_auth_service()
auth_middleware = auth_bootstrap.get_auth_middleware()
"""