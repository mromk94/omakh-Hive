"""
Message Bus - Inter-Bee Communication System

Enables unrestricted communication between Queen and all bee agents.
Priority: Security, Safety, Health of the hive.
"""
import asyncio
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
from collections import defaultdict
import structlog

logger = structlog.get_logger(__name__)


class Message:
    """Message structure for inter-bee communication"""
    
    def __init__(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: int = 0,  # 0=normal, 1=high, 2=critical
    ):
        self.id = f"{sender}_{recipient}_{datetime.utcnow().timestamp()}"
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type
        self.payload = payload
        self.priority = priority
        self.timestamp = datetime.utcnow()
        self.delivered = False
        self.response: Optional[Any] = None


class MessageBus:
    """
    Central message bus for Queen-Bee communication
    
    Features:
    - Asynchronous message passing
    - Priority queuing (critical > high > normal)
    - Broadcast messaging
    - Request-response pattern
    - Message logging for learning
    - No restrictions on communication
    """
    
    def __init__(self):
        self.queues: Dict[str, asyncio.Queue] = {}
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[Message] = []
        self.active = False
        self.worker_tasks: List[asyncio.Task] = []
        
    async def initialize(self):
        """Initialize message bus"""
        self.active = True
        logger.info("Message bus initialized")
    
    def register_bee(self, bee_name: str):
        """Register a bee to receive messages"""
        if bee_name not in self.queues:
            self.queues[bee_name] = asyncio.Queue()
            logger.info(f"Registered bee: {bee_name}")
    
    async def send_message(
        self,
        sender: str,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: int = 0,
        wait_for_response: bool = False,
    ) -> Optional[Any]:
        """
        Send message to a specific bee
        
        Args:
            sender: Sender identifier (e.g., "queen", "maths_bee")
            recipient: Recipient identifier
            message_type: Type of message (e.g., "task", "query", "alert")
            payload: Message data
            priority: 0=normal, 1=high, 2=critical
            wait_for_response: If True, wait for response
            
        Returns:
            Response if wait_for_response=True, else None
        """
        if not self.active:
            logger.warning("Message bus not active")
            return None
        
        # Create message
        message = Message(sender, recipient, message_type, payload, priority)
        
        # Log message
        self.message_history.append(message)
        
        # Queue message
        if recipient in self.queues:
            await self.queues[recipient].put(message)
            logger.debug(
                f"Message sent: {sender} → {recipient}",
                message_type=message_type,
                priority=priority
            )
        elif recipient == "all":
            # Broadcast
            await self.broadcast(sender, message_type, payload, priority)
        else:
            logger.warning(f"Recipient not found: {recipient}")
            return None
        
        # Wait for response if requested
        if wait_for_response:
            # Wait up to 30 seconds for response
            for _ in range(30):
                await asyncio.sleep(1)
                if message.response is not None:
                    return message.response
            logger.warning(f"No response from {recipient} within 30s")
            return None
        
        return None
    
    async def broadcast(
        self,
        sender: str,
        message_type: str,
        payload: Dict[str, Any],
        priority: int = 0,
    ):
        """Broadcast message to all bees"""
        for bee_name in self.queues:
            if bee_name != sender:  # Don't send to self
                await self.send_message(
                    sender,
                    bee_name,
                    message_type,
                    payload,
                    priority
                )
        
        logger.info(f"Broadcast from {sender} to all bees", message_type=message_type)
    
    async def get_messages(self, bee_name: str, timeout: float = 0.1) -> List[Message]:
        """Get pending messages for a bee"""
        if bee_name not in self.queues:
            return []
        
        messages = []
        try:
            while True:
                message = await asyncio.wait_for(
                    self.queues[bee_name].get(),
                    timeout=timeout
                )
                messages.append(message)
        except asyncio.TimeoutError:
            pass
        
        return messages
    
    async def respond_to_message(
        self,
        message: Message,
        response: Any,
    ):
        """Send response to a message"""
        message.response = response
        message.delivered = True
        
        logger.debug(
            f"Response sent: {message.recipient} → {message.sender}",
            message_type=message.message_type
        )
    
    def get_message_history(
        self,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
        message_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get message history for analysis/learning"""
        filtered = self.message_history
        
        if sender:
            filtered = [m for m in filtered if m.sender == sender]
        if recipient:
            filtered = [m for m in filtered if m.recipient == recipient]
        if message_type:
            filtered = [m for m in filtered if m.message_type == message_type]
        
        # Return most recent
        filtered = filtered[-limit:]
        
        return [
            {
                "id": m.id,
                "sender": m.sender,
                "recipient": m.recipient,
                "type": m.message_type,
                "payload": m.payload,
                "priority": m.priority,
                "timestamp": m.timestamp.isoformat(),
                "delivered": m.delivered,
            }
            for m in filtered
        ]
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        total_messages = len(self.message_history)
        delivered_messages = len([m for m in self.message_history if m.delivered])
        
        # Messages by sender
        by_sender = defaultdict(int)
        for m in self.message_history:
            by_sender[m.sender] += 1
        
        # Messages by type
        by_type = defaultdict(int)
        for m in self.message_history:
            by_type[m.message_type] += 1
        
        # Priority distribution
        by_priority = defaultdict(int)
        for m in self.message_history:
            by_priority[m.priority] += 1
        
        return {
            "total_messages": total_messages,
            "delivered_messages": delivered_messages,
            "delivery_rate": (delivered_messages / total_messages * 100) if total_messages > 0 else 0,
            "active_bees": len(self.queues),
            "by_sender": dict(by_sender),
            "by_type": dict(by_type),
            "by_priority": dict(by_priority),
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check message bus health"""
        stats = self.get_communication_stats()
        
        # Check for communication issues
        issues = []
        
        # Check queue backlogs
        for bee_name, queue in self.queues.items():
            queue_size = queue.qsize()
            if queue_size > 100:
                issues.append(f"{bee_name} queue backlog: {queue_size} messages")
        
        # Check delivery rate
        if stats["total_messages"] > 100 and stats["delivery_rate"] < 80:
            issues.append(f"Low delivery rate: {stats['delivery_rate']:.1f}%")
        
        health_status = "healthy" if not issues else "degraded" if len(issues) < 3 else "critical"
        
        return {
            "status": health_status,
            "active": self.active,
            "registered_bees": list(self.queues.keys()),
            "stats": stats,
            "issues": issues,
        }
    
    async def shutdown(self):
        """Shutdown message bus"""
        self.active = False
        
        # Cancel worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Clear queues
        for queue in self.queues.values():
            while not queue.empty():
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
        
        logger.info("Message bus shutdown")
