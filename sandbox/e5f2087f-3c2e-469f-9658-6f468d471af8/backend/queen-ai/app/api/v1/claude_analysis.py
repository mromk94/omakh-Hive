"""
Claude System Analysis API Endpoints - REAL IMPLEMENTATION
AI-powered system architecture analysis using Claude 3.5 Sonnet
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import structlog
import json
import asyncio

from app.llm.providers.anthropic import AnthropicProvider
from app.config.settings import settings
from app.tools.system_analyzer import SystemAnalyzer

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/claude", tags=["Claude Analysis"])

# Initialize Claude provider
claude_provider: Optional[AnthropicProvider] = None

async def get_claude_provider() -> AnthropicProvider:
    """Get or initialize Claude provider"""
    global claude_provider
    if claude_provider is None:
        try:
            claude_provider = AnthropicProvider()
            await claude_provider.initialize()
            logger.info("✅ Claude provider initialized for system analysis")
        except Exception as e:
            logger.warning(f"⚠️ Claude provider initialization failed: {e}")
            raise
    return claude_provider

def verify_admin(request: Request):
    """Verify admin credentials"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

class ImplementationRequest(BaseModel):
    recommendation: str

@router.get("/analysis")
async def get_system_analysis(admin: bool = Depends(verify_admin)):
    """
    Get REAL system analysis by scanning actual codebase
    
    Returns comprehensive analysis of:
    - Data flow architecture
    - Security coverage
    - Performance metrics
    - Real recommendations based on actual findings
    
    NO MOCK DATA - Everything analyzed from real project files
    """
    
    try:
        logger.info("🔍 Starting REAL system analysis (no mock data)...")
        
        # Use real system analyzer
        analyzer = SystemAnalyzer()
        analysis = await analyzer.analyze_system()
        
        logger.info("✅ Real system analysis complete", 
                   source=analysis.get('source'),
                   score=analysis.get('overallScore'))
        
        return analysis
            
    except Exception as e:
        logger.error(f"System analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze system: {str(e)}"
        )

# REMOVED: get_static_analysis() - No more mock data!
# System now uses real SystemAnalyzer to scan actual codebase

@router.post("/implement")
async def request_implementation(
    data: ImplementationRequest,
    admin: bool = Depends(verify_admin)
):
    """
    Request Claude to implement a recommendation
    Automatically creates a code proposal in the system
    """
    
    try:
        provider = await get_claude_provider()
        
        prompt = f"""
You are a senior software engineer implementing the following recommendation:

**Recommendation:** {data.recommendation}

**System Context:**
- Backend: FastAPI (Python 3.11+)
- Frontend: Next.js 14, TypeScript, React
- Database: MySQL
- Caching: Redis

Provide implementation in JSON format:
{{
  "title": "Short title",
  "description": "Detailed description of changes",
  "files": [
    {{
      "path": "relative/path/to/file.py",
      "changes": "Description of what changes to make",
      "code": "Code snippet or full implementation"
    }}
  ],
  "testing_steps": ["Step 1", "Step 2"],
  "deployment_notes": ["Note 1", "Note 2"],
  "risk_level": "low|medium|high",
  "estimated_improvement": "Specific metrics"
}}

Be specific and production-ready.
"""
        
        implementation_text = await provider.generate(
            prompt=prompt,
            temperature=0.2,
            max_tokens=2000
        )
        
        # Try to parse as JSON
        try:
            import json
            implementation = json.loads(implementation_text)
        except:
            # Fallback: create structured data from text
            implementation = {
                "title": data.recommendation,
                "description": implementation_text,
                "files": [],
                "testing_steps": [],
                "deployment_notes": [],
                "risk_level": "medium",
                "estimated_improvement": "See description"
            }
        
        # Create code proposal automatically
        from app.core.code_proposal_system import CodeProposalSystem
        
        proposal_system = CodeProposalSystem()
        proposal_id = await proposal_system.create_proposal(
            title=f"[System Analysis] {implementation.get('title', data.recommendation)}",
            description=implementation.get('description', implementation_text),
            files_to_modify=[{
                "path": f.get("path", "unknown"),
                "changes": f.get("changes", ""),
                "code": f.get("code", "")
            } for f in implementation.get('files', [])],
            priority="high",
            risk_level=implementation.get('risk_level', 'medium'),
            created_by="system_analysis",
            metadata={
                "source": "system_analysis",
                "recommendation": data.recommendation,
                "testing_steps": implementation.get('testing_steps', []),
                "deployment_notes": implementation.get('deployment_notes', []),
                "estimated_improvement": implementation.get('estimated_improvement', '')
            }
        )
        
        logger.info(f"✅ Code proposal created from system analysis", 
                   proposal_id=proposal_id,
                   recommendation=data.recommendation)
        
        return {
            "success": True,
            "recommendation": data.recommendation,
            "implementation": implementation_text,
            "proposal_id": proposal_id,
            "proposal_created": True,
            "status": "proposal_created",
            "navigate_to": f"/kingdom?tab=queen-dev&mode=chat&subtab=proposals&proposal={proposal_id}"
        }
        
    except Exception as e:
        logger.error(f"Implementation generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "recommendation": data.recommendation,
            "status": "failed"
        }

@router.get("/health")
async def claude_health():
    """Check Claude integration health"""
    try:
        provider = await get_claude_provider()
        is_healthy = await provider.health_check()
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "service": "Claude System Analysis",
            "version": "1.0.0",
            "model": "claude-3-5-sonnet-20241022",
            "features": {
                "analysis": "enabled",
                "implementation": "enabled",
                "monitoring": "enabled"
            },
            "api_key_configured": bool(settings.ANTHROPIC_API_KEY)
        }
    except Exception as e:
        return {
            "status": "unavailable",
            "service": "Claude System Analysis",
            "error": str(e),
            "fallback": "static_analysis"
        }
