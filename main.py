from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from src.present.routers.auth_router import router as auth_router
from src.config.config import settings
from src.present.routers.health_router import router as health_router
from src.present.routers.employee_router import router as employee_router
from src.present.middleware.request_id_middleware import RequestIDMiddleware
from src.present.middleware.jwt_middleware import JWTMiddleware
from src.common.exception.exceptions import EMSException
from src.common.log import setup_logging

from sqlalchemy import text

logger = logging.getLogger(__name__)


async def ems_exception_handler(request: Request, exc: EMSException) -> JSONResponse:
    logger.warning(f"EMS Exception: {exc.error_code} - {exc.message}")

    error_response = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "http_status": exc.http_status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    }


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="EMS Employee Management System",
    version=settings.app_version,
    description="""
    **Employee Management System** 
    """,
    debug=settings.debug,
    docs_url="/ems/api/v1/docs",
    redoc_url="/ems/api/v1/redoc",
    openapi_url="/ems/api/v1/openapi.json"
)

# Logging setup
setup_logging(settings.log_level)

# Middleware
app.add_middleware(RequestIDMiddleware, header_name="X-Request-ID")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(JWTMiddleware)
# Exception handler
app.add_exception_handler(EMSException, ems_exception_handler)

# API Routes
api_router = APIRouter(prefix=settings.api_prefix)
api_router.include_router(health_router)  
api_router.include_router(employee_router)  # Employee router tự có tags
api_router.include_router(auth_router)  # Auth router tự có tags
app.include_router(api_router)

# -----------------------------
# Run Uvicorn
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        access_log=True
    )
