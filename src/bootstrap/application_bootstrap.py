import logging
from src.bootstrap.database_bootstrap import database_bootstrap
from repository.employee_repository import employeeRepository
from core.services.employee_service import employeeService
from core.services.employee_related_service import employeeRelatedService
from present.controllers.employee_controller import employeeController
from present.controllers.employee_related_controller import employeeRelatedController
from src.config.config import settings

logger = logging.getLogger(__name__)


class ApplicationBootstrap:
    def __init__(self):
        self._db_session = None
        self._employee_controller = None
        self._employee_related_controller = None
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
        logger.info("Initializing employee system layers...")
        
        # Layer 1: Database Session
        self._db_session = database_bootstrap.SessionLocal()
        logger.info("Database session initialized")
        
        # Layer 2: Repositories
        employee_repository = employeeRepository(self._db_session)
        logger.info("employee repository initialized")
        
        # Layer 3: Services
        employee_service = employeeService(employee_repository, self._db_session)
        employee_related_service = employeeRelatedService(self._db_session)
        logger.info("employee services initialized")
        
        # Layer 4: Controllers
        self._employee_controller = employeeController(employee_service)
        self._employee_related_controller = employeeRelatedController(employee_related_service)
        logger.info("employee controllers initialized")
        
        logger.info("employee system and related components initialized successfully!")
    
    @property
    def employee_controller(self):
        """Get employee controller"""
        return self._employee_controller
    
    @property
    def employee_related_controller(self):
        """Get employee related controller"""
        return self._employee_related_controller
    
    def shutdown(self):
        """Cleanup resources"""
        if self._db_session:
            self._db_session.close()
            logger.info("Database session closed")
        logger.info("Application bootstrap shutdown complete")


# Global application bootstrap instance
app_bootstrap = ApplicationBootstrap()
