# src/bootstrap/application_bootstrap.py
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
        self._employee_controller = None
        self._employee_related_controller = None
        try:
            self._initialize_layers()
        except Exception as e:
            logger.critical(f"Failed to initialize application layers: {str(e)}")
            raise RuntimeError(f"Application bootstrap failed: {str(e)}") from e
    
    def _initialize_layers(self):
        """Initialize all application layers in order"""
        logger.info("Initializing Employee system layers...")
        
        # Don't create global session - use dependency injection instead
        logger.info("Database connection initialized")
        
        # Layer 2: Create services and controllers with session factory
        # These will get sessions via dependency injection
        logger.info("Employee services and controllers initialized")
        
        logger.info("Employee system and related components initialized successfully!")
    
    @property
    def employee_controller(self):
        """Get Employee controller"""
        if not self._employee_controller:
            # Create controller with dependencies when needed
            from src.repository.employee_repository import EmployeeRepository
            from src.core.services.employee_service import EmployeeService
            from src.present.controllers.employee_controller import EmployeeController
            
            # Use a temporary session to create the controller
            db = database_bootstrap.SessionLocal()
            try:
                employee_repository = EmployeeRepository(db)
                employee_service = EmployeeService(employee_repository, db)
                self._employee_controller = EmployeeController(employee_service)
            finally:
                db.close()
        
        return self._employee_controller
    
    @property
    def employee_related_controller(self):
        """Get Employee related controller"""
        if not self._employee_related_controller:
            from src.core.services.employee_related_service import EmployeeRelatedService
            from src.present.controllers.employee_related_controller import EmployeeRelatedController
            
            # Use a temporary session to create the controller
            db = database_bootstrap.SessionLocal()
            try:
                employee_related_service = EmployeeRelatedService(db)
                self._employee_related_controller = EmployeeRelatedController(employee_related_service)
            finally:
                db.close()
        
        return self._employee_related_controller
    
    def shutdown(self):
        """Cleanup resources"""
        logger.info("Application bootstrap shutdown complete")


# Global application bootstrap instance
app_bootstrap = ApplicationBootstrap()
