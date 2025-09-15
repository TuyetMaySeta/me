# src/bootstrap/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from src.bootstrap.database_bootstrap import database_bootstrap
from src.bootstrap.application_bootstrap import app_bootstrap

# Database dependency
def get_db() -> Session:
    """Dependency to get database session"""
    db = database_bootstrap.SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

# Service dependencies
def get_employee_service(db: Session = Depends(get_db)):
    """Dependency to get Employee service"""
    from src.repository.employee_repository import EmployeeRepository
    from src.core.services.employee_service import EmployeeService
    
    employee_repository = EmployeeRepository(db)
    return EmployeeService(employee_repository, db)

def get_employee_related_service(db: Session = Depends(get_db)):
    """Dependency to get Employee related service"""
    from src.core.services.employee_related_service import EmployeeRelatedService
    return EmployeeRelatedService(db)

# Controller dependencies
def get_employee_controller(employee_service = Depends(get_employee_service)):
    """Dependency to get Employee controller"""
    from src.present.controllers.employee_controller import EmployeeController
    return EmployeeController(employee_service)

def get_employee_related_controller(employee_related_service = Depends(get_employee_related_service)):
    """Dependency to get Employee related controller"""
    from src.present.controllers.employee_related_controller import EmployeeRelatedController
    return EmployeeRelatedController(employee_related_service)
