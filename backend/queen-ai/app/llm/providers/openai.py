"""
OpenAI Provider - GPT-4 and GPT-3.5
"""
from typing import Optional
import structlog

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class OpenAIProvider:
    """
    OpenAI Provider (GPT-4, GPT-3.5-turbo)
    """
    
    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.initialized = False
        self.model_name = "gpt-4"  # Default to GPT-4
    
    async def initialize(self):
        """Initialize OpenAI provider"""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed. Run: pip install openai")
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not configured")
        
        try:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.initialized = True
            logger.info("OpenAI provider initialized", model=self.model_name)
            
        except Exception as e:
            logger.error("Failed to initialize OpenAI", error=str(e))
            raise
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate completion from OpenAI"""
        if not self.initialized:
            raise RuntimeError("OpenAI provider not initialized")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            text = response.choices[0].message.content
            
            logger.debug("OpenAI generation complete",
                        input_length=len(prompt),
                        output_length=len(text))
            
            return text
            
        except Exception as e:
            logger.error("OpenAI generation failed", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check if OpenAI is available"""
        if not self.initialized:
            return False
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Say OK"}],
                temperature=0.1,
                max_tokens=10,
            )
            return bool(response.choices[0].message.content)
        except:
            return False
    
    async def shutdown(self):
        """Cleanup"""
        if self.client:
            await self.client.close()
        self.initialized = False
        logger.info("OpenAI provider shutdown")
