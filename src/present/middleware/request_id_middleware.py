import uuid
import time
import logging
from contextvars import ContextVar
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from typing import Callable

# Context variable to store request ID
request_id_context: ContextVar[str] = ContextVar('request_id', default='no-request-id')

# Configure logger for request tracking
logger = logging.getLogger("request_tracker")

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request
    - Generates UUID for each request
    - Adds request ID to response headers
    - Logs request/response with request ID
    - Tracks request duration
    """
    
    def __init__(self, app, header_name: str = "X-Request-ID"):
        super().__init__(app)
        self.header_name = header_name
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add request ID to request state and context for access in route handlers
        request.state.request_id = request_id
        request_id_context.set(request_id)
        
        # Start timing
        start_time = time.time()
        
        # Store user agent for response log (no incoming request log)
        user_agent = request.headers.get('user-agent', 'unknown')
        request.state.user_agent = user_agent
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = round((time.time() - start_time) * 1000, 2)  # in milliseconds
            
            # Log response with user agent
            user_agent = getattr(request.state, 'user_agent', 'unknown')
            logger.info(
                f"[{request_id}] ← {response.status_code} | "
                f"{request.method} {request.url.path} | "
                f"{duration}ms | UA: {user_agent}"
            )
            
            # Add request ID to response headers
            if isinstance(response, StreamingResponse):
                # For streaming responses, set headers directly
                response.headers[self.header_name] = request_id
                response.headers["X-Response-Time"] = f"{duration}ms"
            else:
                # For regular responses
                response.headers[self.header_name] = request_id
                response.headers["X-Response-Time"] = f"{duration}ms"
            
            return response
            
        except Exception as e:
            # Calculate duration for error case
            duration = round((time.time() - start_time) * 1000, 2)
            
            # Log error with user agent
            user_agent = getattr(request.state, 'user_agent', 'unknown')
            logger.error(
                f"[{request_id}] ← ERROR | {request.method} {request.url.path} | "
                f"{duration}ms | UA: {user_agent} | Error: {str(e)}"
            )
            
            # Re-raise the exception to be handled by other middleware/handlers
            raise


class RequestIDFormatter(logging.Formatter):
    """Custom formatter that automatically includes request ID in log messages"""
    
    def format(self, record):
        # Get request ID from context
        request_id = request_id_context.get('no-request-id')
        
        # Add request ID to the log record
        if request_id != 'no-request-id':
            # If there's a request ID, prepend it to the message
            record.msg = f"[{request_id[:8]}...] {record.msg}"
        
        return super().format(record)


# Configure request tracker logger
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
