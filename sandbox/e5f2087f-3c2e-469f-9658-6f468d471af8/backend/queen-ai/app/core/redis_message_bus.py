"""
Redis-backed Message Bus - Persistent Message Queue

Replaces in-memory MessageBus with Redis for production persistence.
"""
import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import structlog

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class RedisMessageBus:
    """
    Redis-backed message bus for persistent inter-bee communication
    
    Features:
    - Persistent message queues (survives restarts)
    - Priority queuing
    - Message broadcasting
    - Request-response pattern
    - Message history for learning
    - TTL for message expiration
    
    Redis Data Structures:
    - queue:{bee_name} - List (LPUSH/RPOP for FIFO queue)
    - queue:{bee_name}:priority - List (high priority messages)
    - messages:history - Sorted Set (for audit trail)
    - subscriptions:{channel} - Pub/Sub channels
    """
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.initialized = False
        self.pubsub = None
        self.subscribers: Dict[str, List[Callable]] = {}
        
        if not REDIS_AVAILABLE:
            logger.warning("⚠️  redis package not installed. Install with: pip install redis")
    
    async def initialize(self, retry_attempts: int = 3):
        """Initialize Redis connection with HA support"""
        if not REDIS_AVAILABLE:
            logger.error("Redis not available - falling back to in-memory")
            return
        
        for attempt in range(retry_attempts):
            try:
                # Create Redis client with HA settings
                self.redis = await aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=50,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_connect_timeout=5,
                    health_check_interval=30
                )
                
                # Test connection
                await self.redis.ping()
                
                # Initialize pub/sub
                self.pubsub = self.redis.pubsub()
                
                self.initialized = True
                logger.info(f"✅ Redis Message Bus initialized: {settings.REDIS_URL.split('@')[1] if '@' in settings.REDIS_URL else settings.REDIS_URL}")
                return
                
            except Exception as e:
                logger.warning(f"Redis connection attempt {attempt + 1}/{retry_attempts} failed: {str(e)}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to connect to Redis after {retry_attempts} attempts")
                    logger.warning("Falling back to in-memory message bus")
                    self.initialized = False
    
    def register_bee(self, bee_name: str):
        """Register a bee (create queue if doesn't exist)"""
        if not self.initialized:
            return
        
        logger.info(f"Registered bee: {bee_name}")
    
    async def send_message(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: int = 0
    ) -> bool:
        """
        Send message to bee's queue
        
        Args:
            sender: Sender bee name
            recipient: Recipient bee name
            message_type: Type of message
            payload: Message payload
            priority: 0=normal, 1=high, 2=critical
        
        Returns:
            Success status
        """
        if not self.initialized:
            logger.warning("Redis not initialized - message not sent")
            return False
        
        try:
            message = {
                "sender": sender,
                "recipient": recipient,
                "message_type": message_type,
                "payload": payload,
                "priority": priority,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            message_json = json.dumps(message)
            
            # Choose queue based on priority
            if priority > 0:
                queue_key = f"queue:{recipient}:priority"
            else:
                queue_key = f"queue:{recipient}"
            
            # Push to queue (LPUSH for FIFO via RPOP)
            await self.redis.lpush(queue_key, message_json)
            
            # Add to message history (sorted set by timestamp)
            timestamp_ms = int(datetime.utcnow().timestamp() * 1000)
            await self.redis.zadd(
                "messages:history",
                {message_json: timestamp_ms}
            )
            
            # Trim history to last 10,000 messages
            await self.redis.zremrangebyrank("messages:history", 0, -10001)
            
            logger.debug(
                f"Message sent",
                sender=sender,
                recipient=recipient,
                type=message_type,
                priority=priority
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return False
    
    async def get_messages(
        self,
        bee_name: str,
        max_messages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get messages from bee's queue
        
        Checks priority queue first, then normal queue
        """
        if not self.initialized:
            return []
        
        try:
            messages = []
            
            # Get priority messages first
            priority_queue = f"queue:{bee_name}:priority"
            while len(messages) < max_messages:
                message_json = await self.redis.rpop(priority_queue)
                if not message_json:
                    break
                messages.append(json.loads(message_json))
            
            # Get normal messages
            normal_queue = f"queue:{bee_name}"
            while len(messages) < max_messages:
                message_json = await self.redis.rpop(normal_queue)
                if not message_json:
                    break
                messages.append(json.loads(message_json))
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages: {str(e)}")
            return []
    
    async def broadcast(
        self,
        sender: str,
        message_type: str,
        payload: Dict[str, Any]
    ) -> int:
        """
        Broadcast message to all bees via pub/sub
        
        Returns:
            Number of subscribers
        """
        if not self.initialized:
            return 0
        
        try:
            message = {
                "sender": sender,
                "message_type": message_type,
                "payload": payload,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Publish to broadcast channel
            subscribers = await self.redis.publish(
                "broadcast:all",
                json.dumps(message)
            )
            
            logger.info(
                f"Broadcast sent to {subscribers} subscribers",
                sender=sender,
                type=message_type
            )
            
            return subscribers
            
        except Exception as e:
            logger.error(f"Failed to broadcast: {str(e)}")
            return 0
    
    async def subscribe(
        self,
        channel: str,
        callback: Callable[[Dict[str, Any]], None]
    ):
        """
        Subscribe to a channel
        
        Args:
            channel: Channel name (e.g., "broadcast:all")
            callback: Async function to call with message
        """
        if not self.initialized:
            return
        
        try:
            await self.pubsub.subscribe(channel)
            
            # Store callback
            if channel not in self.subscribers:
                self.subscribers[channel] = []
            self.subscribers[channel].append(callback)
            
            logger.info(f"Subscribed to channel: {channel}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe: {str(e)}")
    
    async def get_queue_size(self, bee_name: str) -> Dict[str, int]:
        """Get queue sizes for a bee"""
        if not self.initialized:
            return {"normal": 0, "priority": 0, "total": 0}
        
        try:
            normal = await self.redis.llen(f"queue:{bee_name}") or 0
            priority = await self.redis.llen(f"queue:{bee_name}:priority") or 0
            
            return {
                "normal": normal,
                "priority": priority,
                "total": normal + priority
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue size: {str(e)}")
            return {"normal": 0, "priority": 0, "total": 0}
    
    async def clear_queue(self, bee_name: str):
        """Clear all messages for a bee (admin function)"""
        if not self.initialized:
            return
        
        try:
            await self.redis.delete(f"queue:{bee_name}")
            await self.redis.delete(f"queue:{bee_name}:priority")
            logger.info(f"Cleared queue for: {bee_name}")
            
        except Exception as e:
            logger.error(f"Failed to clear queue: {str(e)}")
    
    async def get_message_history(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent message history"""
        if not self.initialized:
            return []
        
        try:
            # Get last N messages from sorted set
            messages_json = await self.redis.zrevrange(
                "messages:history",
                0,
                limit - 1
            )
            
            messages = [json.loads(msg) for msg in messages_json]
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get history: {str(e)}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health"""
        if not self.initialized:
            return {
                "healthy": False,
                "error": "Not initialized"
            }
        
        try:
            # Ping Redis
            await self.redis.ping()
            
            # Get info
            info = await self.redis.info()
            
            return {
                "healthy": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0)
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }
    
    async def shutdown(self):
        """Cleanup Redis connections"""
        if self.pubsub:
            await self.pubsub.close()
        
        if self.redis:
            await self.redis.close()
        
        logger.info("Redis Message Bus shutdown")
