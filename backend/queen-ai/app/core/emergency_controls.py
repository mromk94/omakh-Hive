"""
Emergency Control System

Provides emergency shutdown, pause, and override capabilities.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class EmergencyLevel(str, Enum):
    """Emergency severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SHUTDOWN = "shutdown"


class SystemState(str, Enum):
    """System operational states"""
    NORMAL = "normal"
    PAUSED = "paused"
    DEGRADED = "degraded"
    EMERGENCY = "emergency"
    SHUTDOWN = "shutdown"


class EmergencyControls:
    """
    Emergency Control System
    
    Features:
    - Emergency shutdown (all operations halt)
    - Pause specific bees
    - Override AI decisions
    - Circuit breaker for failed operations
    - Emergency notifications
    - State recovery
    
    Use Cases:
    - Security breach detected
    - Smart contract vulnerability found
    - Anomalous AI behavior
    - Market manipulation detected
    - System instability
    """
    
    def __init__(self):
        self.system_state = SystemState.NORMAL
        self.paused_bees: set = set()
        self.disabled_features: set = set()
        self.emergency_log: List[Dict[str, Any]] = []
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}  # operation -> {failures, state, last_failure}
        self.max_failures = 5  # Circuit breaker threshold
        self.circuit_breaker_timeout = 60  # seconds before retry
        
    def trigger_emergency_shutdown(
        self,
        reason: str,
        triggered_by: str,
        severity: EmergencyLevel = EmergencyLevel.SHUTDOWN
    ):
        """
        Emergency shutdown - halt all operations
        
        Requires manual restart after resolution
        """
        self.system_state = SystemState.SHUTDOWN
        
        event = {
            "event": "emergency_shutdown",
            "severity": severity.value,
            "reason": reason,
            "triggered_by": triggered_by,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.emergency_log.append(event)
        
        logger.critical(
            "🚨 EMERGENCY SHUTDOWN TRIGGERED",
            reason=reason,
            triggered_by=triggered_by
        )
        
        # TODO: Send alerts (email, SMS, Telegram, Discord)
        # TODO: Pause smart contract interactions
        # TODO: Close open positions
        
    def pause_system(self, reason: str):
        """
        Pause system - stop new operations but maintain state
        
        Less severe than shutdown, can be resumed
        """
        self.system_state = SystemState.PAUSED
        
        event = {
            "event": "system_paused",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.emergency_log.append(event)
        
        logger.warning(
            "⏸️  SYSTEM PAUSED",
            reason=reason
        )
    
    def resume_system(self):
        """Resume paused system"""
        if self.system_state == SystemState.PAUSED:
            self.system_state = SystemState.NORMAL
            
            logger.info("▶️  SYSTEM RESUMED")
        else:
            logger.warning(f"Cannot resume - current state: {self.system_state}")
    
    def pause_bee(self, bee_name: str, reason: str):
        """
        Pause specific bee
        
        Bee will not receive or process tasks
        """
        self.paused_bees.add(bee_name)
        
        event = {
            "event": "bee_paused",
            "bee_name": bee_name,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.emergency_log.append(event)
        
        logger.warning(
            f"Bee paused: {bee_name}",
            reason=reason
        )
    
    def resume_bee(self, bee_name: str):
        """Resume paused bee"""
        if bee_name in self.paused_bees:
            self.paused_bees.remove(bee_name)
            logger.info(f"Bee resumed: {bee_name}")
    
    def is_bee_paused(self, bee_name: str) -> bool:
        """Check if bee is paused"""
        return bee_name in self.paused_bees
    
    def disable_feature(self, feature: str, reason: str):
        """
        Disable specific feature
        
        Examples: "staking", "governance", "private_sale"
        """
        self.disabled_features.add(feature)
        
        logger.warning(
            f"Feature disabled: {feature}",
            reason=reason
        )
    
    def enable_feature(self, feature: str):
        """Re-enable feature"""
        if feature in self.disabled_features:
            self.disabled_features.remove(feature)
            logger.info(f"Feature enabled: {feature}")
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        return feature not in self.disabled_features
    
    def record_failure(self, operation: str) -> bool:
        """
        Record operation failure for circuit breaker with time-based reset
        
        Returns:
            True if circuit breaker triggered (too many failures)
        """
        from datetime import datetime
        
        now = datetime.now()
        
        if operation not in self.circuit_breakers:
            self.circuit_breakers[operation] = {
                "failures": 0,
                "state": "CLOSED",
                "last_failure": None
            }
        
        breaker = self.circuit_breakers[operation]
        
        # Check if we should reset (timeout expired)
        if breaker["state"] == "OPEN" and breaker["last_failure"]:
            seconds_since_failure = (now - breaker["last_failure"]).total_seconds()
            if seconds_since_failure > self.circuit_breaker_timeout:
                breaker["state"] = "HALF_OPEN"
                breaker["failures"] = 0
                logger.info(f"Circuit breaker {operation} moved to HALF_OPEN (testing)")
        
        # Record failure
        breaker["failures"] += 1
        breaker["last_failure"] = now
        
        # Trigger circuit breaker
        if breaker["failures"] >= self.max_failures:
            breaker["state"] = "OPEN"
            logger.error(
                f"⚡ CIRCUIT BREAKER TRIGGERED",
                operation=operation,
                failures=breaker["failures"],
                state="OPEN"
            )
            
            # Auto-disable the operation
            self.disable_feature(operation, "Circuit breaker - too many failures")
            
            return True
        
        return False
    
    def reset_circuit_breaker(self, operation: str):
        """Reset circuit breaker for operation"""
        if operation in self.circuit_breakers:
            self.circuit_breakers[operation] = {
                "failures": 0,
                "state": "CLOSED",
                "last_failure": None
            }
            logger.info(f"Circuit breaker reset: {operation}")
    
    def record_success(self, operation: str):
        """Record successful operation (for HALF_OPEN state)"""
        if operation in self.circuit_breakers:
            breaker = self.circuit_breakers[operation]
            if breaker["state"] == "HALF_OPEN":
                breaker["state"] = "CLOSED"
                breaker["failures"] = 0
                logger.info(f"Circuit breaker {operation} recovered (CLOSED)")
    
    def can_operate(self) -> bool:
        """Check if system can perform operations"""
        return self.system_state in [SystemState.NORMAL, SystemState.DEGRADED]
    
    def get_state(self) -> Dict[str, Any]:
        """Get current emergency state"""
        return {
            "system_state": self.system_state.value,
            "paused_bees": list(self.paused_bees),
            "disabled_features": list(self.disabled_features),
            "circuit_breakers": self.circuit_breakers,
            "recent_events": self.emergency_log[-10:] if self.emergency_log else []
        }
    
    def override_decision(
        self,
        decision_id: str,
        override_value: Any,
        reason: str,
        overridden_by: str
    ):
        """
        Override an AI decision
        
        For when human intervention is needed
        """
        event = {
            "event": "decision_override",
            "decision_id": decision_id,
            "override_value": override_value,
            "reason": reason,
            "overridden_by": overridden_by,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.emergency_log.append(event)
        
        logger.warning(
            f"AI decision overridden",
            decision_id=decision_id,
            by=overridden_by,
            reason=reason
        )
    
    def force_recovery(self):
        """
        Force system recovery from shutdown
        
        ADMIN ONLY - requires manual intervention
        """
        if self.system_state == SystemState.SHUTDOWN:
            self.system_state = SystemState.DEGRADED
            
            logger.warning(
                "🔧 FORCED RECOVERY - System in DEGRADED mode"
            )
            logger.warning(
                "   Investigate and resolve issues before returning to NORMAL"
            )
        else:
            logger.error(f"Cannot force recovery from state: {self.system_state}")


# Global emergency controls instance
emergency_controls = EmergencyControls()
