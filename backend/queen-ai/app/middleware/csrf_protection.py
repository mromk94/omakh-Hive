"""
CSRF Protection Middleware
Protects state-changing operations (POST, PUT, DELETE, PATCH) from CSRF attacks
"""

import secrets
import structlog
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable

logger = structlog.get_logger(__name__)


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection for state-changing operations
    
    How it works:
    1. GET requests receive a CSRF token in response headers
    2. POST/PUT/DELETE/PATCH must include X-CSRF-Token header
    3. Token is validated before processing request
    """
    
    def __init__(self, app, secret_key: str = None):
        super().__init__(app)
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.token_store = {}  # In production, use Redis
        
        # Methods that require CSRF protection
        self.protected_methods = {"POST", "PUT", "DELETE", "PATCH"}
        
        # Exempt paths (e.g., public endpoints)
        self.exempt_paths = {
            "/api/v1/auth/login",
            "/api/v1/auth/register", 
            "/docs",
            "/openapi.json",
            "/health"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with CSRF protection"""
        
        # Skip CSRF for exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # For GET requests: Generate and send CSRF token
        if request.method == "GET":
            response = await call_next(request)
            
            # Generate CSRF token
            csrf_token = self._generate_token()
            
            # Store token (in production, use Redis with TTL)
            session_id = request.cookies.get("session_id") or request.headers.get("Authorization", "")
            if session_id:
                self.token_store[session_id] = csrf_token
            
            # Send token in response header
            response.headers["X-CSRF-Token"] = csrf_token
            
            return response
        
        # For state-changing methods: Validate CSRF token
        if request.method in self.protected_methods:
            csrf_token = request.headers.get("X-CSRF-Token")
            
            if not csrf_token:
                logger.warning("CSRF token missing", 
                             method=request.method,
                             path=request.url.path)
                raise HTTPException(
                    status_code=403,
                    detail="CSRF token missing. Include X-CSRF-Token header."
                )
            
            # Validate token
            session_id = request.cookies.get("session_id") or request.headers.get("Authorization", "")
            valid = self._validate_token(session_id, csrf_token)
            
            if not valid:
                logger.warning("CSRF token invalid", 
                             method=request.method,
                             path=request.url.path)
                raise HTTPException(
                    status_code=403,
                    detail="CSRF token invalid or expired"
                )
            
            logger.debug("CSRF token validated", method=request.method, path=request.url.path)
        
        return await call_next(request)
    
    def _generate_token(self) -> str:
        """Generate a secure CSRF token"""
        return secrets.token_urlsafe(32)
    
    def _validate_token(self, session_id: str, token: str) -> bool:
        """Validate CSRF token against stored token"""
        if not session_id or not token:
            return False
        
        stored_token = self.token_store.get(session_id)
        if not stored_token:
            return False
        
        # Constant-time comparison to prevent timing attacks
        return secrets.compare_digest(stored_token, token)
    
    def clear_token(self, session_id: str):
        """Clear CSRF token for a session"""
        if session_id in self.token_store:
            del self.token_store[session_id]


# Simpler alternative: Double Submit Cookie Pattern
class DoubleSubmitCSRFMiddleware(BaseHTTPMiddleware):
    """
    Simplified CSRF using Double Submit Cookie pattern
    
    - Sends CSRF token as cookie
    - Validates against X-CSRF-Token header
    - No server-side storage needed
    """
    
    def __init__(self, app, cookie_name: str = "csrf_token"):
        super().__init__(app)
        self.cookie_name = cookie_name
        
        self.protected_methods = {"POST", "PUT", "DELETE", "PATCH"}
        self.exempt_paths = {
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/docs",
            "/openapi.json",
            "/health"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with Double Submit CSRF"""
        
        # Skip exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # For GET: Send CSRF token as cookie
        if request.method == "GET":
            response = await call_next(request)
            
            # Generate token if not exists
            csrf_token = request.cookies.get(self.cookie_name)
            if not csrf_token:
                csrf_token = secrets.token_urlsafe(32)
                response.set_cookie(
                    key=self.cookie_name,
                    value=csrf_token,
                    httponly=True,
                    secure=False,  # Set True in production with HTTPS
                    samesite="lax",
                    max_age=3600 * 24  # 24 hours
                )
            
            # Also send in header for easy access
            response.headers["X-CSRF-Token"] = csrf_token
            
            return response
        
        # For state-changing: Validate token
        if request.method in self.protected_methods:
            cookie_token = request.cookies.get(self.cookie_name)
            header_token = request.headers.get("X-CSRF-Token")
            
            if not cookie_token or not header_token:
                logger.warning("CSRF token missing",
                             method=request.method,
                             path=request.url.path,
                             has_cookie=bool(cookie_token),
                             has_header=bool(header_token))
                raise HTTPException(
                    status_code=403,
                    detail="CSRF protection: Token missing"
                )
            
            # Validate: cookie and header must match
            if not secrets.compare_digest(cookie_token, header_token):
                logger.warning("CSRF token mismatch",
                             method=request.method,
                             path=request.url.path)
                raise HTTPException(
                    status_code=403,
                    detail="CSRF protection: Token mismatch"
                )
            
            logger.debug("CSRF validated", method=request.method, path=request.url.path)
        
        return await call_next(request)
