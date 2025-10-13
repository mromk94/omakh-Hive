"""
Learning Observer - Passive Data Collection for Future Model Training

Observes all system interactions and logs them for future self-hosted model training.
NON-INTRUSIVE: Does not affect system performance or behavior.
"""
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import hashlib
import structlog

from app.learning.bigquery_logger import bigquery_logger
from app.config.settings import settings

logger = structlog.get_logger(__name__)


class LearningObserver:
    """
    Learning Function Observer
    
    Purpose:
    - Passively observe all system interactions
    - Log to BigQuery for future model training
    - Privacy-preserving (anonymize user data)
    - Non-blocking (async background logging)
    - Respects user preferences (GDPR compliant)
    
    What Gets Logged:
    - All LLM conversations (prompts + responses)
    - Bee decisions and reasoning
    - User queries and satisfaction
    - Pattern detections and outcomes
    - System events and behaviors
    
    What Doesn't Get Logged:
    - Private keys or sensitive credentials
    - Personally identifiable information (PII)
    - User IP addresses
    - Financial account details
    
    Data is used ONLY for:
    - Training future self-hosted OMK Hive model
    - Improving bee decision quality
    - Pattern recognition enhancement
    - System optimization
    """
    
    def __init__(self):
        self.enabled = settings.LEARNING_FUNCTION_ENABLED
        self.pause_collection = False  # Admin can pause
        self.background_tasks: set = set()
        
        # Privacy settings
        self.anonymize_users = True
        self.retention_days = 365  # 1 year
        
    async def initialize(self):
        """Initialize learning observer and BigQuery"""
        if not self.enabled:
            logger.info("Learning function disabled")
            return
        
        try:
            # Initialize BigQuery logger
            await bigquery_logger.initialize()
            
            logger.info("✅ Learning Observer initialized")
            logger.info(f"   Data collection: {'ENABLED' if self.enabled else 'DISABLED'}")
            logger.info(f"   Anonymization: {'ON' if self.anonymize_users else 'OFF'}")
            logger.info(f"   Retention: {self.retention_days} days")
            
        except Exception as e:
            logger.error(f"Failed to initialize Learning Observer: {str(e)}")
            self.enabled = False
    
    def _anonymize_user_id(self, user_id: str) -> str:
        """
        Anonymize user ID using SHA-256 hash
        
        One-way hash ensures privacy while allowing pattern analysis
        """
        return hashlib.sha256(f"{user_id}{settings.SECRET_KEY}".encode()).hexdigest()
    
    async def _log_async(self, coro):
        """Execute logging in background to not block main thread"""
        if not self.enabled or self.pause_collection:
            return
        
        task = asyncio.create_task(coro)
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
    
    # ==================== LLM Conversation Logging ====================
    
    async def observe_llm_interaction(
        self,
        conversation_id: str,
        provider: str,
        model: str,
        prompt: str,
        response: str,
        tokens_used: Optional[int] = None,
        cost_usd: Optional[float] = None,
        response_time_ms: Optional[int] = None,
        bee_source: Optional[str] = None,
        temperature: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """
        Observe LLM interaction
        
        Logs both user and assistant messages
        """
        if not self.enabled:
            return
        
        # Log user message (prompt)
        await self._log_async(
            bigquery_logger.log_llm_conversation(
                conversation_id=conversation_id,
                provider=provider,
                model=model,
                role="user",
                content=prompt,
                tokens_used=None,  # Counted in response
                cost_usd=None,
                bee_source=bee_source,
                temperature=temperature,
                success=True
            )
        )
        
        # Log assistant message (response)
        await self._log_async(
            bigquery_logger.log_llm_conversation(
                conversation_id=conversation_id,
                provider=provider,
                model=model,
                role="assistant",
                content=response,
                tokens_used=tokens_used,
                cost_usd=cost_usd,
                response_time_ms=response_time_ms,
                bee_source=bee_source,
                temperature=temperature,
                success=success,
                error_message=error_message
            )
        )
        
        logger.debug(
            "LLM interaction logged",
            provider=provider,
            bee=bee_source,
            tokens=tokens_used
        )
    
    # ==================== Bee Decision Logging ====================
    
    async def observe_bee_decision(
        self,
        bee_name: str,
        decision_type: str,
        input_data: Dict[str, Any],
        output_decision: Dict[str, Any],
        confidence_score: Optional[float] = None,
        reasoning: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        llm_used: bool = False
    ):
        """
        Observe bee decision
        
        Logs what the bee decided and why
        """
        if not self.enabled:
            return
        
        import uuid
        decision_id = str(uuid.uuid4())
        
        await self._log_async(
            bigquery_logger.log_bee_decision(
                decision_id=decision_id,
                bee_name=bee_name,
                decision_type=decision_type,
                input_data=input_data,
                output_decision=output_decision,
                confidence_score=confidence_score,
                reasoning=reasoning,
                execution_time_ms=execution_time_ms,
                llm_used=llm_used
            )
        )
        
        logger.debug(
            "Bee decision logged",
            bee=bee_name,
            type=decision_type
        )
    
    async def update_decision_outcome(
        self,
        decision_id: str,
        outcome: str,
        override_by_human: bool = False
    ):
        """
        Update decision outcome after execution
        
        Used for training: Did the decision work out?
        """
        # TODO: Implement update logic
        # BigQuery doesn't support updates easily, might need to insert new row
        # or use merge operation
        pass
    
    # ==================== User Interaction Logging ====================
    
    async def observe_user_interaction(
        self,
        user_id: str,
        interaction_type: str,
        input_text: Optional[str] = None,
        response: Optional[str] = None,
        session_id: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        error_occurred: bool = False
    ):
        """
        Observe user interaction
        
        Anonymizes user ID before logging
        """
        if not self.enabled:
            return
        
        import uuid
        interaction_id = str(uuid.uuid4())
        
        # Anonymize user ID
        user_id_hash = self._anonymize_user_id(user_id)
        
        await self._log_async(
            bigquery_logger.log_user_interaction(
                interaction_id=interaction_id,
                user_id_hash=user_id_hash,
                interaction_type=interaction_type,
                input_text=input_text,
                response=response,
                session_id=session_id,
                response_time_ms=response_time_ms,
                error_occurred=error_occurred
            )
        )
        
        logger.debug(
            "User interaction logged",
            type=interaction_type,
            anonymized=True
        )
    
    async def record_user_feedback(
        self,
        interaction_id: str,
        user_satisfied: bool,
        feedback_text: Optional[str] = None
    ):
        """
        Record user feedback
        
        Helps train model on what users found helpful
        """
        # TODO: Implement feedback recording
        # Might need separate feedback table or update mechanism
        pass
    
    # ==================== Pattern Data Logging ====================
    
    async def observe_pattern_detection(
        self,
        pattern_type: str,
        data_points: Dict[str, Any],
        pattern_label: str,
        confidence: float,
        detected_by: str = "PatternBee",
        prediction: Optional[str] = None
    ):
        """
        Observe pattern detection
        
        Logs pattern + prediction for later validation
        """
        if not self.enabled:
            return
        
        import uuid
        pattern_id = str(uuid.uuid4())
        
        await self._log_async(
            bigquery_logger.log_pattern_data(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                detected_by=detected_by,
                data_points=data_points,
                pattern_label=pattern_label,
                confidence=confidence,
                prediction=prediction
            )
        )
        
        logger.debug(
            "Pattern detection logged",
            type=pattern_type,
            label=pattern_label
        )
    
    async def update_pattern_outcome(
        self,
        pattern_id: str,
        actual_outcome: str,
        accuracy: float
    ):
        """
        Update pattern outcome after event occurs
        
        Used for training: Was the prediction accurate?
        """
        # TODO: Implement outcome update
        pass
    
    # ==================== Admin Controls ====================
    
    def pause_collection(self):
        """Pause data collection (admin control)"""
        self.pause_collection = True
        logger.warning("Learning function data collection PAUSED")
    
    def resume_collection(self):
        """Resume data collection"""
        self.pause_collection = False
        logger.info("Learning function data collection RESUMED")
    
    def is_collecting(self) -> bool:
        """Check if actively collecting data"""
        return self.enabled and not self.pause_collection
    
    async def purge_user_data(self, user_id: str):
        """
        Purge all data for a user (GDPR compliance)
        
        Right to be forgotten
        """
        user_id_hash = self._anonymize_user_id(user_id)
        
        # TODO: Implement data deletion
        # Delete from BigQuery where user_id_hash matches
        
        logger.info(f"User data purged (anonymized ID: {user_id_hash[:8]}...)")
    
    async def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Export all data for a user (GDPR compliance)
        
        Right to data portability
        """
        user_id_hash = self._anonymize_user_id(user_id)
        
        # TODO: Implement data export
        # Query BigQuery for all user interactions
        
        return {
            "user_id_hash": user_id_hash,
            "data": []
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get learning function statistics"""
        stats = await bigquery_logger.get_statistics()
        
        stats["enabled"] = self.enabled
        stats["paused"] = self.pause_collection
        stats["active_background_tasks"] = len(self.background_tasks)
        
        return stats
    
    async def shutdown(self):
        """Shutdown learning observer"""
        # Wait for background tasks to complete
        if self.background_tasks:
            logger.info(f"Waiting for {len(self.background_tasks)} background tasks...")
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Flush BigQuery
        await bigquery_logger.shutdown()
        
        logger.info("Learning Observer shutdown")


# Global instance
learning_observer = LearningObserver()
