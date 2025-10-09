#!/usr/bin/env python3
"""
Database Setup Script

Initializes PostgreSQL database and runs migrations.

Usage:
    python3 setup_database.py
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings
from app.db.base import init_db, engine
from app.db import models
import structlog

logger = structlog.get_logger(__name__)


def setup_database():
    """Setup database - create all tables"""
    logger.info("🗄️  Setting up database...")
    logger.info(f"   Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    try:
        # Create all tables
        init_db()
        logger.info("✅ Database tables created successfully")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"📋 Created {len(tables)} tables:")
        for table in sorted(tables):
            logger.info(f"   - {table}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {str(e)}")
        return False


def verify_connection():
    """Verify database connection"""
    logger.info("🔍 Verifying database connection...")
    
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        logger.error("   Please check:")
        logger.error("   1. PostgreSQL is running: pg_isready")
        logger.error("   2. DATABASE_URL is correct in .env")
        logger.error("   3. Database exists: createdb omk_hive")
        return False


def main():
    """Main setup function"""
    print("\n" + "="*70)
    print("  OMK HIVE - DATABASE SETUP")
    print("="*70 + "\n")
    
    # Step 1: Verify connection
    if not verify_connection():
        print("\n❌ Setup failed - fix connection issues and try again\n")
        return 1
    
    # Step 2: Create tables
    if not setup_database():
        print("\n❌ Setup failed - check errors above\n")
        return 1
    
    print("\n" + "="*70)
    print("  ✅ DATABASE SETUP COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Run migrations: alembic upgrade head")
    print("2. Start the application: python3 main.py")
    print()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
