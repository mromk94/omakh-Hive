"""
MySQL Database Connection and Session Management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os
from dotenv import load_dotenv
import structlog

# Load environment variables from .env file
load_dotenv()

# Setup logger
logger = structlog.get_logger(__name__)

# Database configuration from environment variables
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Successtrain2025@@')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'omk-hive1')

# URL-encode password to handle special characters like @ 
from urllib.parse import quote_plus
encoded_password = quote_plus(DB_PASSWORD)

# MySQL connection URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

logger.info("Database configuration loaded", db_name=DB_NAME, db_host=DB_HOST)

# Create engine with optimized connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Verify connections before using
    pool_recycle=3600,       # Recycle connections after 1 hour
    pool_size=10,            # Number of connections to maintain
    max_overflow=20,         # Additional connections when pool is full
    pool_timeout=30,         # Timeout for getting connection from pool
    echo=False,              # Set to True for SQL debugging
    pool_reset_on_return='rollback',  # Reset connections on return to pool
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database - create all tables
    """
    try:
        # Test connection first
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info("✅ Database connection successful")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
        
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        print(f"❌ Database initialization failed: {e}")
        print("⚠️  Please check:")
        print(f"   - MySQL is running")
        print(f"   - Database '{DB_NAME}' exists")
        print(f"   - Credentials are correct (DB_USER={DB_USER}, DB_HOST={DB_HOST})")
        print(f"   - .env file is properly configured")
        raise
