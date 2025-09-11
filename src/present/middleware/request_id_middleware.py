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

# Configure logger without the "request_tracker" prefix
logger = logging.getLogger("ems")

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
        
        # Store user agent for response log
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

