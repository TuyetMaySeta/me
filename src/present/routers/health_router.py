from fastapi import APIRouter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok"}

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with database connection"""
    health_info = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": "unknown",
        "components": {
            "application": "healthy",
            "database": "unknown"
        }
    }
    
    # Check database connection
    try:
        from src.bootstrap.database_bootstrap import database_bootstrap
        
        if database_bootstrap.test_connection():
            health_info["database"] = "connected"
            health_info["components"]["database"] = "healthy"
            
            # Try to get some basic stats
            try:
                with database_bootstrap.engine.connect() as connection:
                    # Check if cv table exists and count records
                    result = connection.execute("SELECT COUNT(*) FROM cv")
                    cv_count = result.fetchone()[0]
                    health_info["database_stats"] = {
                        "cv_count": cv_count
                    }
            except Exception as e:
                logger.warning(f"Could not get database stats: {str(e)}")
                health_info["database_stats"] = {
                    "error": "Could not retrieve stats (tables may not exist)"
                }
        else:
            health_info["status"] = "degraded"
            health_info["database"] = "disconnected" 
            health_info["components"]["database"] = "unhealthy"
            
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_info["status"] = "degraded"
        health_info["database"] = "error"
        health_info["components"]["database"] = "unhealthy"
        health_info["database_error"] = str(e)
    
    return health_info

@router.get("/health/database")
async def database_health_check():
    """Dedicated database health check endpoint"""
    try:
        from src.bootstrap.database_bootstrap import database_bootstrap
        
        # Test basic connection
        connection_test = database_bootstrap.test_connection()
        
        if not connection_test:
            return {
                "database": "failed",
                "status": "Connection test failed",
                "connected": False
            }
        
        # Test table existence and get stats
        try:
            with database_bootstrap.engine.connect() as connection:
                # Check tables exist
                tables_result = connection.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name IN ('cv', 'languages', 'technical_skills', 'soft_skills', 'projects')
                """)
                existing_tables = [row[0] for row in tables_result.fetchall()]
                
                # Get record counts if tables exist
                stats = {}
                if 'cv' in existing_tables:
                    cv_count = connection.execute("SELECT COUNT(*) FROM cv").fetchone()[0]
                    stats["cv_count"] = cv_count
                
                if 'languages' in existing_tables:
                    lang_count = connection.execute("SELECT COUNT(*) FROM languages").fetchone()[0]  
                    stats["languages_count"] = lang_count
                
                return {
                    "database": "healthy",
                    "status": "All systems operational",
                    "connected": True,
                    "tables_found": existing_tables,
                    "expected_tables": ['cv', 'languages', 'technical_skills', 'soft_skills', 'projects'],
                    "stats": stats,
                    "migration_needed": len(existing_tables) == 0
                }
                
        except Exception as e:
            return {
                "database": "connected_but_issues",
                "status": f"Connected but cannot query tables: {str(e)}",
                "connected": True,
                "suggestion": "Run 'python migrate.py upgrade' to create tables"
            }
            
    except Exception as e:
        return {
            "database": "error",
            "status": f"Database check failed: {str(e)}",
            "connected": False,
            "suggestions": [
                "Check if PostgreSQL is running: docker-compose ps",
                "Start database: docker-compose up -d", 
                "Verify DATABASE_URL in .env file"
            ]
        }