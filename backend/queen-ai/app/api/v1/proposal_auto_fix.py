"""
Auto-Fix API Endpoint
Triggers autonomous fixing of failed proposals
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import structlog

from app.api.v1.admin import verify_admin
from app.core.code_proposal_system import CodeProposalSystem, ProposalStatus
from app.core.proposal_auto_fixer import ProposalAutoFixer
from app.llm.providers.anthropic import AnthropicProvider
from app.config.settings import settings

logger = structlog.get_logger(__name__)

router = APIRouter()

# Initialize systems
proposal_system = None
auto_fixer = None
claude_provider = None


def get_proposal_system():
    global proposal_system
    if not proposal_system:
        proposal_system = CodeProposalSystem()
    return proposal_system


def get_auto_fixer():
    global auto_fixer
    if not auto_fixer:
        auto_fixer = ProposalAutoFixer(max_attempts=5)  # Increased for better success
    return auto_fixer


async def get_claude_provider():
    global claude_provider
    if not claude_provider:
        if not settings.ANTHROPIC_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Claude API key not configured. Set ANTHROPIC_API_KEY in .env"
            )
        claude_provider = AnthropicProvider()
        await claude_provider.initialize()
    return claude_provider


class AutoFixRequest(BaseModel):
    proposal_id: str
    max_attempts: Optional[int] = 3


@router.post("/auto-fix/{proposal_id}")
async def auto_fix_proposal(
    proposal_id: str,
    admin: bool = Depends(verify_admin)
):
    """
    🤖 Autonomous Fix - Analyze failure and automatically fix the proposal
    
    Flow:
    1. Analyze test failure logs
    2. Understand what went wrong
    3. Ask Claude to generate a fix
    4. Apply fix and re-test
    5. Repeat until success or max attempts
    """
    try:
        logger.info("🔧 Starting autonomous fix", proposal_id=proposal_id)
        
        # Get systems
        proposal_sys = get_proposal_system()
        fixer = get_auto_fixer()
        claude = await get_claude_provider()
        
        # Get proposal
        proposal = proposal_sys.proposals.get(proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Check if it actually failed
        if proposal["status"] != ProposalStatus.TESTS_FAILED.value:
            return {
                "success": False,
                "error": "Proposal has not failed tests. Current status: " + proposal["status"]
            }
        
        # Get test results
        test_results = proposal.get("test_results")
        if not test_results:
            raise HTTPException(status_code=400, detail="No test results found")
        
        # Run auto-fix
        fix_result = await fixer.auto_fix_proposal(
            proposal=proposal,
            test_results=test_results,
            claude_provider=claude
        )
        
        if not fix_result["success"]:
            return {
                "success": False,
                "error": "Failed to generate fix",
                "attempts": fix_result.get("attempts", 0)
            }
        
        # Apply the fix (update proposal with new code)
        if fix_result["fix_history"]:
            latest_fix = fix_result["fix_history"][-1]
            
            # Update proposal with fixed code
            proposal["auto_fix_history"] = fix_result["fix_history"]
            proposal["auto_fix_applied"] = True
            proposal["auto_fix_attempts"] = fix_result["attempts"]
            
            # Update files with fixed code
            for change in latest_fix["fix"].get("changes", []):
                for file_mod in proposal.get("files_to_modify", []):
                    if file_mod["path"] == change["file"]:
                        file_mod["code"] = change["code"]
                        file_mod["auto_fixed"] = True
            
            # Reset status to allow re-testing
            proposal["status"] = ProposalStatus.PROPOSED.value
            proposal["needs_auto_fix"] = False
            
            proposal_sys._save_proposal(proposal)
            
            logger.info("✅ Auto-fix applied", 
                       proposal_id=proposal_id,
                       attempts=fix_result["attempts"])
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "fix_applied": True,
                "attempts": fix_result["attempts"],
                "explanation": latest_fix["fix"].get("explanation"),
                "next_step": "Deploy to sandbox and test again",
                "fix_history": fix_result["fix_history"]
            }
        
        return {
            "success": False,
            "error": "No fix generated",
            "fix_result": fix_result
        }
        
    except Exception as e:
        logger.error(f"❌ Auto-fix failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auto-fix/status/{proposal_id}")
async def get_auto_fix_status(
    proposal_id: str,
    admin: bool = Depends(verify_admin)
):
    """
    Get auto-fix status for a proposal
    """
    proposal_sys = get_proposal_system()
    proposal = proposal_sys.proposals.get(proposal_id)
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    return {
        "proposal_id": proposal_id,
        "needs_auto_fix": proposal.get("needs_auto_fix", False),
        "auto_fix_applied": proposal.get("auto_fix_applied", False),
        "auto_fix_attempts": proposal.get("auto_fix_attempts", 0),
        "auto_fix_history": proposal.get("auto_fix_history", [])
    }
