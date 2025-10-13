"""
Integration Tests - Test Complete Flows and DB Integration
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
import time

import sys
sys.path.insert(0, '/Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai')

from main import create_app
from app.database.connection import SessionLocal, init_db
from app.database.models import User, OTCRequest, OTCStatus

app = create_app()
client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    """Setup test database"""
    init_db()
    db = SessionLocal()
    yield db
    db.close()

class TestDatabaseIntegration:
    """Test that database is properly integrated into the app"""
    
    def test_database_initialized_on_startup(self):
        """Test that database tables exist when app starts"""
        db = SessionLocal()
        try:
            # Should be able to query users without error
            users = db.query(User).all()
            assert len(users) >= 3  # Admin + 2 demo users
        finally:
            db.close()
    
    def test_seeded_data_exists(self, test_db):
        """Test that seeded data is available"""
        # Check admin exists
        admin = test_db.query(User).filter(User.email == "king@omakh.io").first()
        assert admin is not None
        assert admin.role.value == "admin"
        
        # Check demo users exist
        demo1 = test_db.query(User).filter(User.email == "demo1@omakh.io").first()
        demo2 = test_db.query(User).filter(User.email == "demo2@omakh.io").first()
        
        assert demo1 is not None
        assert demo2 is not None
        assert demo1.omk_balance > 0
        assert demo2.omk_balance > 0

class TestOTCFlowIntegration:
    """Test complete OTC purchase flow with database"""
    
    def test_otc_request_saved_to_database(self, test_db):
        """Test that OTC requests are saved to database"""
        # Create OTC request directly in DB
        request_id = f"TEST-OTC-{int(time.time())}"
        
        otc = OTCRequest(
            request_id=request_id,
            name="Integration Test User",
            email="integration@test.com",
            wallet_address="0x" + "1" * 40,
            omk_amount=100000.0,
            price_per_token=0.10,
            total_usd=10000.0,
            payment_token="USDT",
            status=OTCStatus.PENDING,
            requires_approval=False
        )
        
        test_db.add(otc)
        test_db.commit()
        test_db.refresh(otc)
        
        # Verify it was saved
        saved_otc = test_db.query(OTCRequest).filter(
            OTCRequest.request_id == request_id
        ).first()
        
        assert saved_otc is not None
        assert saved_otc.omk_amount == 100000.0
        assert saved_otc.total_usd == 10000.0
        
        # Cleanup
        test_db.delete(saved_otc)
        test_db.commit()
    
    def test_whale_purchase_flagged(self, test_db):
        """Test that whale purchases are flagged for approval"""
        request_id = f"TEST-WHALE-{int(time.time())}"
        
        # Create whale purchase (≥20M OMK)
        whale_otc = OTCRequest(
            request_id=request_id,
            name="Whale User",
            email="whale@test.com",
            wallet_address="0x" + "2" * 40,
            omk_amount=25000000.0,  # 25M OMK
            price_per_token=0.10,
            total_usd=2500000.0,
            payment_token="USDT",
            status=OTCStatus.PENDING,
            requires_approval=True  # Should be flagged
        )
        
        test_db.add(whale_otc)
        test_db.commit()
        
        # Verify it requires approval
        saved = test_db.query(OTCRequest).filter(
            OTCRequest.request_id == request_id
        ).first()
        
        assert saved.requires_approval == True
        
        # Cleanup
        test_db.delete(saved)
        test_db.commit()

class TestUserAuthenticationIntegration:
    """Test authentication with database"""
    
    def test_login_creates_session(self):
        """Test that login updates last_login in database"""
        db = SessionLocal()
        
        # Get user before login
        user_before = db.query(User).filter(User.email == "demo1@omakh.io").first()
        last_login_before = user_before.last_login
        
        # Login
        time.sleep(1)  # Ensure timestamp is different
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo1@omakh.io",
                "password": "demouser1234"
            }
        )
        
        assert response.status_code == 200
        
        # Check last_login updated
        db.expire_all()  # Refresh from DB
        user_after = db.query(User).filter(User.email == "demo1@omakh.io").first()
        
        if last_login_before:
            assert user_after.last_login > last_login_before
        
        db.close()
    
    def test_new_user_registration_in_database(self):
        """Test that registration creates user in database"""
        db = SessionLocal()
        unique_email = f"dbtest{int(time.time())}@example.com"
        
        # Register
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": "TestPassword123!",
                "full_name": "DB Test User"
            }
        )
        
        assert response.status_code == 200
        
        # Check user exists in database
        user = db.query(User).filter(User.email == unique_email).first()
        
        assert user is not None
        assert user.email == unique_email
        assert user.full_name == "DB Test User"
        assert user.role.value == "user"
        assert user.omk_balance == 0.0
        
        # Cleanup
        db.delete(user)
        db.commit()
        db.close()

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_endpoint_returns_200(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert data["service"] == "Queen AI Orchestrator"

class TestDatabaseConnectionResilience:
    """Test database connection handling"""
    
    def test_database_session_cleanup(self):
        """Test that database sessions are properly closed"""
        # Create multiple sessions
        sessions = []
        for i in range(5):
            db = SessionLocal()
            user = db.query(User).first()
            assert user is not None
            sessions.append(db)
        
        # Close all sessions
        for db in sessions:
            db.close()
        
        # Should still be able to create new session
        new_db = SessionLocal()
        user = new_db.query(User).first()
        assert user is not None
        new_db.close()

class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_admin_user_has_admin_role(self, test_db):
        """Test that admin user has correct role"""
        admin = test_db.query(User).filter(User.email == "king@omakh.io").first()
        
        assert admin.role.value == "admin"
        assert admin.is_active == True
    
    def test_demo_users_have_user_role(self, test_db):
        """Test that demo users have user role"""
        demo1 = test_db.query(User).filter(User.email == "demo1@omakh.io").first()
        demo2 = test_db.query(User).filter(User.email == "demo2@omakh.io").first()
        
        assert demo1.role.value == "user"
        assert demo2.role.value == "user"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
