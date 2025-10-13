"""
Anthropic Provider - Claude 3.5 Sonnet
"""
from typing import Optional
import structlog

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    AsyncAnthropic = None

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class AnthropicProvider:
    """
    Anthropic Claude Provider
    """
    
    def __init__(self):
        self.client: Optional[AsyncAnthropic] = None
        self.initialized = False
        self.model_name = "claude-3-5-sonnet-20241022"  # Latest Claude
    
    async def initialize(self):
        """Initialize Anthropic provider"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic not installed. Run: pip install anthropic")
        
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        try:
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.initialized = True
            logger.info("Anthropic provider initialized", model=self.model_name)
            
        except Exception as e:
            logger.error("Failed to initialize Anthropic", error=str(e))
            raise
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate completion from Claude"""
        if not self.initialized:
            raise RuntimeError("Anthropic provider not initialized")
        
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            text = response.content[0].text
            
            logger.debug("Claude generation complete",
                        input_length=len(prompt),
                        output_length=len(text))
            
            return text
            
        except Exception as e:
            logger.error("Claude generation failed", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check if Claude is available"""
        if not self.initialized:
            return False
        
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=10,
                temperature=0.1,
                messages=[{"role": "user", "content": "Say OK"}]
            )
            return bool(response.content[0].text)
        except:
            return False
    
    async def shutdown(self):
        """Cleanup"""
        if self.client:
            await self.client.close()
        self.initialized = False
        logger.info("Anthropic provider shutdown")
