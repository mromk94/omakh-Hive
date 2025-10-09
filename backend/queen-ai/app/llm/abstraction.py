"""
LLM Provider Abstraction Layer
Supports: Gemini (default), OpenAI, Anthropic, X Grok
"""
from typing import Optional, Dict, List, Any
import structlog
from abc import ABC, abstractmethod

from app.config.settings import settings
from app.llm.providers.gemini import GeminiProvider
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.anthropic import AnthropicProvider
from app.llm.memory import ConversationMemory

logger = structlog.get_logger(__name__)


class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate completion"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is available"""
        pass


class LLMAbstraction:
    """
    Unified LLM interface with provider switching
    
    Features:
    - Multi-provider support (Gemini, OpenAI, Anthropic)
    - Seamless switching without state loss
    - Memory persistence across providers
    - Cost tracking
    - Automatic failover
    """
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.current_provider = settings.DEFAULT_LLM_PROVIDER
        self.memory = ConversationMemory()
        self.costs = {"total": 0.0, "by_provider": {}}
        self.initialized = False
        
    async def initialize(self):
        """Initialize all configured providers"""
        logger.info("Initializing LLM providers")
        
        # Initialize Gemini (default)
        if settings.GEMINI_API_KEY:
            try:
                self.providers["gemini"] = GeminiProvider()
                await self.providers["gemini"].initialize()
                logger.info("✅ Gemini provider ready")
            except Exception as e:
                logger.warning("Failed to initialize Gemini", error=str(e))
        
        # Initialize OpenAI
        if settings.OPENAI_API_KEY:
            try:
                self.providers["openai"] = OpenAIProvider()
                await self.providers["openai"].initialize()
                logger.info("✅ OpenAI provider ready")
            except Exception as e:
                logger.warning("Failed to initialize OpenAI", error=str(e))
        
        # Initialize Anthropic
        if settings.ANTHROPIC_API_KEY:
            try:
                self.providers["anthropic"] = AnthropicProvider()
                await self.providers["anthropic"].initialize()
                logger.info("✅ Anthropic provider ready")
            except Exception as e:
                logger.warning("Failed to initialize Anthropic", error=str(e))
        
        if not self.providers:
            logger.warning("⚠️  No LLM providers configured - running in non-LLM mode")
            self.initialized = True
            return
        
        # Verify current provider is available
        if self.current_provider not in self.providers:
            # Fallback to first available
            self.current_provider = list(self.providers.keys())[0]
            logger.info(f"Defaulting to {self.current_provider} provider")
        
        self.initialized = True
        logger.info(f"Active providers: {list(self.providers.keys())}")
    
    async def generate(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        provider: Optional[str] = None,
        use_memory: bool = True,
    ) -> str:
        """
        Generate completion with memory persistence
        
        Args:
            prompt: User prompt
            context: Additional context
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            provider: Specific provider to use (optional)
            use_memory: Whether to use conversation memory
            
        Returns:
            Generated text
        """
        if not self.providers:
            logger.warning("No LLM providers available, returning placeholder")
            return "[LLM NOT CONFIGURED - Would generate response here]"
        
        # Use specified provider or current default
        provider_name = provider or self.current_provider
        
        if provider_name not in self.providers:
            logger.warning(f"Provider {provider_name} not available, using fallback")
            provider_name = list(self.providers.keys())[0]
        
        provider_instance = self.providers[provider_name]
        
        # Build full prompt with conversation history
        if use_memory:
            full_prompt = await self._build_prompt_with_memory(prompt, context)
        else:
            full_prompt = prompt
        
        # Generate
        try:
            response = await provider_instance.generate(
                prompt=full_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Save to memory
            if use_memory:
                await self.memory.add_exchange(
                    prompt,
                    response,
                    metadata={
                        "provider": provider_name,
                        "temperature": temperature,
                        "context": context,
                    }
                )
            
            # Track cost
            cost = self._calculate_cost(provider_name, full_prompt, response)
            self._track_cost(provider_name, cost)
            
            logger.info(
                "Generated response",
                provider=provider_name,
                input_tokens=len(full_prompt.split()),
                output_tokens=len(response.split()),
                cost=f"${cost:.6f}",
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Generation failed with {provider_name}", error=str(e))
            
            # Try failover to another provider
            if len(self.providers) > 1:
                return await self._failover_generate(
                    prompt, context, temperature, max_tokens, provider_name, use_memory
                )
            raise
    
    async def switch_provider(self, provider: str):
        """
        Switch to different provider (memory persists)
        
        Args:
            provider: Provider name
        """
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available. Available: {list(self.providers.keys())}")
        
        old_provider = self.current_provider
        self.current_provider = provider
        
        logger.info(f"Switched provider: {old_provider} → {provider}")
    
    async def _build_prompt_with_memory(
        self, prompt: str, context: Optional[Dict]
    ) -> str:
        """Build prompt with conversation history"""
        history = await self.memory.get_recent(limit=5)
        
        parts = []
        
        # Add context if provided
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            parts.append(f"Context:\n{context_str}\n")
        
        # Add conversation history
        if history:
            parts.append("Previous conversation:")
            for exchange in history:
                parts.append(f"User: {exchange['user']}")
                parts.append(f"Assistant: {exchange['assistant']}")
            parts.append("")
        
        # Add current prompt
        parts.append(f"User: {prompt}")
        parts.append("Assistant:")
        
        return "\n".join(parts)
    
    async def _failover_generate(
        self, prompt, context, temperature, max_tokens, failed_provider, use_memory
    ):
        """Try other providers on failure"""
        for provider_name, provider in self.providers.items():
            if provider_name == failed_provider:
                continue
            
            try:
                logger.info(f"Failing over to {provider_name}")
                return await self.generate(
                    prompt, context, temperature, max_tokens, provider_name, use_memory
                )
            except Exception as e:
                logger.warning(f"Failover to {provider_name} also failed", error=str(e))
                continue
        
        raise Exception("All providers failed")
    
    def _calculate_cost(
        self, provider: str, prompt: str, response: str
    ) -> float:
        """Calculate cost for this generation"""
        # Rough token estimation (actual would use tokenizer)
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(response.split()) * 1.3
        
        # Pricing (per 1M tokens) - Updated rates
        pricing = {
            "gemini": {"input": 0.075, "output": 0.30},    # Gemini Flash
            "openai": {"input": 30.0, "output": 60.0},     # GPT-4
            "anthropic": {"input": 3.0, "output": 15.0},   # Claude 3.5 Sonnet
        }
        
        rates = pricing.get(provider, {"input": 1.0, "output": 3.0})
        
        cost = (
            (input_tokens / 1_000_000) * rates["input"] +
            (output_tokens / 1_000_000) * rates["output"]
        )
        
        return round(cost, 8)
    
    def _track_cost(self, provider: str, cost: float):
        """Track cost metrics"""
        self.costs["total"] += cost
        if provider not in self.costs["by_provider"]:
            self.costs["by_provider"][provider] = 0.0
        self.costs["by_provider"][provider] += cost
    
    async def health_check(self) -> bool:
        """Check if current provider is healthy"""
        if not self.providers:
            return True  # Non-LLM mode is "healthy"
        
        provider = self.providers.get(self.current_provider)
        if not provider:
            return False
        return await provider.health_check()
    
    def get_costs(self) -> Dict[str, Any]:
        """Get cost tracking data"""
        return self.costs.copy()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    async def shutdown(self):
        """Shutdown all providers"""
        for name, provider in self.providers.items():
            try:
                await provider.shutdown()
                logger.info(f"Shutdown {name} provider")
            except Exception as e:
                logger.error(f"Error shutting down {name}", error=str(e))
