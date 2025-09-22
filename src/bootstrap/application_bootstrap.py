import logging

from src.bootstrap.database_bootstrap import database_bootstrap
from src.config.config import settings

logger = logging.getLogger(__name__)


class ApplicationBootstrap:
    """Simplified Application Bootstrap chỉ cho Employee Management"""

    def __init__(self):
        self._employee_controller = None
        try:
            self._initialize_layers()
        except Exception as e:
            logger.critical(f"Failed to initialize application layers: {str(e)}")
            raise RuntimeError(f"Application bootstrap failed: {str(e)}") from e

    def _initialize_layers(self):
        """Initialize Employee management layers"""
        logger.info("Initializing Employee Management System layers...")

        # Database connection is managed by database_bootstrap
        logger.info("Database connection initialized")

        # Employee services and controllers will be created via dependency injection
        logger.info("Employee system initialized successfully!")

    @property
    def employee_controller(self):
        """Get Employee controller với dependency injection"""
        if not self._employee_controller:
            # Create controller with dependencies when needed
            from src.core.services.employee_service import EmployeeService
            from src.present.controllers.employee_controller import EmployeeController
            from src.repository.employee_repository import EmployeeRepository

            # Use a temporary session to create the controller
            db = database_bootstrap.SessionLocal()
            try:
                employee_repository = EmployeeRepository(db)
                employee_service = EmployeeService(employee_repository, db)
                self._employee_controller = EmployeeController(employee_service)
                logger.info("Employee controller created successfully")
            finally:
                db.close()

        return self._employee_controller

    def health_check(self) -> dict:
        """Get system health status"""
        try:
            # Test database connection
            db_healthy = database_bootstrap.test_connection()

            health_status = {
                "status": "healthy" if db_healthy else "degraded",
                "components": {
                    "database": "healthy" if db_healthy else "unhealthy",
                    "employee_service": "healthy",
                },
                "database_url": (
                    settings.database_url.split("@")[1]
                    if "@" in settings.database_url
                    else "configured"
                ),
            }

            if db_healthy:
                try:
                    # Get basic stats
                    db = database_bootstrap.SessionLocal()
                    try:
                        from sqlalchemy import text

                        result = db.execute(
                            text("SELECT COUNT(*) FROM employees")
                        ).scalar()
                        health_status["stats"] = {"employee_count": result}
                    except Exception as e:
                        health_status["stats"] = {
                            "error": f"Could not get stats: {str(e)}"
                        }
                    finally:
                        db.close()
                except Exception:
                    pass

            return health_status

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "components": {"database": "unknown", "employee_service": "unknown"},
            }

    def shutdown(self):
        """Cleanup resources"""
        logger.info("Application bootstrap shutdown complete")


# Global application bootstrap instance
app_bootstrap = ApplicationBootstrap()
