from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DisconnectionError, OperationalError
from sqlalchemy.pool import QueuePool
import time
import logging
from src.config.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database engine with enhanced recovery settings
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,                    # Number of connections to maintain
    max_overflow=20,                 # Additional connections beyond pool_size
    pool_pre_ping=True,              # Test connections before use
    pool_recycle=300,                # Recycle connections every 5 minutes
    pool_timeout=30,                 # Timeout for getting connection from pool
    echo=settings.debug,
    # Recovery settings
    connect_args={
        "connect_timeout": 10,       # Connection timeout
        "application_name": "ems_fastapi"
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


# Dependency to get database session with retry logic
def get_db():
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            # Test the connection
            db.execute("SELECT 1")
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


def test_database_connection() -> bool:
    """Test database connection and return status"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_database_status() -> dict:
    """Get database connection pool status"""
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid()
    }
