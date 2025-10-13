"""
Unit Tests for Database Connection and Models
"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.connection import SessionLocal, init_db, engine
from app.database.models import User, UserRole, OTCRequest, OTCStatus, SystemConfig
from app.database.auth import get_password_hash, verify_password, create_access_token, decode_token

@pytest.fixture(scope="module")
def db_session():
    """Create test database session"""
    # Initialize database
    init_db()
    
    # Create session
    db = SessionLocal()
    yield db
    
    # Cleanup
    db.close()

class TestDatabaseConnection:
    """Test database connection"""
    
    def test_database_connection(self):
        """Test that database connection works"""
        try:
            from sqlalchemy import text
            db = SessionLocal()
            # Try a simple query
            db.execute(text("SELECT 1"))
            db.close()
            assert True
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")
    
    def test_tables_exist(self, db_session):
        """Test that all tables are created"""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = [
            'users',
            'otc_requests',
            'system_config',
            'transactions',
            'queen_ai_logs',
            'properties',
            'property_investments',
            'analytics'
        ]
        
        for table in required_tables:
            assert table in tables, f"Table '{table}' not found in database"

class TestUserModel:
    """Test User model CRUD operations"""
    
    def test_create_user(self, db_session):
        """Test creating a new user"""
        user = User(
            email="test@example.com",
            password_hash=get_password_hash("TestPassword123!"),
            full_name="Test User",
            role=UserRole.USER,
            is_active=True,
            omk_balance=0.0
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        
        # Cleanup
        db_session.delete(user)
        db_session.commit()
    
    def test_query_user_by_email(self, db_session):
        """Test querying user by email"""
        # Should find admin user created by seed
        user = db_session.query(User).filter(User.email == "king@omakh.io").first()
        
        assert user is not None
        assert user.email == "king@omakh.io"
        assert user.role == UserRole.ADMIN
        assert user.is_active == True
    
    def test_query_demo_users(self, db_session):
        """Test that demo users exist"""
        demo1 = db_session.query(User).filter(User.email == "demo1@omakh.io").first()
        demo2 = db_session.query(User).filter(User.email == "demo2@omakh.io").first()
        
        assert demo1 is not None
        assert demo2 is not None
        assert demo1.omk_balance == 50000.0
        assert demo2.omk_balance == 100000.0

class TestOTCRequestModel:
    """Test OTC Request model"""
    
    def test_create_otc_request(self, db_session):
        """Test creating OTC request"""
        otc = OTCRequest(
            request_id="TEST-001",
            name="Test User",
            email="test@example.com",
            wallet_address="0x1234567890123456789012345678901234567890",
            omk_amount=100000.0,
            total_usd=10000.0,
            payment_token="USDT",
            status=OTCStatus.PENDING
        )
        
        db_session.add(otc)
        db_session.commit()
        db_session.refresh(otc)
        
        assert otc.id is not None
        assert otc.request_id == "TEST-001"
        assert otc.omk_amount == 100000.0
        
        # Cleanup
        db_session.delete(otc)
        db_session.commit()

class TestSystemConfigModel:
    """Test System Config model"""
    
    def test_query_system_config(self, db_session):
        """Test querying system configuration"""
        # Should find seeded configs
        configs = db_session.query(SystemConfig).all()
        
        assert len(configs) >= 6  # At least 6 configs seeded
        
        # Check specific configs
        otc_phase = db_session.query(SystemConfig).filter(
            SystemConfig.key == "otc_phase"
        ).first()
        
        assert otc_phase is not None
        assert "phase" in otc_phase.value

class TestAuthentication:
    """Test authentication functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert hashed != password  # Should be hashed
        assert verify_password(password, hashed)  # Should verify correctly
        assert not verify_password("WrongPassword", hashed)  # Should fail with wrong password
    
    def test_jwt_token_creation(self):
        """Test JWT token creation"""
        data = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_jwt_token_decoding(self):
        """Test JWT token decoding"""
        data = {"sub": "test@example.com", "role": "user"}
        token = create_access_token(data)
        
        decoded = decode_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["role"] == "user"
    
    def test_invalid_token_decoding(self):
        """Test decoding invalid token"""
        invalid_token = "invalid.token.here"
        decoded = decode_token(invalid_token)
        
        assert decoded is None

class TestDatabaseRelations:
    """Test database relationships"""
    
    def test_user_otc_relation(self, db_session):
        """Test linking OTC request to user"""
        # Get existing user
        user = db_session.query(User).filter(User.email == "demo1@omakh.io").first()
        
        # Create OTC request linked to user
        otc = OTCRequest(
            request_id="TEST-REL-001",
            user_id=user.id,
            name=user.full_name,
            email=user.email,
            wallet_address="0x1234567890123456789012345678901234567890",
            omk_amount=50000.0,
            total_usd=5000.0,
            status=OTCStatus.PENDING
        )
        
        db_session.add(otc)
        db_session.commit()
        
        # Query back and verify
        otc_query = db_session.query(OTCRequest).filter(
            OTCRequest.request_id == "TEST-REL-001"
        ).first()
        
        assert otc_query.user_id == user.id
        
        # Cleanup
        db_session.delete(otc_query)
        db_session.commit()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
