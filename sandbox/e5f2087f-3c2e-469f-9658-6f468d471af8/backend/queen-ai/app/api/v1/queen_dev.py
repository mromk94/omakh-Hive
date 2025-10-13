"""
Queen Development API
Admin endpoints for Queen's autonomous development capabilities
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.code_proposal_system import CodeProposalSystem, ProposalStatus
from app.core.queen_system_manager import QueenSystemManager
from app.core.enhanced_claude_integration import ThinkingClaude, QueenRegulator
from app.core.enhanced_sandbox_system import SandboxEnvironment
from app.core.system_reboot_manager import SystemRebootManager
from app.integrations.claude_integration import ClaudeQueenIntegration
from app.api.v1.admin import verify_admin
from app.bees.enhanced_security_bee import EnhancedSecurityBee
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()

# Initialize systems
proposal_system = None
system_manager = None
queen_sessions = {}  # Store active Queen sessions by admin ID
reboot_manager = None
security_bee = None  # EnhancedSecurityBee for prompt protection

def get_proposal_system():
    global proposal_system
    if not proposal_system:
        proposal_system = CodeProposalSystem()
    return proposal_system

def get_system_manager():
    global system_manager
    if not system_manager:
        system_manager = QueenSystemManager()
    return system_manager

def get_reboot_manager():
    global reboot_manager
    if not reboot_manager:
        import os
        from pathlib import Path
        project_root = os.getenv("PROJECT_ROOT")
        if not project_root:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent
        reboot_manager = SystemRebootManager(Path(project_root))
    return reboot_manager

def get_security_bee():
    global security_bee
    if not security_bee:
        security_bee = EnhancedSecurityBee()
    return security_bee


# ==================== REQUEST MODELS ====================

class ChatMessage(BaseModel):
    message: str
    include_system_info: bool = True


class ApproveProposal(BaseModel):
    notes: Optional[str] = None


class RejectProposal(BaseModel):
    reason: str


# ==================== QUEEN CHAT ====================

@router.post("/chat")
async def chat_with_queen(
    data: ChatMessage,
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """
    🛡️ SECURED: Chat with Queen AI (Claude)
    Queen can analyze system and propose code changes
    
    Security Gates:
    1. Pre-processing - Remove invisible chars
    2. Threat Detection - Check for prompt injection
    3. Decision - ALLOW/BLOCK/QUARANTINE
    4. Output Filtering - Redact secrets from response
    """
    try:
        # Get admin info
        admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        admin_id = admin_token[:10]  # Use first 10 chars as ID
        
        # === SECURITY GATE 1-3: Input Validation ===
        security_bee = get_security_bee()
        
        security_check = await security_bee.execute({
            "type": "validate_llm_input",
            "input": data.message,
            "user_id": admin_id,
            "session_id": admin_token,
            "endpoint": "queen_dev_chat",
            "critical": True,  # CRITICAL: Generates code
            "generates_code": True  # CRITICAL: Lower threshold
        })
        
        # Check decision
        decision = security_check.get("decision")
        risk_score = security_check.get("risk_score", 0)
        
        if decision == "BLOCK":
            logger.warning(
                "🚫 Claude chat input BLOCKED",
                admin_id=admin_id,
                risk_score=risk_score,
                reasoning=security_check.get("reasoning")
            )
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Security: Input blocked by protection system",
                    "reasoning": security_check.get("reasoning"),
                    "risk_score": risk_score,
                    "matched_patterns": security_check.get("matched_patterns", [])[:3]
                }
            )
        
        elif decision == "QUARANTINE":
            logger.warning(
                "⚠️ Claude chat input QUARANTINED",
                admin_id=admin_id,
                risk_score=risk_score
            )
            return {
                "success": False,
                "error": "Your message is under security review",
                "reasoning": security_check.get("reasoning"),
                "risk_score": risk_score,
                "quarantined": True,
                "message": "This message has been flagged for potential security concerns and is being reviewed. If you believe this is an error, please contact support."
            }
        
        # ALLOW - Proceed with sanitized input
        sanitized_message = security_check.get("sanitized_input")
        
        logger.info(
            "✅ Claude chat input validated",
            admin_id=admin_id,
            risk_score=risk_score,
            decision=decision
        )
        
        # Get or create Queen session for this admin
        if admin_token not in queen_sessions:
            queen_sessions[admin_token] = ClaudeQueenIntegration()
        
        queen = queen_sessions[admin_token]
        
        # Chat with Queen using sanitized input
        response = await queen.chat(
            message=sanitized_message,
            include_system_info=data.include_system_info
        )
        
        # === SECURITY GATE 4: Output Filtering ===
        output_check = await security_bee.execute({
            "type": "filter_llm_output",
            "output": response.get("response", ""),
            "mask_pii": False,  # Don't mask for admin
            "validate_code": True  # Validate any code in response
        })
        
        filtered_response = output_check.get("filtered_output")
        output_warnings = output_check.get("warnings", [])
        
        if output_warnings:
            logger.warning(
                "Output filtered",
                admin_id=admin_id,
                warnings=output_warnings
            )
        
        # If Queen proposed code changes, validate and create proposal
        proposal_id = None
        if response.get("code_proposal"):
            # Validate code proposal for security
            code_validation = await security_bee.execute({
                "type": "validate_code_proposal",
                "code": str(response["code_proposal"]),
                "proposal_id": "pending"
            })
            
            if not code_validation.get("is_safe"):
                logger.error(
                    "🚨 CRITICAL: Malicious code detected in Claude proposal",
                    admin_id=admin_id,
                    warnings=code_validation.get("warnings")
                )
                return {
                    "success": False,
                    "error": "Security: Code proposal contains dangerous patterns",
                    "warnings": code_validation.get("warnings"),
                    "response": filtered_response,
                    "code_blocked": True
                }
            
            # Code is safe, create proposal
            proposal_system = get_proposal_system()
            result = proposal_system.create_proposal(
                proposal_data=response["code_proposal"],
                queen_session_id=admin_token
            )
            if result["success"]:
                proposal_id = result["proposal_id"]
                logger.info(
                    "Code proposal created",
                    proposal_id=proposal_id,
                    admin_id=admin_id
                )
        
        return {
            "success": True,
            "response": filtered_response,
            "code_proposal_created": proposal_id is not None,
            "proposal_id": proposal_id,
            "tokens_used": response.get("tokens_used"),
            "timestamp": response["timestamp"],
            "security": {
                "input_risk_score": risk_score,
                "output_filtered": len(output_warnings) > 0,
                "decision": decision
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-system")
async def analyze_system(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """
    Ask Queen to analyze the system and suggest improvements
    """
    try:
        admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        if admin_token not in queen_sessions:
            queen_sessions[admin_token] = ClaudeQueenIntegration()
        
        queen = queen_sessions[admin_token]
        
        response = await queen.analyze_system()
        
        # If Queen proposed changes, create proposals
        proposal_id = None
        if response.get("code_proposal"):
            proposal_system = get_proposal_system()
            result = proposal_system.create_proposal(
                proposal_data=response["code_proposal"],
                queen_session_id=admin_token
            )
            if result["success"]:
                proposal_id = result["proposal_id"]
        
        return {
            "success": True,
            "analysis": response["response"],
            "code_proposal_created": proposal_id is not None,
            "proposal_id": proposal_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation-history")
async def get_conversation_history(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Get conversation history with Queen"""
    admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if admin_token not in queen_sessions:
        return {"success": True, "history": []}
    
    queen = queen_sessions[admin_token]
    history = queen.get_conversation_history()
    
    return {
        "success": True,
        "history": history,
        "total": len(history)
    }


