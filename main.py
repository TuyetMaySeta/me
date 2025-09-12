from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from src.config.config import settings
from src.present.routers.health_router import router as health_router
from src.present.routers.cv_router import router as cv_router
from src.present.routers.cv_related_router import router as cv_related_router
from src.present.middleware.request_id_middleware import RequestIDMiddleware
from src.common.exception.exceptions import EMSException
from src.common.log import setup_logging

from sqlalchemy import text
from src.bootstrap.database_bootstrap import database_bootstrap

logger = logging.getLogger(__name__)

# -----------------------------
# Custom Exception Handler
# -----------------------------
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

    if exc.error_code == "DUPLICATE_EMAIL":
        error_response["error"]["suggestion"] = "Please use a different email."
        error_response["error"]["action"] = "Use unique email."

    elif exc.error_code == "DUPLICATE_SETA_ID":
        error_response["error"]["suggestion"] = "Please use a different SETA ID."
        error_response["error"]["action"] = "Use unique SETA ID."

    elif exc.error_code == "CV_NOT_FOUND":
        error_response["error"]["suggestion"] = "Check CV ID or if deleted."
        error_response["error"]["action"] = "Verify CV ID."

    elif "VALIDATION" in exc.error_code:
        error_response["error"]["suggestion"] = "Check your input data."
        error_response["error"]["action"] = "Correct the data."

    return JSONResponse(
        status_code=exc.http_status,
        content=error_response
    )

# -----------------------------
# Database Check Functions
# -----------------------------
def check_database_connection() -> bool:
    print("🔄 Checking database connection...")
    if database_bootstrap.test_connection():
        print("✅ Database connection successful!")
        print(f"📊 Database URL: {settings.database_url}")
        return True
    else:
        print("❌ Database connection failed! Check DB server and .env")
        return False

def check_database_tables() -> bool:
    print("🔄 Checking required tables...")
    try:
        with database_bootstrap.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'cv'"
            ))
            table_exists = result.scalar() > 0
            if table_exists:
                cv_count = conn.execute(text("SELECT COUNT(*) FROM cv")).scalar()
                print(f"✅ CV table exists. Records: {cv_count}")
                return True
            else:
                print("⚠️ CV table not found. Run migrations: python migrate.py upgrade")
                return False
    except Exception as e:
        print(f"⚠️ Could not check tables: {e}")
        return False

# -----------------------------
# Lifespan
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*60)
    print("🚀 Starting EMS CV Management System...")
    print("="*60)

    db_connected = check_database_connection()
    if db_connected:
        tables_exist = check_database_tables()
        if not tables_exist:
            print("\n⚠️ Tables missing. App may not work properly until migrations run.\n")
    else:
        print("\n❌ Critical: DB connection failed. App will start but may not work.\n")

    try:
        from src.bootstrap.application_bootstrap import app_bootstrap
        print("✅ Application layers initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize app layers: {e}")
        raise

    print("\n🎉 EMS CV Management System is ready!")
    print(f"📡 Server: http://{settings.host}:{settings.port}")
    print(f"📚 Docs: http://{settings.host}:{settings.port}/ems/docs")
    print(f"🔍 Health Check: http://{settings.host}:{settings.port}/ems/api/v1/health")
    print(f"🧩 CV Components: http://{settings.host}:{settings.port}/ems/api/v1/cv-components")
    print("="*60 + "\n")

    yield

    print("\n🛑 Shutting down EMS CV Management System...")
    try:
        app_bootstrap.shutdown()
        print("✅ Cleanup completed successfully!")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title="EMS CV Management System",
    version=settings.app_version,
    description="CV Management System with FastAPI + PostgreSQL",
    debug=settings.debug,
    lifespan=lifespan
)

# Logging
setup_logging(settings.log_level)

# Middlewares
app.add_middleware(RequestIDMiddleware, header_name="X-Request-ID")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
app.add_exception_handler(EMSException, ems_exception_handler)

# Routers
api_router = APIRouter(prefix=settings.api_prefix)
api_router.include_router(health_router)
api_router.include_router(cv_router)
api_router.include_router(cv_related_router)
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "EMS CV Management System",
        "version": settings.app_version,
        "api_prefix": settings.api_prefix,
        "docs": f"{settings.api_prefix.replace('/api/v1','')}/docs",
        "endpoints": {
            "health": f"{settings.api_prefix}/health",
            "cvs": f"{settings.api_prefix}/cvs",
            "cv_components": f"{settings.api_prefix}/cv-components"
        }
    }

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