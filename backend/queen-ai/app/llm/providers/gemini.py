"""
Gemini Provider - Google's Gemini 1.5 via Vertex AI
"""
from typing import Optional
import structlog

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from app.config.settings import settings

logger = structlog.get_logger(__name__)


class GeminiProvider:
    """
    Google Gemini 1.5 Provider
    
    Uses Gemini Flash by default (fast & cost-effective)
    Can switch to Gemini Pro for complex reasoning
    """
    
    def __init__(self):
        self.model = None
        self.initialized = False
        self.model_name = "gemini-1.5-flash"  # Default to Flash
    
    async def initialize(self):
        """Initialize Gemini provider"""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed. Run: pip install google-generativeai")
        
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not configured")
        
        try:
            # Configure API key
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            # Initialize model
            self.model = genai.GenerativeModel(self.model_name)
            
            self.initialized = True
            logger.info("Gemini provider initialized", model=self.model_name)
            
        except Exception as e:
            logger.error("Failed to initialize Gemini", error=str(e))
            raise
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """Generate completion from Gemini"""
        if not self.initialized:
            raise RuntimeError("Gemini provider not initialized")
        
        try:
            # Generate content
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            # Extract text
            text = response.text
            
            logger.debug("Gemini generation complete",
                        input_length=len(prompt),
                        output_length=len(text))
            
            return text
            
        except Exception as e:
            logger.error("Gemini generation failed", error=str(e))
            raise
    
    async def health_check(self) -> bool:
        """Check if Gemini is available"""
        if not self.initialized:
            return False
        
        try:
            # Simple test generation
            response = self.model.generate_content(
                "Say 'OK' if you're working",
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=10,
                )
            )
            return bool(response.text)
        except:
            return False
    
    async def shutdown(self):
        """Cleanup"""
        self.initialized = False
        logger.info("Gemini provider shutdown")
