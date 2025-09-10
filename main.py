from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config.config import settings
from src.present.routers.user_router import router as users_router
from src.present.routers.auth_router import router as auth_router
from src.present.middleware.recovery_middleware import RecoveryMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup with recovery
    print("\n" + "="*60)
    print("EMS FastAPI Server - Starting up...")
    print("="*60)
    
    # Test database connection on startup
    from src.bootstrap.database_bootstrap import database_bootstrap
    
    max_startup_retries = 5
    retry_delay = 2
    
    for attempt in range(max_startup_retries):
        if database_bootstrap.test_connection():
            print("Database connection established successfully")
            db_status = database_bootstrap.get_pool_status()
            print(f"Database pool status: {db_status}")
            break
        else:
            print(f"Database connection attempt {attempt + 1} failed")
            if attempt < max_startup_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
            else:
                print("WARNING: Database connection failed after all retries")
                print("Server will start but database operations may fail")
    
    print_routes()
    yield
    
    # Graceful shutdown
    print("\n" + "="*60)
    print("EMS FastAPI Server - Shutting down gracefully...")
    print("="*60)
    
    # Close database connections
    try:
        print("Closing database connections...")
        database_bootstrap.dispose()
        print("Database connections closed successfully")
    except Exception as e:
        print(f"Error closing database connections: {e}")
    
    print("Server shutdown complete")
    print("="*60 + "\n")


# Create FastAPI instance with prefix for ingress
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A FastAPI server with SQLAlchemy, Alembic, and PostgreSQL using 3-layer architecture",
    debug=settings.debug,
    root_path=settings.root_path,  # Prefix from environment
    lifespan=lifespan
)

# Add recovery middleware (first, so it wraps everything)
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
app.include_router(users_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


def print_routes():
    """Dynamically print all available routes to console"""
    print("\n" + "="*60)
    print("EMS FastAPI Server - Available Routes")
    print("="*60)
    print(f"Base URL: http://{settings.host}:{settings.port}{settings.root_path}")
    print(f"API Docs: http://{settings.host}:{settings.port}{settings.root_path}/docs")
    print(f"ReDoc: http://{settings.host}:{settings.port}{settings.root_path}/redoc")
    print("-"*60)
    
    # Group routes by tags
    routes_by_tag = {}
    total_routes = 0
    
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = [method for method in route.methods if method != 'HEAD']
            if methods:
                # Get tags from route
                tags = getattr(route, 'tags', ['system'])
                tag = tags[0] if tags else 'system'
                
                if tag not in routes_by_tag:
                    routes_by_tag[tag] = []
                
                for method in methods:
                    routes_by_tag[tag].append({
                        'method': method,
                        'path': route.path
                    })
                    total_routes += 1
    
    # Print routes grouped by tags
    for tag, routes in routes_by_tag.items():
        print(f"{tag.upper()} ENDPOINTS:")
        for route in routes:
            method = route['method'].ljust(6)
            path = route['path']
            print(f"  {method} {path}")
        print()
    
    print("="*60)
    print(f"Server ready! Total endpoints: {total_routes}")
    print("="*60 + "\n")


# Routes will be printed when server starts


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with database status"""
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


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all system components"""
    from src.bootstrap.database_bootstrap import database_bootstrap
    
    # Test database connection
    db_healthy = database_bootstrap.test_connection()
    db_status = database_bootstrap.get_pool_status() if db_healthy else None
    
    # Get recovery middleware status
    recovery_middleware = None
    for middleware in app.user_middleware:
        if hasattr(middleware, 'cls') and middleware.cls == RecoveryMiddleware:
            recovery_middleware = middleware.kwargs.get('app')
            break
    
    recovery_status = {}
    if recovery_middleware and hasattr(recovery_middleware, 'get_circuit_status'):
        recovery_status = recovery_middleware.get_circuit_status()
    
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
            },
            "api": {
                "status": "healthy",
                "endpoints": len([route for route in app.routes if hasattr(route, 'methods')])
            },
            "recovery": {
                "status": "active",
                "circuit_breaker": recovery_status
            }
        },
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }


@app.get("/recovery/status")
async def recovery_status():
    """Get recovery middleware status"""
    # Find recovery middleware instance
    recovery_middleware = None
    for middleware in app.user_middleware:
        if hasattr(middleware, 'cls') and middleware.cls == RecoveryMiddleware:
            recovery_middleware = middleware.kwargs.get('app')
            break
    
    if not recovery_middleware or not hasattr(recovery_middleware, 'get_circuit_status'):
        return {"error": "Recovery middleware not found"}
    
    return {
        "recovery_middleware": {
            "max_retries": recovery_middleware.max_retries,
            "base_delay": recovery_middleware.base_delay,
            "circuit_timeout": recovery_middleware.circuit_timeout,
            "status": recovery_middleware.get_circuit_status()
        },
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
