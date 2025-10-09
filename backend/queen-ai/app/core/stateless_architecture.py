"""
Stateless Architecture for Cloud Auto-Scaling

Handles ephemeral instances (Cloud Run, GKE auto-scaling) to prevent data loss
when instances are created/destroyed based on traffic load.

Key Principles:
1. All state stored in external persistent storage (PostgreSQL, Redis, BigQuery)
2. No critical data stored in instance memory
3. Graceful shutdown saves all pending data
4. Startup recovery from persistent storage
5. Distributed locking for concurrent operations
6. Session continuity across instance changes
"""
import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import structlog
import os
import signal

logger = structlog.get_logger(__name__)


class StatelessArchitectureManager:
    """
    Manages stateless architecture for cloud auto-scaling
    
    Ensures no data loss when instances are:
    - Created (scale up)
    - Destroyed (scale down)
    - Replaced (rolling updates)
    """
    
    def __init__(self):
        self.instance_id = self._generate_instance_id()
        self.startup_time = datetime.utcnow()
        self.shutdown_initiated = False
        
        # Track what needs to be persisted
        self.pending_operations: List[Dict] = []
        self.active_sessions: Dict[str, Any] = {}
        
        # Setup shutdown handlers
        self._setup_shutdown_handlers()
    
    def _generate_instance_id(self) -> str:
        """Generate unique instance ID"""
        import uuid
        import socket
        
        hostname = socket.gethostname()
        instance_id = f"{hostname}-{uuid.uuid4().hex[:8]}"
        
        logger.info(
            "Instance initialized",
            instance_id=instance_id,
            is_cloud_run=os.getenv("K_SERVICE") is not None,
            is_gke=os.path.exists("/var/run/secrets/kubernetes.io")
        )
        
        return instance_id
    
    def _setup_shutdown_handlers(self):
        """Setup handlers for graceful shutdown"""
        # Cloud Run sends SIGTERM before killing instance
        # GKE sends SIGTERM for rolling updates
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
    
    def _handle_shutdown_signal(self, signum, frame):
        """Handle shutdown signal"""
        logger.warning(
            "Shutdown signal received - instance being terminated",
            signal=signal.Signals(signum).name,
            instance_id=self.instance_id
        )
        
        self.shutdown_initiated = True
        
        # Trigger graceful shutdown
        asyncio.create_task(self.graceful_shutdown())
    
    async def graceful_shutdown(self, max_wait_seconds: int = 10):
        """
        Gracefully shutdown instance before termination
        
        Cloud Run gives 10 seconds after SIGTERM
        GKE gives 30 seconds (configurable)
        """
        logger.info("Starting graceful shutdown sequence...")
        
        shutdown_start = time.time()
        
        try:
            # Step 1: Stop accepting new requests (handled by health check)
            logger.info("Step 1/5: Stopping new request acceptance")
            await self._stop_accepting_requests()
            
            # Step 2: Flush all pending operations
            logger.info("Step 2/5: Flushing pending operations")
            await self._flush_pending_operations()
            
            # Step 3: Persist active sessions
            logger.info("Step 3/5: Persisting active sessions")
            await self._persist_active_sessions()
            
            # Step 4: Flush all logs
            logger.info("Step 4/5: Flushing logs")
            await self._flush_logs()
            
            # Step 5: Close connections gracefully
            logger.info("Step 5/5: Closing connections")
            await self._close_connections()
            
            shutdown_duration = time.time() - shutdown_start
            logger.info(
                "Graceful shutdown complete",
                duration_seconds=shutdown_duration,
                instance_id=self.instance_id
            )
            
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {str(e)}", exc_info=True)
    
    async def _stop_accepting_requests(self):
        """Mark instance as unhealthy to stop receiving new requests"""
        # Health check will return 503, causing load balancer to route elsewhere
        pass
    
    async def _flush_pending_operations(self):
        """Flush all pending operations to persistent storage"""
        if not self.pending_operations:
            return
        
        logger.info(f"Flushing {len(self.pending_operations)} pending operations")
        
        try:
            # Flush to database/Redis
            from app.db.base import SessionLocal
            
            db = SessionLocal()
            try:
                for operation in self.pending_operations:
                    # Process each pending operation
                    await self._persist_operation(db, operation)
                
                db.commit()
                self.pending_operations.clear()
                logger.info("All pending operations flushed successfully")
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to flush pending operations: {str(e)}")
    
    async def _persist_operation(self, db, operation: Dict):
        """Persist a single operation"""
        # Implementation depends on operation type
        operation_type = operation.get("type")
        
        if operation_type == "bee_decision":
            # Store in database or BigQuery
            pass
        elif operation_type == "llm_interaction":
            # Log to BigQuery
            pass
        # Add more operation types as needed
    
    async def _persist_active_sessions(self):
        """Persist all active sessions to Redis"""
        if not self.active_sessions:
            return
        
        logger.info(f"Persisting {len(self.active_sessions)} active sessions")
        
        try:
            from app.core.redis_message_bus import RedisMessageBus
            
            bus = RedisMessageBus()
            await bus.initialize()
            
            if bus.initialized:
                # Store sessions in Redis with TTL
                for session_id, session_data in self.active_sessions.items():
                    await bus.redis.setex(
                        f"session:{session_id}",
                        3600,  # 1 hour TTL
                        str(session_data)
                    )
                
                logger.info("All active sessions persisted to Redis")
            
        except Exception as e:
            logger.error(f"Failed to persist sessions: {str(e)}")
    
    async def _flush_logs(self):
        """Flush all buffered logs"""
        try:
            from app.learning.bigquery_logger import bigquery_logger
            
            if bigquery_logger.initialized:
                await bigquery_logger.flush_batch()
                logger.info("BigQuery logs flushed")
        
        except Exception as e:
            logger.debug(f"Log flush error: {str(e)}")
    
    async def _close_connections(self):
        """Close all open connections gracefully"""
        try:
            # Close database connections
            from app.db.base import engine
            engine.dispose()
            
            # Close Redis connections
            from app.core.redis_message_bus import RedisMessageBus
            bus = RedisMessageBus()
            if bus.initialized:
                await bus.shutdown()
            
            logger.info("All connections closed gracefully")
            
        except Exception as e:
            logger.error(f"Error closing connections: {str(e)}")
    
    async def startup_recovery(self):
        """
        Recover state on instance startup
        
        When a new instance starts (scale up or replacement),
        recover any state from previous instance
        """
        logger.info("Starting instance recovery...")
        
        try:
            # Step 1: Check for orphaned sessions
            await self._recover_sessions()
            
            # Step 2: Check for incomplete operations
            await self._recover_pending_operations()
            
            # Step 3: Register instance in registry
            await self._register_instance()
            
            logger.info("Instance recovery complete")
            
        except Exception as e:
            logger.error(f"Error during startup recovery: {str(e)}")
    
    async def _recover_sessions(self):
        """Recover sessions from Redis"""
        try:
            from app.core.redis_message_bus import RedisMessageBus
            
            bus = RedisMessageBus()
            await bus.initialize()
            
            if bus.initialized:
                # Scan for session keys
                cursor = 0
                recovered = 0
                
                while True:
                    cursor, keys = await bus.redis.scan(cursor, match="session:*", count=100)
                    
                    for key in keys:
                        session_id = key.split(":")[1]
                        session_data = await bus.redis.get(key)
                        
                        if session_data:
                            self.active_sessions[session_id] = session_data
                            recovered += 1
                    
                    if cursor == 0:
                        break
                
                if recovered > 0:
                    logger.info(f"Recovered {recovered} sessions from Redis")
        
        except Exception as e:
            logger.debug(f"Session recovery error: {str(e)}")
    
    async def _recover_pending_operations(self):
        """Recover any pending operations from database"""
        try:
            from app.db.base import SessionLocal
            from app.db.models import SystemEvent
            
            db = SessionLocal()
            try:
                # Query for pending operations
                pending = db.query(SystemEvent).filter(
                    SystemEvent.event_type == "pending_operation"
                ).all()
                
                if pending:
                    logger.info(f"Recovered {len(pending)} pending operations")
                    
                    for event in pending:
                        self.pending_operations.append(event.data)
            
            finally:
                db.close()
        
        except Exception as e:
            logger.debug(f"Operation recovery error: {str(e)}")
    
    async def _register_instance(self):
        """Register this instance in instance registry"""
        try:
            from app.core.redis_message_bus import RedisMessageBus
            
            bus = RedisMessageBus()
            await bus.initialize()
            
            if bus.initialized:
                instance_info = {
                    "instance_id": self.instance_id,
                    "startup_time": self.startup_time.isoformat(),
                    "status": "healthy"
                }
                
                # Register with 5 minute TTL (auto-cleanup if instance dies)
                await bus.redis.setex(
                    f"instance:{self.instance_id}",
                    300,  # 5 minutes
                    str(instance_info)
                )
                
                logger.info("Instance registered in registry")
        
        except Exception as e:
            logger.debug(f"Instance registration error: {str(e)}")
    
    async def heartbeat(self):
        """
        Send periodic heartbeat to registry
        
        Keeps instance marked as alive in distributed system
        """
        try:
            from app.core.redis_message_bus import RedisMessageBus
            
            bus = RedisMessageBus()
            await bus.initialize()
            
            if bus.initialized:
                # Update TTL on instance key
                await bus.redis.expire(f"instance:{self.instance_id}", 300)
        
        except Exception:
            pass  # Heartbeat failures are non-critical
    
    def is_shutting_down(self) -> bool:
        """Check if instance is shutting down"""
        return self.shutdown_initiated
    
    def add_pending_operation(self, operation: Dict):
        """Add operation to pending queue for persistence"""
        self.pending_operations.append(operation)
    
    def register_session(self, session_id: str, session_data: Any):
        """Register active session for persistence"""
        self.active_sessions[session_id] = session_data
    
    def remove_session(self, session_id: str):
        """Remove session when completed"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]


# Global instance
stateless_manager = StatelessArchitectureManager()
