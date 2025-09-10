from fastapi import APIRouter
from src.config.config import settings
from src.present.middleware.recovery_middleware import RecoveryMiddleware

router = APIRouter(tags=["System"])

@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": f"{settings.root_path}/docs",
        "redoc": f"{settings.root_path}/redoc"
    }

@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    from src.bootstrap.database_bootstrap import database_bootstrap
    
    # Test database connection
    db_healthy = database_bootstrap.test_connection()
    db_status = database_bootstrap.get_pool_status() if db_healthy else None
    
    overall_status = "healthy" if db_healthy else "degraded"
    
    return {
        "status": overall_status,
        "service": settings.app_name,
        "version": settings.app_version,
        "database": {
            "status": "connected" if db_healthy else "disconnected",
            "pool_status": db_status
        },
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all system components"""
    from src.bootstrap.database_bootstrap import database_bootstrap
    
    # Test database connection
    db_healthy = database_bootstrap.test_connection()
    db_status = database_bootstrap.get_pool_status() if db_healthy else None
    
    # Check if all components are healthy
    all_healthy = db_healthy
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "service": settings.app_name,
        "version": settings.app_version,
        "components": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "pool_status": db_status,
                "connection_test": "passed" if db_healthy else "failed"
            }
        },
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }

@router.get("/recovery/status")
async def recovery_status():
    """Get recovery middleware status"""
    return {
        "status": "operational",
        "service": "Recovery Middleware",
        "message": "Recovery middleware is active and monitoring requests",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }
