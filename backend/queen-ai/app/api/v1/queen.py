"""
Queen AI API Endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


# ============ REQUEST MODELS ============

class RegisterBeeRequest(BaseModel):
    bee_type: int
    name: str
    endpoint: str
    metadata: str = ""


class BridgeProposalRequest(BaseModel):
    proposal_type: int
    target_address: str = ""
    new_value: int = 0
    description: str


class TreasuryProposalRequest(BaseModel):
    category: int
    amount: int
    recipient: str
    description: str


# ============ ENDPOINTS ============

@router.get("/status")
async def get_queen_status(request: Request):
    """Get Queen AI operational status"""
    queen = request.app.state.queen
    
    return {
        "initialized": queen.initialized,
        "running": queen.running,
        "decision_count": queen.decision_count,
        "proposal_count": queen.proposal_count,
        "active_bees": len([b for b in queen.bees.values() if b.get("status") == 1]),
        "total_bees": len(queen.bees),
    }


@router.get("/health")
async def get_system_health(request: Request):
    """Get comprehensive system health"""
    queen = request.app.state.queen
    return await queen.get_system_health()


@router.get("/metrics")
async def get_system_metrics(request: Request):
    """Get current system metrics from blockchain"""
    queen = request.app.state.queen
    
    return {
        "metrics": queen.system_metrics,
        "last_update": queen.last_metrics_update.isoformat() if queen.last_metrics_update else None,
    }


@router.get("/bees")
async def list_bees(request: Request):
    """List all registered bees"""
    queen = request.app.state.queen
    return {"bees": await queen.get_active_bees()}


@router.post("/bees/register")
async def register_bee(request: Request, bee_request: RegisterBeeRequest):
    """Register a new bee agent on-chain"""
    queen = request.app.state.queen
    
    result = await queen.register_bee(
        bee_type=bee_request.bee_type,
        name=bee_request.name,
        endpoint=bee_request.endpoint,
        metadata=bee_request.metadata,
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/proposals/bridge")
async def submit_bridge_proposal(request: Request, proposal: BridgeProposalRequest):
    """Submit a proposal to OMKBridge contract"""
    queen = request.app.state.queen
    
    result = await queen.propose_bridge_change(
        proposal_type=proposal.proposal_type,
        target_address=proposal.target_address,
        new_value=proposal.new_value,
        description=proposal.description,
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/proposals/treasury")
async def submit_treasury_proposal(request: Request, proposal: TreasuryProposalRequest):
    """Submit a treasury spending proposal"""
    queen = request.app.state.queen
    
    result = await queen.propose_treasury_spending(
        category=proposal.category,
        amount=proposal.amount,
        recipient=proposal.recipient,
        description=proposal.description,
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/process")
async def process_request(request: Request, data: Dict[str, Any]):
    """Process a general request"""
    queen = request.app.state.queen
    
    request_type = data.get("type")
    request_data = data.get("data", {})
    
    if not request_type:
        raise HTTPException(status_code=400, detail="Missing 'type' field")
    
    result = await queen.process_request(request_type, request_data)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


# ============ LLM ENDPOINTS ============

class LLMGenerateRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1000
    provider: str = None
    use_memory: bool = True


@router.post("/llm/generate")
async def llm_generate(request: Request, llm_request: LLMGenerateRequest):
    """Generate text using LLM"""
    queen = request.app.state.queen
    
    try:
        response = await queen.llm.generate(
            prompt=llm_request.prompt,
            temperature=llm_request.temperature,
            max_tokens=llm_request.max_tokens,
            provider=llm_request.provider,
            use_memory=llm_request.use_memory,
        )
        
        return {
            "response": response,
            "provider": llm_request.provider or queen.llm.current_provider,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/llm/providers")
async def get_llm_providers(request: Request):
    """Get available LLM providers"""
    queen = request.app.state.queen
    
    return {
        "current": queen.llm.current_provider,
        "available": queen.llm.get_available_providers(),
        "costs": queen.llm.get_costs(),
    }


@router.post("/llm/switch")
async def switch_llm_provider(request: Request, data: Dict[str, Any]):
    """Switch LLM provider"""
    queen = request.app.state.queen
    
    provider = data.get("provider")
    if not provider:
        raise HTTPException(status_code=400, detail="Missing 'provider' field")
    
    try:
        await queen.llm.switch_provider(provider)
        return {"success": True, "current_provider": queen.llm.current_provider}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