@router.delete("/clear-conversation")
async def clear_conversation(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Clear conversation history"""
    admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if admin_token in queen_sessions:
        queen_sessions[admin_token].clear_history()
    
    return {
        "success": True,
        "message": "Conversation history cleared"
    }


# ==================== CODE PROPOSALS ====================

@router.get("/proposals")
async def list_proposals(
    status: Optional[str] = None,
    admin: bool = Depends(verify_admin)
):
    """List all code proposals from Queen"""
    proposal_system = get_proposal_system()
    proposals = proposal_system.get_all_proposals(status=status)
    
    return {
        "success": True,
        "proposals": proposals,
        "total": len(proposals)
    }


@router.get("/proposals/{proposal_id}")
async def get_proposal_details(
    proposal_id: str,
    admin: bool = Depends(verify_admin)
):
    """Get detailed information about a specific proposal"""
    proposal_system = get_proposal_system()
    proposal = proposal_system.get_proposal(proposal_id)
    
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    return {
        "success": True,
        "proposal": proposal
    }


@router.post("/proposals/{proposal_id}/deploy-sandbox")
async def deploy_proposal_to_sandbox(
    proposal_id: str,
    admin: bool = Depends(verify_admin)
):
    """Deploy proposal to sandbox for testing"""
    proposal_system = get_proposal_system()
    result = await proposal_system.deploy_to_sandbox(proposal_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/proposals/{proposal_id}/run-tests")
async def run_proposal_tests(
    proposal_id: str,
    admin: bool = Depends(verify_admin)
):
    """Run automated tests on sandboxed proposal"""
    proposal_system = get_proposal_system()
    result = await proposal_system.run_tests(proposal_id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(
    proposal_id: str,
    data: ApproveProposal,
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Approve a proposal after review"""
    admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    proposal_system = get_proposal_system()
    result = proposal_system.approve_proposal(
        proposal_id=proposal_id,
        admin_id=admin_token,
        notes=data.notes
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(
    proposal_id: str,
    data: RejectProposal,
    admin: bool = Depends(verify_admin)
):
    """Reject a proposal"""
    admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    proposal_system = get_proposal_system()
    result = proposal_system.reject_proposal(
        proposal_id=proposal_id,
        admin_id=admin_token,
        reason=data.reason
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/proposals/{proposal_id}/apply")
async def apply_proposal_to_production(
    proposal_id: str,
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Apply approved proposal to production"""
    admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    proposal_system = get_proposal_system()
    result = await proposal_system.apply_to_production(
        proposal_id=proposal_id,
        admin_id=admin_token
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/proposals/{proposal_id}/rollback")
async def rollback_proposal(
    proposal_id: str,
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Rollback a proposal that was applied"""
    admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    proposal_system = get_proposal_system()
    result = proposal_system.rollback(
        proposal_id=proposal_id,
        admin_id=admin_token
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


# ==================== STATISTICS ====================

@router.get("/stats")
async def get_queen_dev_stats(admin: bool = Depends(verify_admin)):
    """Get statistics about Queen's development activity"""
    proposal_system = get_proposal_system()
    all_proposals = proposal_system.get_all_proposals()
    
    stats = {
        "total_proposals": len(all_proposals),
        "by_status": {},
        "by_priority": {},
        "approved_count": 0,
        "applied_count": 0,
        "rejected_count": 0,
        "tests_passed": 0,
        "tests_failed": 0
    }
    
    for proposal in all_proposals:
        # Count by status
        status = proposal["status"]
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        # Count by priority
        priority = proposal["priority"]
        stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
        
        # Count outcomes
        if status == ProposalStatus.APPROVED.value:
            stats["approved_count"] += 1
        elif status == ProposalStatus.APPLIED.value:
            stats["applied_count"] += 1
        elif status == ProposalStatus.REJECTED.value:
            stats["rejected_count"] += 1
        elif status == ProposalStatus.TESTS_PASSED.value:
            stats["tests_passed"] += 1
        elif status == ProposalStatus.TESTS_FAILED.value:
            stats["tests_failed"] += 1
    
    return {
        "success": True,
        "stats": stats
    }


# ==================== ENHANCED SYSTEM FEATURES ====================

@router.post("/system/index")
async def index_system(admin: bool = Depends(verify_admin)):
    """Index the entire system for Queen's knowledge"""
    manager = get_system_manager()
    index = manager.index_system()
    
    return {
        "success": True,
        "index": index
    }

@router.get("/system/context")
async def get_system_context(admin: bool = Depends(verify_admin)):
    """Get current system context for Queen"""
    manager = get_system_manager()
    context = manager.get_context_summary()
    
    return {
        "success": True,
        "context": context
    }

@router.post("/system/todos/add")
async def add_todo(
    task: str,
    priority: str = "medium",
    admin: bool = Depends(verify_admin)
):
    """Add task to Queen's TODO list"""
    manager = get_system_manager()
    manager.add_todo(task, priority)
    
    return {
        "success": True,
        "message": "Task added to Queen's TODO list"
    }

@router.get("/system/todos")
async def get_todos(admin: bool = Depends(verify_admin)):
    """Get Queen's TODO list"""
    manager = get_system_manager()
    
    return {
        "success": True,
        "todos": manager.queen_memory["todos"],
        "completed": manager.queen_memory["completed_tasks"]
    }

@router.post("/system/fetch-api")
async def safe_fetch_api(
    url: str,
    method: str = "GET",
    admin: bool = Depends(verify_admin)
):
    """Safely fetch from an approved API"""
    manager = get_system_manager()
    result = await manager.safe_fetch_api(url, method)
    
    return result

@router.get("/system/protected-files")
async def get_protected_files(admin: bool = Depends(verify_admin)):
    """Get list of protected files"""
    manager = get_system_manager()
    
    return {
        "success": True,
        "protected_files": list(manager.protected_files)
    }

@router.post("/system/can-modify")
async def check_can_modify_file(
    file_path: str,
    admin: bool = Depends(verify_admin)
):
    """Check if Queen can modify a file"""
    manager = get_system_manager()
    can_modify, reason = manager.can_modify_file(file_path)
    
    return {
        "success": True,
        "can_modify": can_modify,
        "reason": reason,
        "file_path": file_path
    }


# ==================== SYSTEM REBOOT ====================

@router.post("/system/reboot/request")
async def request_reboot(
    reason: str,
    component: str,  # "backend", "frontend", "full"
    admin: bool = Depends(verify_admin)
):
    """Request a system reboot"""
    manager = get_reboot_manager()
    result = manager.request_reboot(reason, component, "Admin")
    
    return result

@router.post("/system/reboot/execute/{reboot_id}")
async def execute_reboot(
    reboot_id: str,
    request: Request,
    force: bool = False,
    admin: bool = Depends(verify_admin)
):
    """Execute approved reboot"""
    admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    manager = get_reboot_manager()
    result = await manager.execute_reboot(reboot_id, admin_token, force)
    
    return result

@router.post("/system/reboot/cancel/{reboot_id}")
async def cancel_reboot(
    reboot_id: str,
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Cancel pending reboot"""
    admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    manager = get_reboot_manager()
    result = manager.cancel_reboot(reboot_id, admin_token)
    
    return result

@router.get("/system/reboot/history")
async def get_reboot_history(
    limit: int = 10,
    admin: bool = Depends(verify_admin)
):
    """Get reboot history"""
    manager = get_reboot_manager()
    history = manager.get_reboot_history(limit)
    
    return {
        "success": True,
        "history": history
    }
