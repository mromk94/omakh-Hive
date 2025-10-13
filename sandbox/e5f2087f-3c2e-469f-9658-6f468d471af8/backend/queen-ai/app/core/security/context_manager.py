"""
Security Context Manager - Track security state across conversations
Detect escalation patterns and manage user security profiles
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class ThreatLevel(Enum):
    """User threat levels"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event in conversation"""
    timestamp: datetime
    event_type: str  # "injection_attempt", "jailbreak", "info_extraction", etc
    risk_score: int
    details: str
    blocked: bool


@dataclass
class SecurityContext:
    """Security context for a user/session"""
    user_id: str
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    # Threat tracking
    threat_level: ThreatLevel = ThreatLevel.SAFE
    cumulative_risk_score: float = 0.0
    warnings_count: int = 0
    blocks_count: int = 0
    
    # Event history
    events: List[SecurityEvent] = field(default_factory=list)
    
    # Conversation tracking
    message_count: int = 0
    last_10_risk_scores: List[int] = field(default_factory=list)
    
    # Escalation detection
    escalation_detected: bool = False
    escalation_reason: Optional[str] = None
    
    # Actions
    is_blocked: bool = False
    blocked_at: Optional[datetime] = None
    blocked_reason: Optional[str] = None


class SecurityContextManager:
    """
    Manage security contexts across conversations
    
    Responsibilities:
    - Track user security state
    - Detect escalation patterns
    - Manage threat levels
    - Decide when to block users
    - Provide security summaries
    """
    
    def __init__(self):
        """Initialize context manager"""
        self.contexts: Dict[str, SecurityContext] = {}
        self.global_stats = {
            "total_users": 0,
            "blocked_users": 0,
            "total_threats": 0,
            "escalations_detected": 0
        }
    
    def get_or_create_context(
        self, 
        user_id: str, 
        session_id: Optional[str] = None
    ) -> SecurityContext:
        """
        Get existing context or create new one
        
        Args:
            user_id: User identifier
            session_id: Optional session identifier
            
        Returns:
            SecurityContext for user
        """
        if user_id not in self.contexts:
            self.contexts[user_id] = SecurityContext(
                user_id=user_id,
                session_id=session_id
            )
            self.global_stats["total_users"] += 1
            
            logger.info("Created new security context", user_id=user_id)
        
        return self.contexts[user_id]
    
    def update_threat_level(
        self,
        context: SecurityContext,
        new_risk_score: int,
        event_type: str,
        details: str,
        blocked: bool = False
    ):
        """
        Update threat level based on new risk score
        
        Args:
            context: Security context to update
            new_risk_score: New risk score (0-100)
            event_type: Type of security event
            details: Event details
            blocked: Whether the input was blocked
        """
        # Update activity
        context.last_activity = datetime.utcnow()
        context.message_count += 1
        
        # Add event
        event = SecurityEvent(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            risk_score=new_risk_score,
            details=details,
            blocked=blocked
        )
        context.events.append(event)
        
        # Keep only last 50 events
        if len(context.events) > 50:
            context.events = context.events[-50:]
        
        # Update risk score tracking
        context.last_10_risk_scores.append(new_risk_score)
        if len(context.last_10_risk_scores) > 10:
            context.last_10_risk_scores = context.last_10_risk_scores[-10:]
        
        # Calculate exponential moving average
        # Give more weight to recent scores
        context.cumulative_risk_score = (
            context.cumulative_risk_score * 0.7 + new_risk_score * 0.3
        )
        
        # Update counts
        if new_risk_score > 50:
            context.warnings_count += 1
            self.global_stats["total_threats"] += 1
        
        if blocked:
            context.blocks_count += 1
        
        # Determine threat level
        old_level = context.threat_level
        context.threat_level = self._calculate_threat_level(context)
        
        # Log if threat level increased
        if context.threat_level != old_level:
            logger.warning(
                "User threat level changed",
                user_id=context.user_id,
                old_level=old_level.value,
                new_level=context.threat_level.value,
                cumulative_score=round(context.cumulative_risk_score, 2)
            )
        
        # Check for escalation
        if self._detect_escalation(context):
            if not context.escalation_detected:
                context.escalation_detected = True
                context.escalation_reason = "Multi-turn attack pattern detected"
                self.global_stats["escalations_detected"] += 1
                
                logger.error(
                    "Escalation pattern detected",
                    user_id=context.user_id,
                    warnings=context.warnings_count,
                    avg_risk=round(sum(context.last_10_risk_scores) / len(context.last_10_risk_scores), 2)
                )
    
    def _calculate_threat_level(self, context: SecurityContext) -> ThreatLevel:
        """Calculate threat level from context"""
        score = context.cumulative_risk_score
        
        # Factor in warnings and blocks
        if context.blocks_count > 3:
            return ThreatLevel.CRITICAL
        
        if score >= 80:
            return ThreatLevel.CRITICAL
        elif score >= 60:
            return ThreatLevel.HIGH
        elif score >= 40:
            return ThreatLevel.MEDIUM
        elif score >= 20:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.SAFE
    
    def _detect_escalation(self, context: SecurityContext) -> bool:
        """
        Detect escalation pattern in conversation
        
        Escalation indicators:
        - Multiple warnings in short time
        - Increasing risk scores
        - Repeated similar attacks
        """
        # Need at least 5 messages
        if len(context.last_10_risk_scores) < 5:
            return False
        
        # Check for increasing trend
        recent_5 = context.last_10_risk_scores[-5:]
        if all(recent_5[i] <= recent_5[i+1] for i in range(len(recent_5)-1)):
            # Monotonically increasing
            return True
        
        # Check for multiple high-risk attempts
        high_risk_count = sum(1 for score in recent_5 if score > 60)
        if high_risk_count >= 3:
            return True
        
        # Check for rapid warnings
        recent_events = [e for e in context.events if e.timestamp > datetime.utcnow() - timedelta(minutes=5)]
        high_risk_events = [e for e in recent_events if e.risk_score > 50]
        if len(high_risk_events) >= 3:
            return True
        
        return False
    
    def should_block_user(self, context: SecurityContext) -> Tuple[bool, Optional[str]]:
        """
        Decide if user should be blocked
        
        Args:
            context: Security context
            
        Returns:
            (should_block, reason)
        """
        # Already blocked
        if context.is_blocked:
            return True, context.blocked_reason
        
        # Critical threat level
        if context.threat_level == ThreatLevel.CRITICAL:
            return True, "Critical threat level reached"
        
        # Too many blocks
        if context.blocks_count > 5:
            return True, f"Exceeded block limit ({context.blocks_count} attempts)"
        
        # Escalation detected with high threat
        if context.escalation_detected and context.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            return True, "Escalating attack pattern detected"
        
        # Very high cumulative score
        if context.cumulative_risk_score > 85:
            return True, f"Cumulative risk score too high ({context.cumulative_risk_score:.1f})"
        
        return False, None
    
    def block_user(
        self,
        context: SecurityContext,
        reason: str,
        duration_minutes: Optional[int] = None
    ):
        """
        Block a user
        
        Args:
            context: Security context
            reason: Reason for blocking
            duration_minutes: Optional auto-unblock duration
        """
        context.is_blocked = True
        context.blocked_at = datetime.utcnow()
        context.blocked_reason = reason
        
        self.global_stats["blocked_users"] += 1
        
        logger.error(
            "User blocked",
            user_id=context.user_id,
            reason=reason,
            threat_level=context.threat_level.value,
            cumulative_score=context.cumulative_risk_score,
            duration_minutes=duration_minutes
        )
    
    def unblock_user(self, user_id: str):
        """Unblock a user"""
        if user_id in self.contexts:
            context = self.contexts[user_id]
            context.is_blocked = False
            context.blocked_at = None
            context.blocked_reason = None
            
            logger.info("User unblocked", user_id=user_id)
    
    def get_security_summary(self, context: SecurityContext) -> Dict[str, Any]:
        """
        Get security summary for context
        
        Args:
            context: Security context
            
        Returns:
            Summary dict
        """
        recent_events = context.events[-10:]  # Last 10 events
        
        return {
            "user_id": context.user_id,
            "threat_level": context.threat_level.value,
            "cumulative_risk_score": round(context.cumulative_risk_score, 2),
            "warnings_count": context.warnings_count,
            "blocks_count": context.blocks_count,
            "message_count": context.message_count,
            "is_blocked": context.is_blocked,
            "blocked_reason": context.blocked_reason,
            "escalation_detected": context.escalation_detected,
            "recent_risk_scores": context.last_10_risk_scores,
            "avg_recent_risk": (
                round(sum(context.last_10_risk_scores) / len(context.last_10_risk_scores), 2)
                if context.last_10_risk_scores else 0
            ),
            "recent_events": [
                {
                    "type": e.event_type,
                    "risk_score": e.risk_score,
                    "blocked": e.blocked,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in recent_events
            ],
            "session_duration_minutes": (
                (datetime.utcnow() - context.created_at).total_seconds() / 60
            )
        }
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global security statistics"""
        return {
            **self.global_stats,
            "active_contexts": len(self.contexts),
            "threat_distribution": {
                level.value: sum(
                    1 for c in self.contexts.values()
                    if c.threat_level == level
                )
                for level in ThreatLevel
            }
        }
    
    def cleanup_old_contexts(self, inactive_hours: int = 24):
        """Remove inactive contexts"""
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=inactive_hours)
        
        to_remove = [
            user_id for user_id, context in self.contexts.items()
            if context.last_activity < cutoff and not context.is_blocked
        ]
        
        for user_id in to_remove:
            del self.contexts[user_id]
        
        if to_remove:
            logger.info(f"Cleaned up {len(to_remove)} inactive security contexts")
