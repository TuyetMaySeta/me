# src/present/routers/health_router.py
from fastapi import APIRouter
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "EMS Employee Management System"
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check với database connection"""
    health_info = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "EMS Employee Management System",
        "database": "unknown",
        "components": {
            "application": "healthy",
            "database": "unknown",
            "employee_service": "healthy"
        }
    }
    
    # Check database connection
    try:
        from src.bootstrap.database_bootstrap import database_bootstrap
        
        if database_bootstrap.test_connection():
            health_info["database"] = "connected"
            health_info["components"]["database"] = "healthy"
            
            # Try to get employee statistics
            try:
                from sqlalchemy import text
                with database_bootstrap.engine.connect() as connection:
                    # Check if employees table exists and count records
                    try:
                        result = connection.execute(text("SELECT COUNT(*) FROM employees"))
                        employee_count = result.fetchone()[0]
                        
                        # Count related data
                        contact_count = connection.execute(text("SELECT COUNT(*) FROM employee_contacts")).fetchone()[0]
                        document_count = connection.execute(text("SELECT COUNT(*) FROM employee_documents")).fetchone()[0]
                        language_count = connection.execute(text("SELECT COUNT(*) FROM languages")).fetchone()[0]
                        skill_count = connection.execute(text("SELECT COUNT(*) FROM employee_technical_skills")).fetchone()[0]
                        project_count = connection.execute(text("SELECT COUNT(*) FROM employee_projects")).fetchone()[0]
                        
                        health_info["database_stats"] = {
                            "employees": employee_count,
                            "contacts": contact_count,
                            "documents": document_count,
                            "languages": language_count,
                            "technical_skills": skill_count,
                            "projects": project_count,
                            "total_records": employee_count + contact_count + document_count + language_count + skill_count + project_count
                        }
                        
                    except Exception as table_error:
                        health_info["database_stats"] = {
                            "error": f"Tables not found or not accessible: {str(table_error)}",
                            "suggestion": "Run 'python migrate.py upgrade' to create tables"
                        }
                        
            except Exception as e:
                logger.warning(f"Could not get database stats: {str(e)}")
                health_info["database_stats"] = {
                    "error": "Could not retrieve stats",
                    "details": str(e)
                }
        else:
            health_info["status"] = "degraded"
            health_info["database"] = "disconnected" 
            health_info["components"]["database"] = "unhealthy"
            health_info["database_stats"] = {
                "error": "Database connection failed"
            }
            
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_info["status"] = "degraded"
        health_info["database"] = "error"
        health_info["components"]["database"] = "unhealthy"
        health_info["database_error"] = str(e)
        health_info["suggestions"] = [
            "Check if PostgreSQL is running: docker-compose ps",
            "Start database: docker-compose up -d",
            "Check DATABASE_URL in .env file"
        ]
    
    return health_info

@router.get("/health/database")
async def database_health_check():
    """Dedicated database health check endpoint"""
    try:
        from src.bootstrap.database_bootstrap import database_bootstrap
        from sqlalchemy import text
        
        # Test basic connection
        connection_test = database_bootstrap.test_connection()
        
        if not connection_test:
            return {
                "database": "failed",
                "status": "Connection test failed",
                "connected": False,
                "suggestions": [
                    "Check if PostgreSQL is running",
                    "Verify DATABASE_URL in .env",
                    "Run: docker-compose up -d"
                ]
            }
        
        # Test table existence and get stats
        try:
            with database_bootstrap.engine.connect() as connection:
                # Check main tables exist
                main_tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('employees')
                """)
                main_tables = [row[0] for row in connection.execute(main_tables_query).fetchall()]
                
                # Check related tables
                related_tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN (
                        'employee_contacts', 'employee_documents', 
                        'employee_education', 'employee_certifications', 'employee_profiles',
                        'languages', 'employee_technical_skills', 'employee_projects', 'employee_children'
                    )
                """)
                related_tables = [row[0] for row in connection.execute(related_tables_query).fetchall()]
                
                # Get record counts for existing tables
                stats = {}
                all_tables = main_tables + related_tables
                
                for table in all_tables:
                    try:
                        count_result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = count_result.fetchone()[0]
                        stats[f"{table}_count"] = count
                    except Exception as e:
                        stats[f"{table}_error"] = str(e)
                
                return {
                    "database": "healthy",
                    "status": "All systems operational",
                    "connected": True,
                    "tables": {
                        "main_tables": main_tables,
                        "related_tables": related_tables,
                        "total_found": len(all_tables)
                    },
                    "stats": stats,
                    "migration_status": "complete" if len(main_tables) > 0 else "needed"
                }
                
        except Exception as e:
            return {
                "database": "connected_but_issues",
                "status": f"Connected but cannot query tables: {str(e)}",
                "connected": True,
                "suggestion": "Run 'python migrate.py upgrade' to create/update tables",
                "error": str(e)
            }
            
    except Exception as e:
        return {
            "database": "error",
            "status": f"Database check failed: {str(e)}",
            "connected": False,
            "suggestions": [
                "Check if PostgreSQL is running: docker-compose ps",
                "Start database: docker-compose up -d", 
                "Verify DATABASE_URL in .env file",
                "Check database credentials and permissions"
            ],
            "error": str(e)
        }

@router.get("/health/system")
async def system_health_check():
    """System overview health check"""
    try:
        from src.bootstrap.application_bootstrap import app_bootstrap
        health = app_bootstrap.health_check()
        
        return {
            "system": "EMS Employee Management System",
            "timestamp": datetime.utcnow().isoformat(),
            **health
        }
        
    except Exception as e:
        return {
            "system": "EMS Employee Management System", 
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        }
