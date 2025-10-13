"""
State Manager - Manages Queen AI's operational state
"""
from typing import Dict, Any, Optional
from datetime import datetime
import structlog
import json
from pathlib import Path

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class StateManager:
    """
    Manages Queen AI's persistent state
    
    Tracks:
    - Daily transfer usage (rate limiting)
    - Operation history
    - Decision metrics
    - System health status
    """
    
    def __init__(self):
        self.state_file = Path("data/queen_state.json")
        self.state: Dict[str, Any] = {
            "daily_transfers": 0,
            "last_reset": None,
            "operation_count": 0,
            "last_decision": None,
            "metrics": {},
        }
    
    async def load_state(self):
        """Load state from disk"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    self.state = json.load(f)
                logger.info("State loaded from disk")
            else:
                logger.info("No existing state file, starting fresh")
                await self.save_state()
        except Exception as e:
            logger.error("Failed to load state", error=str(e))
    
    async def save_state(self):
        """Save state to disk"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2, default=str)
            logger.debug("State saved to disk")
        except Exception as e:
            logger.error("Failed to save state", error=str(e))
    
    async def update_metrics(self, metrics: Dict[str, Any]):
        """Update cached metrics"""
        self.state["metrics"] = metrics
        self.state["last_update"] = datetime.utcnow().isoformat()
        await self.save_state()
    
    async def record_operation(self, operation_type: str, amount: int):
        """Record an operation"""
        self.state["operation_count"] += 1
        self.state["last_decision"] = {
            "type": operation_type,
            "amount": amount,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.save_state()
    
    async def check_daily_reset(self) -> bool:
        """Check if daily counters should reset"""
        if not self.state.get("last_reset"):
            self.state["last_reset"] = datetime.utcnow().isoformat()
            await self.save_state()
            return True
        
        last_reset = datetime.fromisoformat(self.state["last_reset"])
        now = datetime.utcnow()
        
        if (now - last_reset).total_seconds() >= 86400:  # 24 hours
            self.state["daily_transfers"] = 0
            self.state["last_reset"] = now.isoformat()
            await self.save_state()
            logger.info("Daily counters reset")
            return True
        
        return False
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state"""
        return self.state.copy()
