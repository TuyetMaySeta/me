from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config.config import settings
from src.present.routers.user_router import router as users_router
from src.present.routers.auth_router import router as auth_router
from src.present.routers.health_router import router as health_router
from src.present.middleware.recovery_middleware import RecoveryMiddleware
from src.present.middleware.request_id_middleware import RequestIDMiddleware

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

# Setup centralized logging configuration
from src.log import setup_logging
setup_logging(settings.log_level)

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
