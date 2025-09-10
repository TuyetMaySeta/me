import time
import logging
from typing import Optional, Callable, Any
from functools import wraps
from sqlalchemy.exc import DisconnectionError, OperationalError

logger = logging.getLogger(__name__)


class RecoveryService:
    """Service for handling system recovery and resilience"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def retry_on_failure(self, exceptions: tuple = (DisconnectionError, OperationalError)):
        """Decorator for retrying operations on database failures"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                
                for attempt in range(self.max_retries):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < self.max_retries - 1:
                            delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                            logger.warning(
                                f"Operation {func.__name__} failed on attempt {attempt + 1}: {e}. "
                                f"Retrying in {delay} seconds..."
                            )
                            time.sleep(delay)
                        else:
                            logger.error(
                                f"Operation {func.__name__} failed after {self.max_retries} attempts: {e}"
                            )
                
                # If we get here, all retries failed
                raise last_exception
            
            return wrapper
        return decorator
    
    def circuit_breaker(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        """Simple circuit breaker pattern"""
        def decorator(func: Callable) -> Callable:
            failure_count = 0
            last_failure_time = 0
            circuit_open = False
            
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                nonlocal failure_count, last_failure_time, circuit_open
                
                current_time = time.time()
                
                # Check if circuit should be reset
                if circuit_open and (current_time - last_failure_time) > recovery_timeout:
                    circuit_open = False
                    failure_count = 0
                    logger.info(f"Circuit breaker for {func.__name__} reset")
                
                # Check if circuit is open
                if circuit_open:
                    logger.warning(f"Circuit breaker open for {func.__name__}")
                    raise Exception(f"Circuit breaker open for {func.__name__}")
                
                try:
                    result = func(*args, **kwargs)
                    # Reset failure count on success
                    failure_count = 0
                    return result
                except Exception as e:
                    failure_count += 1
                    last_failure_time = current_time
                    
                    if failure_count >= failure_threshold:
                        circuit_open = True
                        logger.error(
                            f"Circuit breaker opened for {func.__name__} after {failure_count} failures"
                        )
                    
                    raise e
            
            return wrapper
        return decorator
    
    def health_check(self, check_function: Callable[[], bool]) -> dict:
        """Perform health check and return status"""
        try:
            is_healthy = check_function()
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "timestamp": time.time(),
                "check_function": check_function.__name__
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time(),
                "check_function": check_function.__name__
            }


# Global recovery service instance
recovery_service = RecoveryService(max_retries=3, base_delay=1.0)
