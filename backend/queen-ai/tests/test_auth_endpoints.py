"""
Unit Tests for Authentication API Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import sys
sys.path.insert(0, '/Users/mac/CascadeProjects/omakh-Hive/backend/queen-ai')

from main import create_app
from app.database.connection import SessionLocal, init_db
from app.database.models import User

# Create test client
app = create_app()
client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    """Setup test database"""
    init_db()
    db = SessionLocal()
    yield db
    db.close()

class TestLoginEndpoint:
    """Test login endpoint"""
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "king@omakh.io",
                "password": "Successtrain2025@@"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "king@omakh.io"
        assert data["user"]["role"] == "admin"
        assert data["token_type"] == "bearer"
    
    def test_demo_user_login_success(self):
        """Test successful demo user login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo1@omakh.io",
                "password": "demouser1234"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["user"]["email"] == "demo1@omakh.io"
        assert data["user"]["role"] == "user"
        assert data["user"]["omk_balance"] == 50000.0
    
    def test_login_wrong_password(self):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "king@omakh.io",
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123"
            }
        )
        
        assert response.status_code == 401

class TestRegisterEndpoint:
    """Test registration endpoint"""
    
    def test_register_new_user(self):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"newuser{datetime.now().timestamp()}@example.com",
                "password": "NewPassword123!",
                "full_name": "New Test User"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["role"] == "user"
        assert data["user"]["is_active"] == True
    
    def test_register_duplicate_email(self):
        """Test registration with existing email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "king@omakh.io",  # Already exists
                "password": "SomePassword123!",
                "full_name": "Duplicate User"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

class TestGetCurrentUserEndpoint:
    """Test get current user endpoint"""
    
    def test_get_current_user_with_valid_token(self):
        """Test getting current user with valid token"""
        # First login to get token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo1@omakh.io",
                "password": "demouser1234"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Now get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "demo1@omakh.io"
        assert data["role"] == "user"
        assert "omk_balance" in data
    
    def test_get_current_user_without_token(self):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # Forbidden without token
    
    def test_get_current_user_with_invalid_token(self):
        """Test getting current user with invalid token"""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401

class TestLogoutEndpoint:
    """Test logout endpoint"""
    
    def test_logout_with_valid_token(self):
        """Test logout with valid token"""
        # Login first
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo1@omakh.io",
                "password": "demouser1234"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()

class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    def test_complete_flow(self):
        """Test complete auth flow: register -> login -> get user -> logout"""
        import time
        unique_email = f"flowtest{int(time.time())}@example.com"
        
        # 1. Register
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": unique_email,
                "password": "FlowTest123!",
                "full_name": "Flow Test User"
            }
        )
        assert register_response.status_code == 200
        register_token = register_response.json()["access_token"]
        
        # 2. Get user info with register token
        me_response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {register_token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == unique_email
        
        # 3. Login with same credentials
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": unique_email,
                "password": "FlowTest123!"
            }
        )
        assert login_response.status_code == 200
        login_token = login_response.json()["access_token"]
        
        # 4. Get user info with login token
        me_response2 = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_token}"}
        )
        assert me_response2.status_code == 200
        
        # 5. Logout
        logout_response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {login_token}"}
        )
        assert logout_response.status_code == 200

if __name__ == "__main__":
    from datetime import datetime
    pytest.main([__file__, "-v"])
