# src/bootstrap/dependencies.py (CV Only)
from src.bootstrap.application_bootstrap import app_bootstrap


def get_cv_controller():
    """Dependency to get CV controller from bootstrap"""
    return app_bootstrap.cv_controller