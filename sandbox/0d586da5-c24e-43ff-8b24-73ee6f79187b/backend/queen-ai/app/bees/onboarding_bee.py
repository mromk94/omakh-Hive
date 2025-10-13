"""
OnboardingBee - User Management & Database Operations

Responsibilities:
- User registration and authentication
- Profile management
- Database CRUD operations
- Wallet connection/creation
- KYC/verification status
- User preferences (language, theme, etc.)
- Session management
- Email verification
- Password reset flows
"""
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime, timedelta
import hashlib
import secrets
import re
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class OnboardingBee(BaseBee):
    """
    User Onboarding & Management Bee
    
    Handles all user-related operations:
    - Registration & authentication
    - Profile management
    - Database operations
    - Wallet management
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="OnboardingBee")
        
        # In-memory user store (replace with real database)
        self.users: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.verification_codes: Dict[str, str] = {}
        
        # Stats
        self.total_users = 0
        self.active_sessions = 0
        self.signups_today = 0
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute onboarding task"""
        task_type = task_data.get("type")
        
        # Authentication
        if task_type == "check_email":
            return await self._check_email_exists(task_data)
        elif task_type == "register_user":
            return await self._register_user(task_data)
        elif task_type == "login":
            return await self._login_user(task_data)
        elif task_type == "logout":
            return await self._logout_user(task_data)
        elif task_type == "verify_session":
            return await self._verify_session(task_data)
        
        # Profile Management
        elif task_type == "get_profile":
            return await self._get_user_profile(task_data)
        elif task_type == "update_profile":
            return await self._update_user_profile(task_data)
        elif task_type == "update_preferences":
            return await self._update_preferences(task_data)
        
        # Wallet Management
        elif task_type == "connect_wallet":
            return await self._connect_wallet(task_data)
        elif task_type == "create_wallet":
            return await self._create_wallet(task_data)
        elif task_type == "get_wallet_balance":
            return await self._get_wallet_balance(task_data)
        
        # Password Management
        elif task_type == "change_password":
            return await self._change_password(task_data)
        elif task_type == "reset_password_request":
            return await self._reset_password_request(task_data)
        elif task_type == "reset_password_confirm":
            return await self._reset_password_confirm(task_data)
        
        # Statistics
        elif task_type == "get_stats":
            return await self._get_onboarding_stats(task_data)
        
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    # ============ AUTHENTICATION ============
    
    async def _check_email_exists(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if email already exists"""
        email = data.get("email", "").lower().strip()
        
        if not email:
            return {"success": False, "error": "Email required"}
        
        if not self._is_valid_email(email):
            return {"success": False, "error": "Invalid email format"}
        
        exists = email in self.users
        
        return {
            "success": True,
            "exists": exists,
            "email": email
        }
    
    async def _register_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new user"""
        try:
            email = data.get("email", "").lower().strip()
            password = data.get("password")
            full_name = data.get("full_name", "")
            user_type = data.get("user_type", "explorer")  # explorer, investor, institutional
            language = data.get("language", "en")
            theme = data.get("theme", "light")
            
            # Validation
            if not email or not password:
                return {"success": False, "error": "Email and password required"}
            
            if not self._is_valid_email(email):
                return {"success": False, "error": "Invalid email format"}
            
            if email in self.users:
                return {"success": False, "error": "Email already registered"}
            
            if len(password) < 8:
                return {"success": False, "error": "Password must be at least 8 characters"}
            
            # Hash password
            password_hash = self._hash_password(password)
            
            # Generate user ID
            user_id = self._generate_user_id()
            
            # Create user
            user = {
                "user_id": user_id,
                "email": email,
                "password_hash": password_hash,
                "full_name": full_name,
                "user_type": user_type,
                "language": language,
                "theme": theme,
                "wallet_address": None,
                "wallet_balance_omk": 0,
                "wallet_balance_usd": 0,
                "roi_percentage": 0,
                "kyc_status": "not_started",
                "email_verified": False,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": None,
                "preferences": {
                    "notifications": True,
                    "newsletter": True,
                    "sound_effects": True
                }
            }
            
            self.users[email] = user
            self.total_users += 1
            self.signups_today += 1
            
            logger.info("User registered", email=email, user_type=user_type)
            
            # Create session
            session_token = self._create_session(email)
            
            return {
                "success": True,
                "message": "Registration successful!",
                "user": self._sanitize_user(user),
                "session_token": session_token
            }
            
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _login_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Login existing user"""
        try:
            email = data.get("email", "").lower().strip()
            password = data.get("password")
            
            if not email or not password:
                return {"success": False, "error": "Email and password required"}
            
            # Check if user exists
            if email not in self.users:
                return {"success": False, "error": "Invalid email or password"}
            
            user = self.users[email]
            
            # Verify password
            if not self._verify_password(password, user["password_hash"]):
                return {"success": False, "error": "Invalid email or password"}
            
            # Update last login
            user["last_login"] = datetime.utcnow().isoformat()
            
            # Create session
            session_token = self._create_session(email)
            
            logger.info("User logged in", email=email)
            
            return {
                "success": True,
                "message": f"Welcome back, {user['full_name'] or 'User'}!",
                "user": self._sanitize_user(user),
                "session_token": session_token
            }
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _logout_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Logout user"""
        session_token = data.get("session_token")
        
        if session_token and session_token in self.sessions:
            del self.sessions[session_token]
            self.active_sessions -= 1
            
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    
    async def _verify_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify if session is valid"""
        session_token = data.get("session_token")
        
        if not session_token or session_token not in self.sessions:
            return {"success": False, "valid": False}
        
        session = self.sessions[session_token]
        
        # Check if expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.utcnow() > expires_at:
            del self.sessions[session_token]
            return {"success": False, "valid": False, "error": "Session expired"}
        
        email = session["email"]
        user = self.users.get(email)
        
        return {
            "success": True,
            "valid": True,
            "user": self._sanitize_user(user) if user else None
        }
    
    # ============ PROFILE MANAGEMENT ============
    
    async def _get_user_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get user profile"""
        email = data.get("email", "").lower().strip()
        
        if email not in self.users:
            return {"success": False, "error": "User not found"}
        
        user = self.users[email]
        
        return {
            "success": True,
            "user": self._sanitize_user(user)
        }
    
    async def _update_user_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        email = data.get("email", "").lower().strip()
        
        if email not in self.users:
            return {"success": False, "error": "User not found"}
        
        user = self.users[email]
        
        # Update fields
        if "full_name" in data:
            user["full_name"] = data["full_name"]
        if "language" in data:
            user["language"] = data["language"]
        if "theme" in data:
            user["theme"] = data["theme"]
        
        logger.info("Profile updated", email=email)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": self._sanitize_user(user)
        }
    
    async def _update_preferences(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        email = data.get("email", "").lower().strip()
        preferences = data.get("preferences", {})
        
        if email not in self.users:
            return {"success": False, "error": "User not found"}
        
        user = self.users[email]
        user["preferences"].update(preferences)
        
        return {
            "success": True,
            "message": "Preferences updated",
            "preferences": user["preferences"]
        }
    
    # ============ WALLET MANAGEMENT ============
    
    async def _connect_wallet(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Connect user's Web3 wallet"""
        email = data.get("email", "").lower().strip()
        wallet_address = data.get("wallet_address")
        
        if email not in self.users:
            return {"success": False, "error": "User not found"}
        
        user = self.users[email]
        user["wallet_address"] = wallet_address
        
        # TODO: Verify wallet ownership via signature
        
        logger.info("Wallet connected", email=email, wallet=wallet_address[:10])
        
        return {
            "success": True,
            "message": "Wallet connected successfully!",
            "wallet_address": wallet_address
        }
    
    async def _create_wallet(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new wallet for user (custodial)"""
        email = data.get("email", "").lower().strip()
        
        if email not in self.users:
            return {"success": False, "error": "User not found"}
        
        # TODO: Integrate with wallet creation service
        # For now, generate placeholder
        wallet_address = f"0x{secrets.token_hex(20)}"
        
        user = self.users[email]
        user["wallet_address"] = wallet_address
        
        logger.info("Wallet created", email=email)
        
        return {
            "success": True,
            "message": "Wallet created successfully!",
            "wallet_address": wallet_address,
            "note": "Keep your recovery phrase safe!"
        }
    
    async def _get_wallet_balance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get wallet balance"""
        email = data.get("email", "").lower().strip()
        
        if email not in self.users:
            return {"success": False, "error": "User not found"}
        
        user = self.users[email]
        
        # TODO: Query actual blockchain balance
        # For now, use stored values
        
        return {
            "success": True,
            "wallet_address": user.get("wallet_address"),
            "balance_omk": user.get("wallet_balance_omk", 0),
            "balance_usd": user.get("wallet_balance_usd", 0),
            "roi_percentage": user.get("roi_percentage", 0)
        }
    
    # ============ PASSWORD MANAGEMENT ============
    
    async def _change_password(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Change user password"""
        email = data.get("email", "").lower().strip()
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        
        if email not in self.users:
            return {"success": False, "error": "User not found"}
        
        user = self.users[email]
        
        # Verify old password
        if not self._verify_password(old_password, user["password_hash"]):
            return {"success": False, "error": "Incorrect current password"}
        
        if len(new_password) < 8:
            return {"success": False, "error": "New password must be at least 8 characters"}
        
        # Update password
        user["password_hash"] = self._hash_password(new_password)
        
        logger.info("Password changed", email=email)
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    
    async def _reset_password_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Request password reset"""
        email = data.get("email", "").lower().strip()
        
        if email not in self.users:
            # Don't reveal if email exists
            return {
                "success": True,
                "message": "If the email exists, a reset code has been sent"
            }
        
        # Generate reset code
        reset_code = secrets.token_urlsafe(32)
        self.verification_codes[email] = reset_code
        
        # TODO: Send email with reset code
        
        logger.info("Password reset requested", email=email)
        
        return {
            "success": True,
            "message": "Password reset code sent to your email",
            "reset_code": reset_code  # Remove this in production!
        }
    
    async def _reset_password_confirm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Confirm password reset with code"""
        email = data.get("email", "").lower().strip()
        reset_code = data.get("reset_code")
        new_password = data.get("new_password")
        
        if email not in self.users:
            return {"success": False, "error": "Invalid request"}
        
        if email not in self.verification_codes:
            return {"success": False, "error": "No reset code found"}
        
        if self.verification_codes[email] != reset_code:
            return {"success": False, "error": "Invalid reset code"}
        
        if len(new_password) < 8:
            return {"success": False, "error": "Password must be at least 8 characters"}
        
        # Update password
        user = self.users[email]
        user["password_hash"] = self._hash_password(new_password)
        
        # Remove reset code
        del self.verification_codes[email]
        
        logger.info("Password reset completed", email=email)
        
        return {
            "success": True,
            "message": "Password reset successfully!"
        }
    
    # ============ STATISTICS ============
    
    async def _get_onboarding_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get onboarding statistics"""
        return {
            "success": True,
            "stats": {
                "total_users": self.total_users,
                "active_sessions": self.active_sessions,
                "signups_today": self.signups_today,
                "user_types": self._get_user_type_breakdown()
            }
        }
    
    # ============ HELPER METHODS ============
    
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_value = password_hash.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_value
        except:
            return False
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"user_{secrets.token_hex(8)}"
    
    def _create_session(self, email: str) -> str:
        """Create user session"""
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        self.sessions[session_token] = {
            "email": email,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat()
        }
        
        self.active_sessions += 1
        
        return session_token
    
    def _sanitize_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from user object"""
        if not user:
            return {}
        
        sanitized = user.copy()
        sanitized.pop("password_hash", None)
        return sanitized
    
    def _get_user_type_breakdown(self) -> Dict[str, int]:
        """Get breakdown of user types"""
        breakdown = {}
        for user in self.users.values():
            user_type = user.get("user_type", "unknown")
            breakdown[user_type] = breakdown.get(user_type, 0) + 1
        return breakdown
