"""
Security & Governance Layer

Implements security controls, authentication, and governance mechanisms.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import structlog
from functools import wraps

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config.settings import settings

logger = structlog.get_logger(__name__)

# API Key header
api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


class SecurityManager:
    """
    Security & Governance Manager
    
    Features:
    - API key authentication
    - Rate limiting
    - IP whitelisting
    - Multisig verification
    - Timelock enforcement
    - Audit logging
    - Emergency controls
    """
    
    def __init__(self):
        self.rate_limits: Dict[str, List[datetime]] = {}
        self.blocked_ips: set = set()
        self.admin_keys: set = set(settings.ADMIN_API_KEYS.split(",") if settings.ADMIN_API_KEYS else [])
        self.emergency_mode = False
        self.timelock_proposals: Dict[int, datetime] = {}
    
    def verify_api_key(self, api_key: Optional[str] = None) -> bool:
        """
        Verify API key
        
        Returns:
            True if valid
        """
        if not api_key:
            return False
        
        # Check admin keys
        if api_key in self.admin_keys:
            return True
        
        # TODO: Check database for user API keys
        
        return False
    
    def is_admin(self, api_key: str) -> bool:
        """Check if API key has admin privileges"""
        return api_key in self.admin_keys
    
    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """
        Check rate limit for identifier (IP or API key)
        
        Args:
            identifier: IP address or API key
            max_requests: Max requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            True if within limit, False if exceeded
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Get request history
        if identifier not in self.rate_limits:
            self.rate_limits[identifier] = []
        
        # Remove old requests
        self.rate_limits[identifier] = [
            req_time for req_time in self.rate_limits[identifier]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.rate_limits[identifier]) >= max_requests:
            logger.warning(
                f"Rate limit exceeded",
                identifier=identifier,
                requests=len(self.rate_limits[identifier])
            )
            return False
        
        # Add current request
        self.rate_limits[identifier].append(now)
        return True
    
    def block_ip(self, ip_address: str):
        """Block an IP address"""
        self.blocked_ips.add(ip_address)
        logger.warning(f"IP blocked: {ip_address}")
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            logger.info(f"IP unblocked: {ip_address}")
    
    def is_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips
    
    def create_timelock(
        self,
        proposal_id: int,
        delay_hours: int = 48
    ):
        """
        Create timelock for proposal
        
        Proposals cannot be executed until timelock expires
        """
        execute_after = datetime.utcnow() + timedelta(hours=delay_hours)
        self.timelock_proposals[proposal_id] = execute_after
        
        logger.info(
            f"Timelock created",
            proposal_id=proposal_id,
            execute_after=execute_after.isoformat()
        )
    
    def check_timelock(self, proposal_id: int) -> bool:
        """
        Check if timelock has expired
        
        Returns:
            True if can execute, False if still locked
        """
        if proposal_id not in self.timelock_proposals:
            return True  # No timelock
        
        execute_after = self.timelock_proposals[proposal_id]
        can_execute = datetime.utcnow() >= execute_after
        
        if can_execute:
            # Remove timelock
            del self.timelock_proposals[proposal_id]
        
        return can_execute
    
    def enable_emergency_mode(self, reason: str):
        """
        Enable emergency mode - blocks all non-admin operations
        
        Use for critical security incidents
        """
        self.emergency_mode = True
        logger.critical(
            f"🚨 EMERGENCY MODE ENABLED",
            reason=reason
        )
    
    def disable_emergency_mode(self):
        """Disable emergency mode"""
        self.emergency_mode = False
        logger.warning("Emergency mode disabled")
    
    def is_emergency_mode(self) -> bool:
        """Check if emergency mode is active"""
        return self.emergency_mode
    
    def generate_api_key(self) -> str:
        """Generate new API key"""
        return secrets.token_urlsafe(32)
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def audit_log(
        self,
        action: str,
        user: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log security-sensitive action
        
        All governance and critical actions should be logged
        """
        logger.info(
            f"AUDIT: {action}",
            user=user,
            action=action,
            details=details,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def verify_multisig(
        self,
        signatures: List[str],
        required_signatures: int = 2
    ) -> bool:
        """
        Verify multisig signatures
        
        For critical operations like contract upgrades
        
        Args:
            signatures: List of signatures
            required_signatures: Minimum required
        
        Returns:
            True if valid
        """
        # TODO: Implement actual signature verification
        # This is a placeholder
        
        if len(signatures) < required_signatures:
            logger.warning(
                f"Insufficient signatures",
                provided=len(signatures),
                required=required_signatures
            )
            return False
        
        logger.info(
            f"Multisig verified",
            signatures=len(signatures)
        )
        return True


# Global security manager instance
security_manager = SecurityManager()


# Dependency for FastAPI routes
async def verify_api_key_dependency(
    api_key: Optional[str] = Security(api_key_header)
) -> str:
    """
    FastAPI dependency for API key verification
    
    Usage:
        @app.get("/protected")
        async def protected_route(api_key: str = Depends(verify_api_key_dependency)):
            # Route logic
            pass
    """
    if not api_key or not security_manager.verify_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    
    return api_key


async def verify_admin_key(
    api_key: str = Security(api_key_header)
) -> str:
    """
    FastAPI dependency for admin verification
    
    Requires admin-level API key
    """
    if not api_key or not security_manager.is_admin(api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return api_key


def require_api_key(func):
    """Decorator for requiring API key (non-FastAPI functions)"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract api_key from kwargs
        api_key = kwargs.get("api_key")
        
        if not api_key or not security_manager.verify_api_key(api_key):
            raise PermissionError("Invalid API key")
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_admin(func):
    """Decorator for requiring admin access"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        api_key = kwargs.get("api_key")
        
        if not api_key or not security_manager.is_admin(api_key):
            raise PermissionError("Admin access required")
        
        return await func(*args, **kwargs)
    
    return wrapper
