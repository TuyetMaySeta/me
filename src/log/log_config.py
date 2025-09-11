"""
Centralized logging configuration for EMS application
"""

import logging
from contextvars import ContextVar

# Import request_id_context from middleware
from src.present.middleware.request_id_middleware import request_id_context


class RequestIDFormatter(logging.Formatter):
    """Custom formatter that automatically includes request ID in log messages"""
    
    def format(self, record):
        # Get request ID from context
        request_id = request_id_context.get('no-request-id')
        
        # Add request ID to the log record
        if request_id != 'no-request-id':
            # If there's a request ID, prepend the full request ID to the message
            record.msg = f"[{request_id}] {record.msg}"
        
        return super().format(record)


def setup_request_logging():
    """Setup logging configuration for request tracking"""
    request_logger = logging.getLogger("request_tracker")
    request_logger.setLevel(logging.INFO)
    
    # Prevent propagation to avoid duplicate logs
    request_logger.propagate = False
    
    # Create handler if not exists
    if not request_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        request_logger.addHandler(handler)
    
    return request_logger


def setup_application_logging():
    """Setup application logging with request ID formatting"""
    # Get the root logger or application logger
    app_logger = logging.getLogger()
    
    # Find existing handlers and update their formatters
    for handler in app_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            # Use custom formatter that includes request ID
            formatter = RequestIDFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
    
    # If no handlers exist, create one
    if not app_logger.handlers:
        handler = logging.StreamHandler()
        formatter = RequestIDFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        app_logger.addHandler(handler)
        app_logger.setLevel(logging.INFO)


def setup_logging(log_level: str = "DEBUG") -> None:
    """
    Setup centralized logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Setup request logging first
    setup_request_logging()
    
    # Setup application logging with request ID formatting
    setup_application_logging()
    
    # Configure root logger level
    app_logger = logging.getLogger()
    app_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Suppress noisy third-party libraries
    _suppress_third_party_logs()
    
    # Suppress database-related logs
    _suppress_database_logs()
    
    # Configure application-specific loggers
    _configure_application_loggers()


def _suppress_third_party_logs():
    """Suppress noisy third-party library logs"""
    
    # Suppress uvicorn logs
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.setLevel(logging.CRITICAL)
    
    # Suppress passlib debug logs
    passlib_logger = logging.getLogger("passlib")
    passlib_logger.setLevel(logging.WARNING)
    
    # Suppress other common noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def _suppress_database_logs():
    """Suppress database-related logs for cleaner output"""
    
    # Suppress SQLAlchemy logs completely
    sqlalchemy_engine_logger = logging.getLogger("sqlalchemy.engine")
    sqlalchemy_engine_logger.setLevel(logging.CRITICAL)
    
    # Also suppress SQLAlchemy connection pool logs
    sqlalchemy_pool_logger = logging.getLogger("sqlalchemy.pool")
    sqlalchemy_pool_logger.setLevel(logging.CRITICAL)
    
    # Suppress general SQLAlchemy logs
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.setLevel(logging.CRITICAL)
    
    # Suppress database bootstrap logs
    db_logger = logging.getLogger("src.bootstrap.database_bootstrap")
    db_logger.setLevel(logging.CRITICAL)


def _configure_application_loggers():
    """Configure application-specific logger levels"""
    
    # Core business logic - keep INFO level
    core_logger = logging.getLogger("src.core")
    core_logger.setLevel(logging.INFO)
    
    # API presentation layer - keep INFO level
    present_logger = logging.getLogger("src.present")
    present_logger.setLevel(logging.INFO)
    
    # Repository layer - keep INFO level
    repository_logger = logging.getLogger("src.repository")
    repository_logger.setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
