import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import DisconnectionError, OperationalError

logger = logging.getLogger(__name__)


class RecoveryMiddleware(BaseHTTPMiddleware):
    """Global recovery middleware for all router operations"""
    
    def __init__(self, app, max_retries: int = 3, base_delay: float = 1.0):
        super().__init__(app)
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.circuit_breaker = {}
        self.failure_counts = {}
        self.circuit_timeout = 60  # seconds
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Wrap all requests with recovery logic"""
        
        # Skip health checks and static endpoints
        if request.url.path in ["/health", "/health/detailed", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get endpoint identifier
        endpoint_key = f"{request.method}:{request.url.path}"
        
        # Check circuit breaker
        if self._is_circuit_open(endpoint_key):
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service temporarily unavailable",
                    "message": "Circuit breaker is open",
                    "endpoint": endpoint_key,
                    "retry_after": self.circuit_timeout
                }
            )
        
        # Retry logic for database-related operations
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                response = await call_next(request)
                
                # Reset failure count on success
                if endpoint_key in self.failure_counts:
                    self.failure_counts[endpoint_key] = 0
                
                return response
                
            except (DisconnectionError, OperationalError) as e:
                last_exception = e
                self._record_failure(endpoint_key)
                
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Request {endpoint_key} failed on attempt {attempt + 1}: {e}. "
                        f"Retrying in {delay} seconds..."
                    )
                    await self._sleep(delay)
                else:
                    logger.error(
                        f"Request {endpoint_key} failed after {self.max_retries} attempts: {e}"
                    )
                    break
                    
            except Exception as e:
                # For non-database errors, don't retry
                logger.error(f"Non-retryable error for {endpoint_key}: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal server error",
                        "message": str(e),
                        "endpoint": endpoint_key
                    }
                )
        
        # All retries failed
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service unavailable",
                "message": f"Request failed after {self.max_retries} attempts",
                "endpoint": endpoint_key,
                "last_error": str(last_exception) if last_exception else "Unknown error"
            }
        )
    
    def _record_failure(self, endpoint_key: str):
        """Record a failure for circuit breaker"""
        if endpoint_key not in self.failure_counts:
            self.failure_counts[endpoint_key] = 0
        
        self.failure_counts[endpoint_key] += 1
        
        # Open circuit if threshold reached
        if self.failure_counts[endpoint_key] >= 5:  # 5 failures threshold
            self.circuit_breaker[endpoint_key] = time.time()
            logger.error(f"Circuit breaker opened for {endpoint_key}")
    
    def _is_circuit_open(self, endpoint_key: str) -> bool:
        """Check if circuit breaker is open for endpoint"""
        if endpoint_key not in self.circuit_breaker:
            return False
        
        # Check if circuit should be reset
        if time.time() - self.circuit_breaker[endpoint_key] > self.circuit_timeout:
            del self.circuit_breaker[endpoint_key]
            if endpoint_key in self.failure_counts:
                self.failure_counts[endpoint_key] = 0
            logger.info(f"Circuit breaker reset for {endpoint_key}")
            return False
        
        return True
    
    async def _sleep(self, seconds: float):
        """Async sleep for retry delays"""
        import asyncio
        await asyncio.sleep(seconds)
    
    def get_circuit_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            "open_circuits": list(self.circuit_breaker.keys()),
            "failure_counts": self.failure_counts.copy(),
            "circuit_timeout": self.circuit_timeout
        }
