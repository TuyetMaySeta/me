import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from src.config.config import settings

logger = logging.getLogger(__name__)

# Create base class for models
Base = declarative_base()

class DatabaseBootstrap:
    """Database initialization and session management"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database engine and session"""
        try:
            # Create engine
            self.engine = create_engine(
                settings.database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False  # True nếu muốn debug SQL
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine,
                future=True   # SQLAlchemy 2.x
            )
            
            logger.info("Database bootstrap initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def get_base(self):
        """Get SQLAlchemy base class"""
        return Base
    
    def get_session(self):
        """Get database session (generator for dependency injection)"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                # SQLAlchemy 2.x requires text() for raw SQL
                connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            return False

# Global singleton
database_bootstrap = DatabaseBootstrap()
