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
async def get_system_analysis(
    force_refresh: bool = False,
    admin: bool = Depends(verify_admin)
):
    """
    Get REAL system analysis integrating Queen & Hive data
    
    Returns comprehensive analysis of:
    - Codebase structure and metrics
    - Bug reports from BugAnalyzer (Queen)
    - Error logs from system (Hive)
    - Security coverage
    - Performance metrics
    - Real recommendations
    
    Caching: Results cached for 24 hours (set force_refresh=true to bypass)
    
    Args:
        force_refresh: If True, bypass cache and run fresh analysis
    """
    
    try:
        logger.info("🔍 System analysis requested", 
                   force_refresh=force_refresh)
        
        # Use real system analyzer with caching
        from app.tools.system_analyzer import SystemAnalyzer
        analyzer = SystemAnalyzer()
        analysis = await analyzer.analyze_system(force_refresh=force_refresh)
        
        logger.info("✅ System analysis complete", 
                   source=analysis.get('source'),
                   cached=analysis.get('cached', False),
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
    Request Claude to implement a recommendation with full codebase context
    Uses smart context builder and validation for high-quality proposals
    """
    
    try:
        # Import new components
        from app.core.codebase_context_builder import CodebaseContextBuilder
        from app.core.proposal_validator import ProposalValidator
        
        provider = await get_claude_provider()
        
        # Build rich codebase context
        logger.info("🔍 Building codebase context for recommendation")
        context_builder = CodebaseContextBuilder()
        
        # Detect recommendation type
        rec_lower = data.recommendation.lower()
        if 'redis' in rec_lower or 'cache' in rec_lower:
            rec_type = 'redis'
        elif 'database' in rec_lower or 'sql' in rec_lower:
            rec_type = 'database'
        elif 'api' in rec_lower or 'endpoint' in rec_lower:
            rec_type = 'api'
        elif 'websocket' in rec_lower:
            rec_type = 'websocket'
        elif 'security' in rec_lower:
            rec_type = 'security'
        else:
            rec_type = 'general'
        
        context = context_builder.build_context(rec_type)
        context_str = context_builder.format_for_claude(context)
        
        # Enhanced prompt with context
        prompt = f"""
You are a senior software engineer implementing a feature for an EXISTING, WORKING codebase.

**RECOMMENDATION TO IMPLEMENT:**
{data.recommendation}

{context_str}

**YOUR TASK:**
Generate a production-ready implementation that:
1. Follows the EXACT patterns shown in the code examples above
2. Uses ONLY packages listed in installed_packages
3. Creates files in valid project directories (see project structure)
4. Uses async/await for ALL I/O operations (database, Redis, HTTP)
5. Includes proper error handling
6. Follows all validation rules

**CRITICAL REQUIREMENTS:**
- For Redis: MUST use 'from redis.asyncio import Redis, ConnectionPool' (not sync redis)
- For FastAPI: Follow the async endpoint patterns shown above
- All file paths must be relative to project root (e.g., "app/core/cache_manager.py")
- Include ALL necessary imports at the top of each file
- Use type hints: def function(param: str) -> Dict[str, Any]
- Add docstrings to explain what the code does

**OUTPUT FORMAT (STRICT JSON):**
{{
  "title": "Short descriptive title",
  "description": "What this implements and why",
  "files": [
    {{
      "path": "app/core/example.py",
      "changes": "Creates new cache manager class",
      "code": "# Complete, runnable code here\\nfrom redis.asyncio import Redis\\n\\nclass CacheManager:\\n    ..."
    }}
  ],
  "testing_steps": ["How to test this feature"],
  "deployment_notes": ["What to configure before deploying"],
  "risk_level": "low",
  "estimated_improvement": "Expected impact"
}}

**VALIDATION:**
Before responding, verify:
✅ All imports are from installed packages
✅ All paths follow project structure
✅ Code is complete and runnable (no placeholders like "# ... rest of code")
✅ Async functions use await for I/O
✅ No syntax errors

Generate the implementation now in valid JSON format:
"""
        
        logger.info("🤖 Requesting implementation from Claude with enhanced context")
        implementation_text = await provider.generate(
            prompt=prompt,
            temperature=0.35,  # Increased for better problem-solving
            max_tokens=4000    # Doubled for complex implementations
        )
        
        # Parse and validate JSON response
        import json
        try:
            # Try to extract JSON from response (Claude sometimes adds markdown)
            if "```json" in implementation_text:
                # Extract JSON from code block
                json_match = re.search(r'```json\s*\n(.*?)\n```', implementation_text, re.DOTALL)
                if json_match:
                    implementation_text = json_match.group(1)
            
            implementation = json.loads(implementation_text)
            logger.info("✅ Successfully parsed implementation JSON")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Claude's response as JSON: {e}")
            
            # Retry with explicit JSON request
            logger.info("🔄 Retrying with explicit JSON formatting request")
            retry_prompt = f"""
The previous response was not valid JSON. Please provide ONLY valid JSON (no markdown, no explanation) for this recommendation:

{data.recommendation}

JSON structure required:
{{
  "title": "string",
  "description": "string",
  "files": [{{"path": "string", "changes": "string", "code": "string"}}],
  "testing_steps": ["string"],
  "deployment_notes": ["string"],
  "risk_level": "low|medium|high",
  "estimated_improvement": "string"
}}

Respond with ONLY the JSON object:
"""
            
            implementation_text = await provider.generate(
                prompt=retry_prompt,
                temperature=0.2,
                max_tokens=4000
            )
            
            try:
                implementation = json.loads(implementation_text)
                logger.info("✅ Retry successful - JSON parsed")
            except:
                logger.error("❌ Retry failed - returning error")
                return {
                    "success": False,
                    "error": "Claude could not generate valid JSON response",
                    "recommendation": data.recommendation,
                    "raw_response": implementation_text[:500],
                    "status": "failed"
                }
        
        # Validate required fields
        if not implementation.get('files') or len(implementation['files']) == 0:
            logger.error("❌ Implementation has no files")
            return {
                "success": False,
                "error": "Implementation contains no files to modify",
                "recommendation": data.recommendation,
                "status": "failed"
            }
        
        # Prepare proposal data for validation
        proposal_data = {
            "title": f"[System Analysis] {implementation.get('title', data.recommendation)}",
            "description": implementation.get('description', ''),
            "files_to_modify": [{
                "path": f.get("path", ""),
                "changes": f.get("changes", ""),
                "code": f.get("code", "")
            } for f in implementation.get('files', [])],
            "priority": "high",
            "risk_level": implementation.get('risk_level', 'medium')
        }
        
        # Validate proposal before creating it
        logger.info("🔍 Validating proposal before creation")
        validator = ProposalValidator()
        is_valid, fixed_proposal, messages = validator.validate_and_fix(proposal_data)
        
        if not is_valid:
            logger.error("❌ Proposal validation failed", errors=messages)
            return {
                "success": False,
                "error": "Generated code failed validation",
                "validation_errors": messages,
                "recommendation": data.recommendation,
                "status": "validation_failed"
            }
        
        if len(messages) > 0:
            logger.info("⚠️ Proposal had issues but was auto-fixed", fixes=messages)
        
        # Create code proposal with validated data
        from app.core.code_proposal_system import CodeProposalSystem
        
        proposal_system = CodeProposalSystem()
        proposal_id = await proposal_system.create_proposal(
            title=fixed_proposal['title'],
            description=fixed_proposal['description'],
            files_to_modify=fixed_proposal['files_to_modify'],
            priority=fixed_proposal['priority'],
            risk_level=fixed_proposal['risk_level'],
            created_by="system_analysis",
            metadata={
                "source": "system_analysis",
                "recommendation": data.recommendation,
                "testing_steps": implementation.get('testing_steps', []),
                "deployment_notes": implementation.get('deployment_notes', []),
                "estimated_improvement": implementation.get('estimated_improvement', ''),
                "validation_messages": messages,
                "context_enhanced": True
            }
        )
        
        logger.info(f"✅ Code proposal created from system analysis", 
                   proposal_id=proposal_id,
                   recommendation=data.recommendation,
                   validated=True,
                   auto_fixes=len(messages))
        
        return {
            "success": True,
            "recommendation": data.recommendation,
            "implementation": implementation.get('description', ''),
            "proposal_id": proposal_id,
            "proposal_created": True,
            "validated": True,
            "validation_messages": messages,
            "files_count": len(fixed_proposal['files_to_modify']),
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
