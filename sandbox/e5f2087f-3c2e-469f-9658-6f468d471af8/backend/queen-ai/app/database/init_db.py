"""
Database Initialization Script
Run this to create database and seed initial data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database.connection import init_db, SessionLocal
from app.database.seed import seed_all

def main():
    print("🔧 Initializing database...")
    
    try:
        # Create all tables
        init_db()
        
        # Seed initial data
        db = SessionLocal()
        try:
            seed_all(db)
        finally:
            db.close()
        
        print("\n✅ Database initialization complete!")
        print("\n📝 Admin Login:")
        print("   Email: king@omakh.io")
        print("   Password: Successtrain2025@@")
        print("\n📝 Demo Users:")
        print("   Email: demo1@omakh.io / demo2@omakh.io")
        print("   Password: demouser1234")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
