# src/bootstrap/dependencies.py
from fastapi import Depends
from sqlalchemy.orm import Session
from src.bootstrap.database_bootstrap import database_bootstrap

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

# Employee Service dependency
def get_employee_service(db: Session = Depends(get_db)):
    """Dependency to get Employee service"""
    from src.repository.employee_repository import EmployeeRepository
    from src.core.services.employee_service import EmployeeService
    
    employee_repository = EmployeeRepository(db)
    return EmployeeService(employee_repository, db)

# Employee Controller dependency
def get_employee_controller(employee_service = Depends(get_employee_service)):
    """Dependency to get Employee controller"""
    from src.present.controllers.employee_controller import EmployeeController
    return EmployeeController(employee_service)
