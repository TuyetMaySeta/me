from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config.config import settings
from src.present.routers.user_router import router as users_router
from src.present.routers.auth_router import router as auth_router
from src.present.routers.system_router import router as system_router
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

# Suppress all other logs - keep only middleware request tracking
import logging
# Suppress uvicorn logs
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.setLevel(logging.CRITICAL)

# Suppress SQLAlchemy logs
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.CRITICAL)

# Allow ERROR logs but suppress INFO/DEBUG
app_logger = logging.getLogger()
app_logger.setLevel(logging.ERROR)

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

# Include routers
app.include_router(system_router, prefix="/ems")  # System endpoints (health, etc.)
app.include_router(users_router, prefix="/ems/api/v1")  # Users API
app.include_router(auth_router, prefix="/ems/api/v1")  # Auth API


# API documentation available at /ems/docs


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
