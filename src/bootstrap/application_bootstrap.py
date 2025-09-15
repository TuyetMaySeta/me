import logging
from src.bootstrap.database_bootstrap import database_bootstrap
from src.repository.employee_repository import EmployeeRepository
from src.core.services.employee_service import EmployeeService
from src.core.services.employee_related_service import EmployeeRelatedService
from src.present.controllers.employee_controller import EmployeeController
from src.present.controllers.employee_related_controller import EmployeeRelatedController
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
        logger.info("Initializing Employee system layers...")
        
        # Layer 1: Database Session
        self._db_session = database_bootstrap.SessionLocal()
        logger.info("Database session initialized")
        
        # Layer 2: Repositories
        employee_repository = EmployeeRepository(self._db_session)
        logger.info("Employee repository initialized")
        
        # Layer 3: Services
        employee_service = EmployeeService(employee_repository, self._db_session)
        employee_related_service = EmployeeRelatedService(self._db_session)
        logger.info("Employee services initialized")
        
        # Layer 4: Controllers
        self._employee_controller = EmployeeController(employee_service)
        self._employee_related_controller = EmployeeRelatedController(employee_related_service)
        logger.info("Employee controllers initialized")
        
        logger.info("Employee system and related components initialized successfully!")
    
    @property
    def employee_controller(self):
        """Get Employee controller"""
        return self._employee_controller
    
    @property
    def employee_related_controller(self):
        """Get Employee related controller"""
        return self._employee_related_controller
    
    def shutdown(self):
        """Cleanup resources"""
        if self._db_session:
            self._db_session.close()
            logger.info("Database session closed")
        logger.info("Application bootstrap shutdown complete")


# Global application bootstrap instance
app_bootstrap = ApplicationBootstrap()
