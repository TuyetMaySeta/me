from src.bootstrap.application_bootstrap import app_bootstrap


def get_employee_controller():
    """Dependency to get Employee controller from bootstrap"""
    return app_bootstrap.employee_controller


def get_employee_related_controller():
    """Dependency to get Employee related controller from bootstrap"""
    return app_bootstrap.employee_related_controller
