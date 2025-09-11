from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from src.config.config import settings
from src.present.routers.user_router import router as users_router
from src.present.routers.auth_router import router as auth_router
from src.present.routers.health_router import router as health_router
from src.present.middleware.request_id_middleware import RequestIDMiddleware
from src.common.exception.exceptions import EMSException

logger = logging.getLogger(__name__)


async def ems_exception_handler(request: Request, exc: EMSException) -> JSONResponse:
    """Handle custom EMS exceptions"""
    logger.warning(f"EMS Exception: {exc.error_code} - {exc.message}")
    
    return JSONResponse(
        status_code=exc.http_status,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "http_status": exc.http_status
            }
        }
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Initialize application layers
    from src.bootstrap.application_bootstrap import app_bootstrap
    yield
    
    # Shutdown - Cleanup resources
    try:
        app_bootstrap.shutdown()
    except Exception:
        pass


# Create FastAPI instance with prefix for ingress
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A FastAPI server with SQLAlchemy, Alembic, and PostgreSQL using 3-layer architecture",
    debug=settings.debug,
    lifespan=lifespan
)

# Setup custom logging configuration
from src.common.log import setup_logging
setup_logging(settings.log_level)

# Register exception handler for custom exceptions
app.add_exception_handler(EMSException, ems_exception_handler)

# Add middlewares (order matters - last added runs first)
# Request ID middleware (tracks all requests)
app.add_middleware(RequestIDMiddleware, header_name="X-Request-ID")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create main API router with common prefix
from fastapi import APIRouter
api_router = APIRouter(prefix=settings.api_prefix)

# Include routers under the main API router
api_router.include_router(health_router)    # {api_prefix}/health
api_router.include_router(users_router)     # {api_prefix}/users
api_router.include_router(auth_router)      # {api_prefix}/auth

# Include the main API router in the app
app.include_router(api_router)


# API documentation available at /ems/docs
# All API endpoints available under {settings.api_prefix}/


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=False,  # Disable reload to prevent double initialization
        access_log=False  # Disable uvicorn access logs, use custom request tracking instead
    )
