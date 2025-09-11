from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config.config import settings
from src.present.routers.user_router import router as users_router
from src.present.routers.auth_router import router as auth_router
from src.present.routers.health_router import router as health_router
from src.present.middleware.recovery_middleware import RecoveryMiddleware
from src.present.middleware.request_id_middleware import RequestIDMiddleware, setup_request_logging, setup_application_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup with recovery
    # Initialize database silently
    from src.bootstrap.database_bootstrap import database_bootstrap
    database_bootstrap.test_connection()
    yield
    
    # Graceful shutdown - close database connections silently
    try:
        database_bootstrap.dispose()
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

# Setup request logging and suppress all other logs
setup_request_logging()

# Setup application logging with request ID formatting
from src.present.middleware.request_id_middleware import setup_application_logging
setup_application_logging()

# Suppress all other logs - keep only middleware request tracking
import logging
# Suppress uvicorn logs
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.setLevel(logging.CRITICAL)

# Suppress SQLAlchemy logs completely
sqlalchemy_engine_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_engine_logger.setLevel(logging.CRITICAL)

# Also suppress SQLAlchemy connection pool logs
sqlalchemy_pool_logger = logging.getLogger("sqlalchemy.pool")
sqlalchemy_pool_logger.setLevel(logging.CRITICAL)

# Suppress general SQLAlchemy logs
sqlalchemy_logger = logging.getLogger("sqlalchemy")
sqlalchemy_logger.setLevel(logging.CRITICAL)

# Allow DEBUG and all higher level logs
app_logger = logging.getLogger()
app_logger.setLevel(logging.DEBUG)

# Suppress database bootstrap logs
db_logger = logging.getLogger("src.bootstrap.database_bootstrap")
db_logger.setLevel(logging.CRITICAL)

# Add middlewares (order matters - last added runs first)
# 1. Request ID middleware (outermost - tracks all requests)
app.add_middleware(RequestIDMiddleware, header_name="X-Request-ID")

# 2. Recovery middleware (wraps business logic)
app.add_middleware(RecoveryMiddleware, max_retries=3, base_delay=1.0)

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
        reload=settings.debug
    )
