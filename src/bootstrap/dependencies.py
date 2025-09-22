from fastapi import Depends
from sqlalchemy.orm import Session

from src.bootstrap.database_bootstrap import database_bootstrap


# Database dependency
def get_db() -> Session:
    """Dependency to get database session"""
    db = database_bootstrap.SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Employee Service dependency
def get_employee_service(db: Session = Depends(get_db)):
    from src.core.services.employee_service import EmployeeService
    from src.repository.employee_repository import EmployeeRepository

    employee_repository = EmployeeRepository(db)
    return EmployeeService(employee_repository, db)


# Employee Controller dependency
def get_employee_controller(employee_service=Depends(get_employee_service)):
    from src.present.controllers.employee_controller import EmployeeController

    return EmployeeController(employee_service)
