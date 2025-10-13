"""
WebSocket endpoints for real-time admin dashboard updates
"""
import asyncio
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import app.models.database as db
from app.api.v1.admin import verify_admin
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()

# Global queen instance for WebSocket access
queen_instance = None

def set_queen_instance(queen):
    """Set global queen instance for WebSocket access"""
    global queen_instance
    queen_instance = queen
    logger.info("✅ Queen instance registered for WebSocket")

# Connection manager for WebSocket clients
class ConnectionManager:
    MAX_CONNECTIONS_PER_CHANNEL = 100
    HEARTBEAT_INTERVAL = 30  # seconds
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "hive": set(),
            "analytics": set(),
            "bees": set(),
        }
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, channel: str) -> bool:
        # Check connection limit
        if len(self.active_connections.get(channel, set())) >= self.MAX_CONNECTIONS_PER_CHANNEL:
            await websocket.close(code=1008, reason="Channel full")
            logger.warning(f"Connection rejected: {channel} channel full")
            return False
        
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        
        self.active_connections[channel].add(websocket)
        self.connection_metadata[websocket] = {
            "channel": channel,
            "connected_at": asyncio.get_event_loop().time(),
            "last_heartbeat": asyncio.get_event_loop().time()
        }
        
        logger.info(f"WebSocket client connected to {channel}", 
                   total_connections=len(self.active_connections[channel]))
        
        # Start heartbeat
        asyncio.create_task(self._heartbeat(websocket, channel))
        return True
    
    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            if websocket in self.connection_metadata:
                del self.connection_metadata[websocket]
            logger.info(f"WebSocket client disconnected from {channel}",
                       remaining_connections=len(self.active_connections[channel]))
    
    async def _heartbeat(self, websocket: WebSocket, channel: str):
        """Send periodic heartbeat to detect stale connections"""
        while websocket in self.active_connections.get(channel, set()):
            try:
                await websocket.send_json({"type": "ping", "timestamp": asyncio.get_event_loop().time()})
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["last_heartbeat"] = asyncio.get_event_loop().time()
                await asyncio.sleep(self.HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                self.disconnect(websocket, channel)
                break
    
    async def broadcast(self, channel: str, message: dict):
        """Broadcast message to all connected clients on a channel"""
        if channel not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to client: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections[channel].discard(conn)

manager = ConnectionManager()


@router.websocket("/ws/admin/hive")
async def websocket_hive_updates(websocket: WebSocket):
    """
    Real-time Hive Intelligence updates
    Replaces polling for HiveIntelligence and HiveMonitor components
    """
    await manager.connect(websocket, "hive")
    
    try:
        # Send initial data immediately
        await send_hive_update(websocket)
        
        # Then send updates every 5 seconds when data changes
        last_data = None
        while True:
            await asyncio.sleep(5)  # Check for changes every 5s
            
            # Fetch current data
            current_data = await get_hive_data()
            
            # Only send if data changed
            if current_data != last_data:
                await websocket.send_json({
                    "type": "hive_update",
                    "data": current_data,
                    "timestamp": asyncio.get_event_loop().time()
                })
                last_data = current_data
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "hive")
        logger.info("Client disconnected from hive channel")
    except Exception as e:
        logger.error(f"WebSocket error in hive channel: {e}")
        manager.disconnect(websocket, "hive")


@router.websocket("/ws/admin/analytics")
async def websocket_analytics_updates(websocket: WebSocket):
    """
    Real-time Analytics updates
    Replaces polling for EnhancedAnalytics component
    """
    await manager.connect(websocket, "analytics")
    
    try:
        # Send initial data
        await send_analytics_update(websocket)
        
        # Then send updates every 30 seconds
        last_data = None
        while True:
            await asyncio.sleep(30)  # Analytics don't need frequent updates
            
            current_data = await get_analytics_data()
            
            if current_data != last_data:
                await websocket.send_json({
                    "type": "analytics_update",
                    "data": current_data,
                    "timestamp": asyncio.get_event_loop().time()
                })
                last_data = current_data
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "analytics")
        logger.info("Client disconnected from analytics channel")
    except Exception as e:
        logger.error(f"WebSocket error in analytics channel: {e}")
        manager.disconnect(websocket, "analytics")


@router.websocket("/ws/admin/bees")
async def websocket_bee_updates(websocket: WebSocket):
    """
    Real-time Bee monitoring updates
    Specifically for HiveMonitor component
    """
    await manager.connect(websocket, "bees")
    
    try:
        # Send initial bee data
        await send_bee_update(websocket)
        
        # Then send updates every 10 seconds
        last_data = None
        while True:
            await asyncio.sleep(10)
            
            current_data = await get_bee_data()
            
            if current_data != last_data:
                await websocket.send_json({
                    "type": "bee_update",
                    "data": current_data,
                    "timestamp": asyncio.get_event_loop().time()
                })
                last_data = current_data
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "bees")
        logger.info("Client disconnected from bees channel")
    except Exception as e:
        logger.error(f"WebSocket error in bees channel: {e}")
        manager.disconnect(websocket, "bees")


