# src/bootstrap/application_bootstrap.py (CV Only)
"""
Application Bootstrap - Initialize CV system only
"""

import logging
from src.bootstrap.database_bootstrap import database_bootstrap
from src.repository.cv_repository import CVRepository
from src.core.services.cv_service import CVService
from src.present.controllers.cv_controller import CVController
from src.config.config import settings

logger = logging.getLogger(__name__)


class ApplicationBootstrap:
    """
    Bootstrap class that initializes CV system
    Controller → Service → Repository → DB
    """
    
    def __init__(self):
        self._db_session = None
        self._cv_controller = None
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
        logger.info("Initializing CV system layers...")
        
        # Layer 1: Database Session
        self._db_session = database_bootstrap.SessionLocal()
        logger.info("Database session initialized")
        
        # Layer 2: Repository
        cv_repository = CVRepository(self._db_session)
        logger.info("CV repository initialized")
        
        # Layer 3: Service
        cv_service = CVService(cv_repository, self._db_session)
        logger.info("CV service initialized")
        
        # Layer 4: Controller
        self._cv_controller = CVController(cv_service)
        logger.info("CV controller initialized")
        
        logger.info("CV system initialized successfully!")
    
    @property
    def cv_controller(self):
        """Get CV controller"""
        return self._cv_controller
    
    def shutdown(self):
        """Cleanup resources"""
        if self._db_session:
            self._db_session.close()
            logger.info("Database session closed")
        logger.info("Application bootstrap shutdown complete")


# Global application bootstrap instance
app_bootstrap = ApplicationBootstrap()