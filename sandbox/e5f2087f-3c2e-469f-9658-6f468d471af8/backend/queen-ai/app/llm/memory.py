"""
Conversation Memory - Persistent memory across LLM provider switches
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)


class ConversationMemory:
    """
    Persistent conversation memory that survives provider switches
    
    Features:
    - Stores conversation history
    - Survives LLM provider changes
    - Sliding window for context management
    - Importance-based retention
    """
    
    def __init__(self, max_exchanges: int = 100):
        self.max_exchanges = max_exchanges
        self.memory_file = Path("data/conversation_memory.json")
        self.exchanges: List[Dict[str, Any]] = []
        self._load_memory()
    
    def _load_memory(self):
        """Load memory from disk"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, "r") as f:
                    data = json.load(f)
                    self.exchanges = data.get("exchanges", [])
                logger.info("Conversation memory loaded", exchanges=len(self.exchanges))
            else:
                logger.info("No existing memory file, starting fresh")
        except Exception as e:
            logger.error("Failed to load conversation memory", error=str(e))
    
    def _save_memory(self):
        """Save memory to disk"""
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "exchanges": self.exchanges[-self.max_exchanges:],  # Keep only recent
                "last_updated": datetime.utcnow().isoformat(),
            }
            with open(self.memory_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug("Conversation memory saved")
        except Exception as e:
            logger.error("Failed to save conversation memory", error=str(e))
    
    async def add_exchange(
        self,
        user_prompt: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a conversation exchange to memory"""
        exchange = {
            "user": user_prompt,
            "assistant": assistant_response,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        
        self.exchanges.append(exchange)
        
        # Trim if exceeds max
        if len(self.exchanges) > self.max_exchanges:
            self.exchanges = self.exchanges[-self.max_exchanges:]
        
        self._save_memory()
        
        logger.debug("Exchange added to memory", total=len(self.exchanges))
    
    async def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation exchanges"""
        return self.exchanges[-limit:]
    
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search memory for relevant exchanges"""
        # Simple keyword search (in production, would use embeddings)
        results = []
        query_lower = query.lower()
        
        for exchange in reversed(self.exchanges):
            user_text = exchange.get("user", "").lower()
            assistant_text = exchange.get("assistant", "").lower()
            
            if query_lower in user_text or query_lower in assistant_text:
                results.append(exchange)
                if len(results) >= limit:
                    break
        
        return results
    
    async def clear(self):
        """Clear all memory"""
        self.exchanges = []
        self._save_memory()
        logger.info("Conversation memory cleared")
    
    def get_context_string(self, limit: int = 10) -> str:
        """Get recent exchanges as formatted string for LLM context"""
        recent = self.exchanges[-limit:]
        
        if not recent:
            return ""
        
        context_lines = ["Previous conversation:"]
        for exchange in recent:
            context_lines.append(f"User: {exchange['user']}")
            context_lines.append(f"Assistant: {exchange['assistant']}")
        
        return "\n".join(context_lines)
