"""
Distributed Locking for Multi-Instance Coordination

Prevents race conditions and data corruption when multiple instances
operate concurrently during auto-scaling.

Uses Redis for distributed locks with automatic expiration.
"""
import asyncio
import time
import uuid
from typing import Optional
from contextlib import asynccontextmanager
import structlog

logger = structlog.get_logger(__name__)


class DistributedLock:
    """
    Distributed lock using Redis
    
    Ensures only one instance can perform critical operations at a time.
    Automatically releases locks on timeout to prevent deadlocks.
    
    Usage:
        async with distributed_lock.acquire("operation_name"):
            # Critical section - only one instance executes this
            await perform_operation()
    """
    
    def __init__(self):
        self.redis = None
        self.locks_held: set = set()
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            from app.core.redis_message_bus import RedisMessageBus
            
            bus = RedisMessageBus()
            await bus.initialize()
            
            if bus.initialized:
                self.redis = bus.redis
                logger.info("Distributed locking initialized")
                return True
            else:
                logger.warning("Distributed locking unavailable - using local locks")
                return False
        
        except Exception as e:
            logger.warning(f"Distributed locking unavailable: {str(e)}")
            return False
    
    @asynccontextmanager
    async def acquire(
        self,
        lock_name: str,
        timeout: int = 30,
        retry_delay: float = 0.1,
        max_retries: int = 100
    ):
        """
        Acquire distributed lock
        
        Args:
            lock_name: Unique name for the lock
            timeout: Lock expiration in seconds (prevents deadlocks)
            retry_delay: Delay between retries in seconds
            max_retries: Maximum number of retries
        
        Raises:
            TimeoutError: If lock cannot be acquired after max_retries
        """
        if not self.redis:
            # Fallback to local lock (development mode)
            lock = asyncio.Lock()
            async with lock:
                yield
            return
        
        lock_key = f"lock:{lock_name}"
        lock_value = str(uuid.uuid4())  # Unique identifier for this lock
        acquired = False
        
        try:
            # Try to acquire lock
            for attempt in range(max_retries):
                # SET NX EX - Set if Not eXists with EXpiration
                acquired = await self.redis.set(
                    lock_key,
                    lock_value,
                    ex=timeout,
                    nx=True  # Only set if doesn't exist
                )
                
                if acquired:
                    self.locks_held.add(lock_name)
                    logger.debug(
                        f"Lock acquired: {lock_name}",
                        attempt=attempt + 1,
                        timeout=timeout
                    )
                    break
                
                # Lock is held by another instance, wait and retry
                await asyncio.sleep(retry_delay)
            
            if not acquired:
                raise TimeoutError(
                    f"Could not acquire lock '{lock_name}' after {max_retries} retries"
                )
            
            # Execute critical section
            yield
        
        finally:
            # Release lock only if we hold it
            if acquired:
                await self._release_lock(lock_key, lock_value, lock_name)
    
    async def _release_lock(self, lock_key: str, lock_value: str, lock_name: str):
        """Release lock safely (only if we own it)"""
        try:
            # Use Lua script to ensure atomic check-and-delete
            # Only delete if the value matches (prevents releasing someone else's lock)
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            
            result = await self.redis.eval(lua_script, 1, lock_key, lock_value)
            
            if result:
                self.locks_held.discard(lock_name)
                logger.debug(f"Lock released: {lock_name}")
            else:
                logger.warning(
                    f"Lock already expired or owned by another instance: {lock_name}"
                )
        
        except Exception as e:
            logger.error(f"Error releasing lock '{lock_name}': {str(e)}")
    
    async def is_locked(self, lock_name: str) -> bool:
        """Check if lock is currently held"""
        if not self.redis:
            return False
        
        try:
            lock_key = f"lock:{lock_name}"
            exists = await self.redis.exists(lock_key)
            return bool(exists)
        
        except Exception:
            return False
    
    async def force_release(self, lock_name: str):
        """
        Force release a lock (admin function)
        
        Use with caution - only for recovery from deadlocks
        """
        if not self.redis:
            return
        
        try:
            lock_key = f"lock:{lock_name}"
            await self.redis.delete(lock_key)
            logger.warning(f"Lock force-released: {lock_name}")
        
        except Exception as e:
            logger.error(f"Error force-releasing lock: {str(e)}")
    
    async def get_all_locks(self) -> list:
        """Get all active locks (debugging)"""
        if not self.redis:
            return []
        
        try:
            cursor = 0
            locks = []
            
            while True:
                cursor, keys = await self.redis.scan(cursor, match="lock:*", count=100)
                
                for key in keys:
                    ttl = await self.redis.ttl(key)
                    locks.append({
                        "name": key.replace("lock:", ""),
                        "ttl_seconds": ttl
                    })
                
                if cursor == 0:
                    break
            
            return locks
        
        except Exception as e:
            logger.error(f"Error getting locks: {str(e)}")
            return []
    
    async def cleanup_expired_locks(self):
        """Cleanup any expired locks (maintenance)"""
        # Redis automatically removes expired keys, but we can log them
        locks = await self.get_all_locks()
        
        for lock in locks:
            if lock["ttl_seconds"] < 0:
                # Already expired, just log
                logger.debug(f"Expired lock detected: {lock['name']}")


# Global instance
distributed_lock = DistributedLock()


# Decorator for critical sections
def critical_section(lock_name: str, timeout: int = 30):
    """
    Decorator to make a function a critical section
    
    Usage:
        @critical_section("process_proposal")
        async def process_proposal(proposal_id):
            # Only one instance executes this at a time
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with distributed_lock.acquire(lock_name, timeout=timeout):
                return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator
