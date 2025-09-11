import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DisconnectionError, OperationalError
from sqlalchemy.pool import QueuePool
import time
from src.config.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseBootstrap:
    """Centralized database initialization and management"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.Base = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database engine and session"""
        try:
            # Create database engine with enhanced recovery settings
            self.engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=10,                    # Number of connections to maintain
                max_overflow=20,                 # Additional connections beyond pool_size
                pool_pre_ping=True,              # Test connections before use
                pool_recycle=300,                # Recycle connections every 5 minutes
                pool_timeout=30,                 # Timeout for getting connection from pool
                echo=False,                      # Disable SQL query logging
                # Recovery settings
                connect_args={
                    "connect_timeout": 10,       # Connection timeout
                    "application_name": "ems_fastapi"
                }
            )
            
            # Create SessionLocal class
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create Base class for models
            self.Base = declarative_base()
            
            logger.info("Database engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_session(self):
        """Get database session with retry logic"""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                db = self.SessionLocal()
                # Test the connection
                from sqlalchemy import text
                db.execute(text("SELECT 1"))
                yield db
                break
            except (DisconnectionError, OperationalError) as e:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    logger.error(f"All database connection attempts failed after {max_retries} retries")
                    raise
            except Exception as e:
                logger.error(f"Unexpected database error: {e}")
                raise
            finally:
                if 'db' in locals():
                    db.close()
    
    def test_connection(self) -> bool:
        """Test database connection and return status"""
        try:
            db = self.SessionLocal()
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            db.close()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_pool_status(self) -> dict:
        """Get database connection pool status"""
        if not self.engine:
            return {"error": "Database engine not initialized"}
        
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total_connections": pool.size() + pool.overflow()
        }
    
    def dispose(self):
        """Dispose of database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections disposed")
    
    def get_engine(self):
        """Get database engine"""
        return self.engine
    
    def get_base(self):
        """Get SQLAlchemy Base class"""
        return self.Base


# Global database bootstrap instance
database_bootstrap = DatabaseBootstrap()
