"""
Base Bee Class - Template for all bee agents

All bees have optional LLM access for intelligent reasoning.
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)


class BaseBee(ABC):
    """
    Base class for all bee agents
    
    Each bee specializes in a specific task:
    - MathsBee: AMM calculations, pool analysis
    - SecurityBee: Validation, risk assessment
    - DataBee: Blockchain queries, data aggregation
    - TreasuryBee: Treasury management
    - GovernanceBee: DAO governance, proposals, voting
    
    Features:
    - Optional LLM access for intelligent reasoning
    - Task processing with metrics
    - Health monitoring
    - Error handling
    """
    
    def __init__(self, bee_id: Optional[int] = None, name: str = "BaseBee", llm_enabled: bool = False):
        self.bee_id = bee_id
        self.name = name
        self.status = "initialized"  # initialized, active, paused, error
        self.task_count = 0
        self.success_count = 0
        self.error_count = 0
        self.last_task_time: Optional[datetime] = None
        
        # LLM Integration (optional - for bees that need reasoning)
        self.llm_enabled = llm_enabled
        self.llm = None  # Will be set by BeeManager if LLM enabled
        
        # Elastic Search Integration (for activity logging)
        self.elastic = None  # Will be set by BeeManager if Elastic enabled
    
    def set_llm(self, llm_abstraction):
        """
        Set LLM abstraction layer for this bee
        
        Called by BeeManager to provide LLM access to bees that need it
        """
        if self.llm_enabled:
            self.llm = llm_abstraction
            logger.info(f"{self.name} LLM enabled")
    
    async def use_llm(self, prompt: str, temperature: float = 0.7, **kwargs) -> Optional[str]:
        """
        Use LLM for reasoning/analysis
        
        Args:
            prompt: The prompt to send to LLM
            temperature: Sampling temperature (0-1)
            **kwargs: Additional LLM parameters
            
        Returns:
            LLM response or None if LLM not available
        """
        if not self.llm_enabled or not self.llm:
            logger.warning(f"{self.name} attempted to use LLM but it's not enabled")
            return None
        
        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=temperature,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"{self.name} LLM error", error=str(e))
            return None
    
    @abstractmethod
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute bee-specific task
        
        Args:
            task_data: Task parameters
            
        Returns:
            Result dictionary with status and data
        """
        pass
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process task with error handling and metrics
        
        Args:
            task_data: Task parameters
            
        Returns:
            Result dictionary
        """
        self.task_count += 1
        self.last_task_time = datetime.utcnow()
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"{self.name} processing task", 
                       bee_id=self.bee_id,
                       task=task_data.get("type"))
            
            # Execute bee-specific logic
            result = await self.execute(task_data)
            
            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Track success
            if result.get("success", True):
                self.success_count += 1
                self.status = "active"
            else:
                self.error_count += 1
            
            # Add metadata
            result["bee_id"] = self.bee_id
            result["bee_name"] = self.name
            result["response_time"] = response_time
            result["timestamp"] = datetime.utcnow().isoformat()
            
            logger.info(f"{self.name} task complete",
                       bee_id=self.bee_id,
                       success=result.get("success", True),
                       response_time=response_time)
            
            # Log to Elastic Search if available
            if self.elastic:
                try:
                    await self.elastic.log_bee_activity(
                        bee_name=self.name,
                        action=task_data.get("type", "unknown"),
                        data=task_data,
                        result=result,
                        success=result.get("success", True),
                        duration_ms=response_time * 1000,
                        tags=[self.name, task_data.get("type", "unknown")]
                    )
                except Exception as e:
                    logger.warning(f"Failed to log to Elastic: {str(e)}")
            
            return result
            
        except Exception as e:
            self.error_count += 1
            self.status = "error"
            
            logger.error(f"{self.name} task failed",
                        bee_id=self.bee_id,
                        error=str(e),
                        exc_info=True)
            
            error_result = {
                "success": False,
                "error": str(e),
                "bee_id": self.bee_id,
                "bee_name": self.name,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Log error to Elastic Search if available
            if self.elastic:
                try:
                    response_time = (datetime.utcnow() - start_time).total_seconds()
                    await self.elastic.log_bee_activity(
                        bee_name=self.name,
                        action=task_data.get("type", "unknown"),
                        data=task_data,
                        result=error_result,
                        success=False,
                        error=str(e),
                        duration_ms=response_time * 1000,
                        tags=[self.name, "error", task_data.get("type", "unknown")]
                    )
                except Exception as log_error:
                    logger.warning(f"Failed to log error to Elastic: {str(log_error)}")
            
            return error_result
    
    async def health_check(self) -> Dict[str, Any]:
        """Check bee health status"""
        success_rate = (self.success_count / self.task_count * 100) if self.task_count > 0 else 100
        
        return {
            "bee_id": self.bee_id,
            "name": self.name,
            "status": self.status,
            "task_count": self.task_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": round(success_rate, 2),
            "last_task": self.last_task_time.isoformat() if self.last_task_time else None,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bee statistics"""
        return {
            "bee_id": self.bee_id,
            "name": self.name,
            "status": self.status,
            "tasks_completed": self.task_count,
            "success_rate": f"{(self.success_count / self.task_count * 100):.1f}%" if self.task_count > 0 else "N/A",
        }