# Helper functions to fetch data
async def get_hive_data() -> dict:
    """Get all hive intelligence data from Queen"""
    global queen_instance
    
    if not queen_instance:
        logger.warning("Queen not initialized for WebSocket")
        return {
            "overview": {},
            "message_stats": {},
            "board_stats": {},
            "bee_performance": {},
            "live_activity": []
        }
    
    try:
        queen = queen_instance
        from datetime import datetime
        
        # Message bus stats
        message_stats = queen.message_bus.get_communication_stats()
        
        # Hive board stats
        board_stats = await queen.hive_board.get_stats()
        
        # Bee performance
        bee_performance = {}
        for bee_name, bee in queen.bee_manager.bees.items():
            bee_performance[bee_name] = {
                "task_count": bee.task_count,
                "success_count": bee.success_count,
                "error_count": bee.error_count,
                "success_rate": (bee.success_count / bee.task_count * 100) if bee.task_count > 0 else 0,
                "last_task_time": bee.last_task_time.isoformat() if bee.last_task_time else None,
                "status": bee.status,
                "llm_enabled": bee.llm_enabled
            }
        
        # Live activity (tasks in last 10 seconds)
        now = datetime.utcnow()
        active_tasks = []
        for bee_name, bee in queen.bee_manager.bees.items():
            if bee.last_task_time:
                time_diff = (now - bee.last_task_time).total_seconds()
                if time_diff < 10:
                    active_tasks.append({
                        "bee_name": bee_name,
                        "status": bee.status,
                        "last_active": bee.last_task_time.isoformat(),
                        "seconds_ago": int(time_diff)
                    })
        
        # Bee health
        bee_health = await queen.bee_manager.check_all_health()
        active_count = sum(1 for bee in queen.bee_manager.bees.values() 
                          if bee.last_task_time and (now - bee.last_task_time).total_seconds() < 10)
        
        # Overview
        overview = {
            "message_bus": {
                "total_messages": message_stats["total_messages"],
                "delivery_rate": message_stats["delivery_rate"],
                "active_bees": message_stats["active_bees"]
            },
            "hive_board": {
                "total_posts": board_stats["total_posts"],
                "active_categories": board_stats["active_categories"],
                "total_subscribers": board_stats["total_subscribers"]
            },
            "bees": {
                "total": len(queen.bee_manager.bees),
                "healthy": len([b for b in bee_health["bees"].values() if b["status"] == "active"]),
                "currently_active": active_count
            },
            "queen": {
                "initialized": queen.initialized,
                "running": queen.running,
                "decision_count": queen.decision_count
            }
        }
        
        return {
            "overview": overview,
            "message_stats": message_stats,
            "board_stats": board_stats,
            "bee_performance": bee_performance,
            "live_activity": active_tasks
        }
        
    except Exception as e:
        logger.error(f"Error fetching hive data: {e}", exc_info=True)
        return {
            "overview": {},
            "message_stats": {},
            "board_stats": {},
            "bee_performance": {},
            "live_activity": []
        }


async def get_analytics_data() -> dict:
    """Get analytics data"""
    try:
        analytics = db.get_analytics()
        users = db.get_all_users()
        
        # Calculate user stats
        total_users = len(users)
        active_users = len([u for u in users if u.get('status') == 'active'])
        pending_users = len([u for u in users if u.get('status') == 'pending'])
        
        return {
            "overview": analytics,
            "users": {
                "total": total_users,
                "active": active_users,
                "pending": pending_users,
                "growth": analytics.get('user_growth', 0)
            },
            "transactions": {
                "total_volume": analytics.get('total_volume', 0),
                "transaction_count": analytics.get('transaction_count', 0),
                "avg_transaction": analytics.get('avg_transaction', 0)
            }
        }
    except Exception as e:
        logger.error(f"Error fetching analytics data: {e}")
        return {}


async def get_bee_data() -> dict:
    """Get bee monitoring data from Queen"""
    global queen_instance
    
    if not queen_instance:
        return {
            "bees": [],
            "total": 0,
            "active": 0,
            "idle": 0
        }
    
    try:
        queen = queen_instance
        from datetime import datetime
        now = datetime.utcnow()
        
        bees = []
        for bee_name, bee in queen.bee_manager.bees.items():
            bees.append({
                "name": bee_name,
                "status": bee.status,
                "task_count": bee.task_count,
                "success_rate": (bee.success_count / bee.task_count * 100) if bee.task_count > 0 else 0,
                "last_active": bee.last_task_time.isoformat() if bee.last_task_time else None,
                "llm_enabled": bee.llm_enabled
            })
        
        active = sum(1 for bee in queen.bee_manager.bees.values() 
                    if bee.last_task_time and (now - bee.last_task_time).total_seconds() < 30)
        
        return {
            "bees": bees,
            "total": len(bees),
            "active": active,
            "idle": len(bees) - active
        }
    except Exception as e:
        logger.error(f"Error fetching bee data: {e}", exc_info=True)
        return {
            "bees": [],
            "total": 0,
            "active": 0,
            "idle": 0
        }


async def send_hive_update(websocket: WebSocket):
    """Send hive update to a specific websocket"""
    data = await get_hive_data()
    await websocket.send_json({
        "type": "hive_update",
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    })


async def send_analytics_update(websocket: WebSocket):
    """Send analytics update to a specific websocket"""
    data = await get_analytics_data()
    await websocket.send_json({
        "type": "analytics_update",
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    })


async def send_bee_update(websocket: WebSocket):
    """Send bee update to a specific websocket"""
    data = await get_bee_data()
    await websocket.send_json({
        "type": "bee_update",
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    })


# Broadcast function for triggering updates from other parts of the system
async def broadcast_hive_update():
    """Broadcast hive update to all connected clients"""
    data = await get_hive_data()
    await manager.broadcast("hive", {
        "type": "hive_update",
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    })


async def broadcast_analytics_update():
    """Broadcast analytics update to all connected clients"""
    data = await get_analytics_data()
    await manager.broadcast("analytics", {
        "type": "analytics_update",
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    })


async def broadcast_bee_update():
    """Broadcast bee update to all connected clients"""
    data = await get_bee_data()
    await manager.broadcast("bees", {
        "type": "bee_update",
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    })
