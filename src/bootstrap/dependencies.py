
from src.bootstrap.application_bootstrap import app_bootstrap


def get_cv_controller():
    """Dependency to get CV controller from bootstrap"""
    return app_bootstrap.cv_controller


def get_cv_related_controller():
    """Dependency to get CV related controller from bootstrap"""
    return app_bootstrap.cv_related_controller