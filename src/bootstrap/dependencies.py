from src.bootstrap.application_bootstrap import app_bootstrap


def get_user_controller():
    """Dependency to get user controller from bootstrap"""
    return app_bootstrap.user_controller


def get_auth_controller():
    """Dependency to get auth controller from bootstrap"""
    return app_bootstrap.auth_controller
