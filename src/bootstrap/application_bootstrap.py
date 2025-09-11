"""
Application Bootstrap - Initialize all application layers once
"""

import logging
from src.bootstrap.database_bootstrap import database_bootstrap
from src.repository.user_repository import UserRepository
from src.core.services.user_service import UserService
from src.present.controllers.user_controller import UserController
from src.present.controllers.auth_controller import AuthController

logger = logging.getLogger(__name__)


class ApplicationBootstrap:
    """
    Bootstrap class that initializes all application layers once
    Controller → Service → Repository → DB
    """
    
    def __init__(self):
        self._db_session = None
        self._user_controller = None
        self._auth_controller = None
        try:
            self._initialize_layers()
        except Exception as e:
            logger.critical(f"Failed to initialize application layers: {str(e)}")
            # Clean up any partial initialization
            if self._db_session:
                try:
                    self._db_session.close()
                except:
                    pass
            raise RuntimeError(f"Application bootstrap failed: {str(e)}") from e
    
    def _initialize_layers(self):
        """Initialize all application layers in order"""
        logger.info("Initializing application layers...")
        
        # Layer 1: Database Session
        self._db_session = database_bootstrap.SessionLocal()
        logger.info("Database session initialized")
        
        # Layer 2: Repositories
        user_repository = UserRepository(self._db_session)
        logger.info("User repository initialized")
        
        # Layer 3: Services
        user_service = UserService(user_repository)
        logger.info("User service initialized")
        
        # Layer 4: Controllers
        self._user_controller = UserController(user_service)
        self._auth_controller = AuthController(user_service)
        logger.info("Controllers initialized")
        
        logger.info("All application layers initialized successfully!")
    
    @property
    def user_controller(self):
        """Get user controller"""
        return self._user_controller
    
    @property
    def auth_controller(self):
        """Get auth controller"""
        return self._auth_controller
    
    def shutdown(self):
        """Cleanup resources"""
        if self._db_session:
            self._db_session.close()
            logger.info("Database session closed")
        logger.info("Application bootstrap shutdown complete")


# Global application bootstrap instance
app_bootstrap = ApplicationBootstrap()
