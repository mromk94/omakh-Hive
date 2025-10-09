"""
Session Manager for Stateless Architecture

Maintains session continuity across ephemeral instances.
Sessions are stored in Redis so they survive instance termination.
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)


class SessionManager:
    """
    Distributed session manager using Redis
    
    Ensures user sessions continue seamlessly even when:
    - Instance is terminated (scale down)
    - Request is routed to different instance (load balancing)
    - Instance is replaced (rolling update)
    """
    
    def __init__(self):
        self.redis = None
        self.default_ttl = 3600  # 1 hour
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            from app.core.redis_message_bus import RedisMessageBus
            
            bus = RedisMessageBus()
            await bus.initialize()
            
            if bus.initialized:
                self.redis = bus.redis
                logger.info("Session manager initialized")
                return True
            else:
                logger.warning("Session manager unavailable - sessions won't persist")
                return False
        
        except Exception as e:
            logger.warning(f"Session manager unavailable: {str(e)}")
            return False
    
    async def create_session(
        self,
        session_id: str,
        session_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Create new session
        
        Args:
            session_id: Unique session identifier
            session_data: Session data to store
            ttl: Time to live in seconds (default: 1 hour)
        
        Returns:
            True if created successfully
        """
        if not self.redis:
            return False
        
        try:
            # Add metadata
            full_session_data = {
                **session_data,
                "_created_at": datetime.utcnow().isoformat(),
                "_last_accessed": datetime.utcnow().isoformat()
            }
            
            # Store in Redis with TTL
            await self.redis.setex(
                f"session:{session_id}",
                ttl or self.default_ttl,
                json.dumps(full_session_data)
            )
            
            logger.debug(f"Session created: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        
        Automatically updates last_accessed timestamp and refreshes TTL
        """
        if not self.redis:
            return None
        
        try:
            session_key = f"session:{session_id}"
            session_json = await self.redis.get(session_key)
            
            if not session_json:
                return None
            
            session_data = json.loads(session_json)
            
            # Update last accessed
            session_data["_last_accessed"] = datetime.utcnow().isoformat()
            
            # Refresh TTL
            await self.redis.setex(
                session_key,
                self.default_ttl,
                json.dumps(session_data)
            )
            
            logger.debug(f"Session retrieved: {session_id}")
            return session_data
        
        except Exception as e:
            logger.error(f"Failed to get session: {str(e)}")
            return None
    
    async def update_session(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update session data"""
        if not self.redis:
            return False
        
        try:
            # Get current session
            session_data = await self.get_session(session_id)
            
            if not session_data:
                logger.warning(f"Session not found for update: {session_id}")
                return False
            
            # Apply updates
            session_data.update(updates)
            session_data["_last_accessed"] = datetime.utcnow().isoformat()
            
            # Save back
            await self.redis.setex(
                f"session:{session_id}",
                self.default_ttl,
                json.dumps(session_data)
            )
            
            logger.debug(f"Session updated: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update session: {str(e)}")
            return False
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(f"session:{session_id}")
            logger.debug(f"Session deleted: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")
            return False
    
    async def extend_session(self, session_id: str, additional_seconds: int = 3600) -> bool:
        """Extend session TTL"""
        if not self.redis:
            return False
        
        try:
            session_key = f"session:{session_id}"
            
            # Get current TTL
            current_ttl = await self.redis.ttl(session_key)
            
            if current_ttl < 0:
                # Session doesn't exist or has no expiry
                return False
            
            # Extend TTL
            new_ttl = current_ttl + additional_seconds
            await self.redis.expire(session_key, new_ttl)
            
            logger.debug(f"Session extended: {session_id} (+{additional_seconds}s)")
            return True
        
        except Exception as e:
            logger.error(f"Failed to extend session: {str(e)}")
            return False
    
    async def get_session_count(self) -> int:
        """Get total active session count"""
        if not self.redis:
            return 0
        
        try:
            cursor = 0
            count = 0
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match="session:*", count=100)
                count += len(keys)
                
                if cursor == 0:
                    break
            
            return count
        
        except Exception as e:
            logger.error(f"Failed to count sessions: {str(e)}")
            return 0
    
    async def cleanup_expired_sessions(self):
        """
        Cleanup expired sessions (maintenance)
        
        Redis automatically removes expired keys, but we can scan for orphaned data
        """
        if not self.redis:
            return
        
        try:
            cursor = 0
            cleaned = 0
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match="session:*", count=100)
                
                for key in keys:
                    ttl = await self.redis.ttl(key)
                    
                    # If TTL is -2, key doesn't exist (already expired)
                    if ttl == -2:
                        cleaned += 1
                
                if cursor == 0:
                    break
            
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired sessions")
        
        except Exception as e:
            logger.error(f"Failed to cleanup sessions: {str(e)}")


# Global instance
session_manager = SessionManager()
