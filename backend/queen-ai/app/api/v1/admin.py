"""
Admin API Endpoints
For Kingdom admin portal
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.models import database as db
from app.bees.enhanced_security_bee import EnhancedSecurityBee
from app.bees.data_pipeline_bee import DataPipelineBee
from app.integrations.elastic_search import ElasticSearchIntegration
import structlog

# Try to import Google Cloud BigQuery (optional)
try:
    from google.cloud import bigquery
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    bigquery = None

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Initialize security bee
_security_bee = None

def get_security_bee():
    global _security_bee
    if not _security_bee:
        _security_bee = EnhancedSecurityBee()
    return _security_bee

# ==================== AUTH MIDDLEWARE ====================
# In production, use proper JWT authentication
def verify_admin(request: Request):
    """Verify admin credentials"""
    # TODO: Implement proper JWT auth
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    # For now, accept any bearer token (UNSAFE - fix in production)
    return True

# ==================== REQUEST MODELS ====================

class UpdateOTCPhaseRequest(BaseModel):
    phase: str  # 'private_sale', 'standard', or 'disabled'
    
class UpdateConfigRequest(BaseModel):
    otc_phase: Optional[str] = None
    otc_enabled: Optional[bool] = None
    tge_completed: Optional[bool] = None
    omk_price_usd: Optional[float] = None
    allow_property_investment: Optional[bool] = None
    allow_staking: Optional[bool] = None
    allow_governance: Optional[bool] = None
    # Staking controls
    staking_apr: Optional[float] = None
    staking_lock_days: Optional[int] = None
    staking_terms: Optional[str] = None
    # Social links (admin-editable)
    social_links: Optional[Dict[str, str]] = None

class SetOMKContractRequest(BaseModel):
    address: str
    chain: str = "ethereum"  # ethereum or solana

class SetOTCPriceRequest(BaseModel):
    price: float
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None

class ChatWithQueenRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = {}

class ExecuteBeeRequest(BaseModel):
    bee_name: str
    task_data: Dict[str, Any]

class CreateOTCRequestRequest(BaseModel):
    name: str
    email: str
    wallet: str
    allocation: str
    amount_usd: str
    price_per_token: float = 0.10
    payment_token: Optional[str] = 'USDT'
    tx_hash: Optional[str] = None

class UpdateTreasuryWalletsRequest(BaseModel):
    wallets: Dict[str, str]  # {"usdt": "0x...", "usdc": "0x...", "dai": "0x...", "eth": "0x..."}

class UpdatePaymentMethodsRequest(BaseModel):
    payment_methods: Dict[str, bool]  # {"usdt": true, "usdc": true, "dai": false, "eth": false}

class UpdateTGEDateRequest(BaseModel):
    tge_date: str  # ISO format date string

class PropertyPayload(BaseModel):
    data: Dict[str, Any]

class VerifyPaymentRequest(BaseModel):
    request_id: str
    tx_hash: str
    payment_token: str

class PrivateInvestorRequest(BaseModel):
    wallet: str
    allocation: int
    amount_paid: float
    investor_id: str

class UserActionRequest(BaseModel):
    reason: Optional[str] = None

# ==================== CONFIG ENDPOINTS ====================

@router.get("/config")
async def get_system_config(admin: bool = Depends(verify_admin)):
    """Get current system configuration"""
    config = db.get_system_config()
    return {
        "success": True,
        "config": config
    }

@router.put("/config")
async def update_system_config(
    data: UpdateConfigRequest,
    admin: bool = Depends(verify_admin)
):
    """Update system configuration"""
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    config = db.update_system_config(update_data)
    
    return {
        "success": True,
        "message": "Configuration updated",
        "config": config
    }

@router.post("/config/otc-phase")
async def set_otc_phase(
    data: UpdateOTCPhaseRequest,
    admin: bool = Depends(verify_admin)
):
    """Set OTC phase (private_sale, standard, or disabled)"""
    config = db.update_system_config({'otc_phase': data.phase})
    
    return {
        "success": True,
        "message": f"OTC phase set to {data.phase}",
        "otc_phase": config['otc_phase']
    }

@router.post("/config/treasury-wallets")
async def update_treasury_wallets(
    data: UpdateTreasuryWalletsRequest,
    admin: bool = Depends(verify_admin)
):
    """Update treasury wallet addresses for OTC payments"""
    # Validate wallet addresses (basic check)
    for token, address in data.wallets.items():
        if address and not address.startswith('0x'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid wallet address for {token}: {address}"
            )
        if address and len(address) != 42:  # Ethereum address length
            raise HTTPException(
                status_code=400,
                detail=f"Invalid wallet address length for {token}"
            )
    
    config = db.update_system_config({'treasury_wallets': data.wallets})
    
    logger.info(
        "Treasury wallets updated",
        wallets={k: v[:10] + '...' for k, v in data.wallets.items() if v}
    )
    
    return {
        "success": True,
        "message": "Treasury wallets updated successfully",
        "treasury_wallets": config['treasury_wallets']
    }

@router.post("/config/payment-methods")
async def update_payment_methods(
    data: UpdatePaymentMethodsRequest,
    admin: bool = Depends(verify_admin)
):
    """Enable/disable payment methods"""
    config = db.update_system_config({'payment_methods_enabled': data.payment_methods})
    
    enabled_methods = [k.upper() for k, v in data.payment_methods.items() if v]
    logger.info(
        "Payment methods updated",
        enabled=enabled_methods
    )
    
    return {
        "success": True,
        "message": "Payment methods updated successfully",
        "payment_methods_enabled": config['payment_methods_enabled']
    }

@router.post("/config/tge-date")
async def update_tge_date(
    data: UpdateTGEDateRequest,
    admin: bool = Depends(verify_admin)
):
    """Set TGE (Token Generation Event) date"""
    from datetime import datetime
    
    # Validate date format
    try:
        datetime.fromisoformat(data.tge_date.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use ISO format (e.g., 2025-12-31T00:00:00Z)"
        )
    
    config = db.update_system_config({'tge_date': data.tge_date})
    
    logger.info("TGE date updated", tge_date=data.tge_date)
    
    return {
        "success": True,
        "message": "TGE date updated successfully",
        "tge_date": config['tge_date']
    }

# ==================== PROPERTIES MANAGEMENT ====================

@router.get("/properties")
async def admin_list_properties(admin: bool = Depends(verify_admin)):
    props = db.list_properties()
    return { "success": True, "properties": props, "total": len(props) }

@router.post("/properties")
async def admin_create_property(payload: PropertyPayload, admin: bool = Depends(verify_admin)):
    created = db.upsert_property(payload.data)
    return { "success": True, "property": created }

@router.put("/properties/{prop_id}")
async def admin_update_property(prop_id: str, payload: PropertyPayload, admin: bool = Depends(verify_admin)):
    updated = db.upsert_property({ **payload.data, 'id': prop_id })
    return { "success": True, "property": updated }

@router.delete("/properties/{prop_id}")
async def admin_delete_property(prop_id: str, admin: bool = Depends(verify_admin)):
    ok = db.delete_property(prop_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Property not found")
    return { "success": True, "deleted": prop_id }

@router.get("/config/otc-flow")
async def get_active_otc_flow_endpoint(admin: bool = Depends(verify_admin)):
    """Get which OTC flow is currently active"""
    flow = db.get_active_otc_flow()
    config = db.get_system_config()
    
    return {
        "success": True,
        "active_flow": flow,
        "otc_phase": config['otc_phase'],
        "otc_enabled": config['otc_enabled'],
        "tge_completed": config['tge_completed']
    }

# ==================== QUEEN AI CONTROL ====================

@router.post("/queen/chat")
async def chat_with_queen(
    request: Request,
    data: ChatWithQueenRequest,
    admin: bool = Depends(verify_admin)
):
    """
    🛡️ SECURED: Direct chat with Queen AI (admin access)
    
    Security Gates:
    1. Input validation and sanitization
    2. Prompt injection detection
    3. Output filtering
    """
    queen = request.app.state.queen
    
    # Get admin ID from auth header
    admin_token = request.headers.get("Authorization", "").replace("Bearer ", "")
    admin_id = admin_token[:10]  # Use first 10 chars as ID
    
    # === SECURITY GATE 1-3: Input Validation ===
    security_bee = get_security_bee()
    
    security_check = await security_bee.execute({
        "type": "validate_llm_input",
        "input": data.message,
        "user_id": admin_id,
        "endpoint": "admin_chat",
        "critical": False,  # Admin chat, less critical than dev chat
        "generates_code": False
    })
    
    # Check decision
    decision = security_check.get("decision")
    risk_score = security_check.get("risk_score", 0)
    
    if decision == "BLOCK":
        logger.warning(
            "Admin chat input BLOCKED",
            admin_id=admin_id,
            risk_score=risk_score
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Your message was blocked by security",
                "reasoning": security_check.get("reasoning"),
                "risk_score": risk_score
            }
        )
    
    elif decision == "QUARANTINE":
        logger.warning(
            "Admin chat input QUARANTINED",
            admin_id=admin_id,
            risk_score=risk_score
        )
        return {
            "success": False,
            "error": "Message under security review",
            "quarantined": True
        }
    
    # ALLOW - Proceed with sanitized input
    sanitized_message = security_check.get("sanitized_input")
    
    # Execute with admin context (using sanitized input)
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "generate_response",
        "user_input": sanitized_message,
        "context": {**data.context, "admin": True}
    })
    
    # === SECURITY GATE 4: Output Filtering ===
    output_check = await security_bee.execute({
        "type": "filter_llm_output",
        "output": result.get("message", ""),
        "mask_pii": False  # Don't mask for admin
    })
    
    filtered_response = output_check.get("filtered_output")
    
    return {
        "success": True,
        "response": filtered_response,
        "full_result": result,
        "security": {
            "risk_score": risk_score,
            "decision": decision
        }
    }

@router.get("/queen/status")
async def get_queen_status(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Get Queen AI status"""
    queen = request.app.state.queen
    
    return {
        "success": True,
        "queen_id": queen.queen_id,
        "active_bees": await queen.get_active_bees(),
        "status": "operational"
    }

@router.get("/queen/bees")
async def list_all_bees(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """List all registered bees"""
    queen = request.app.state.queen
    bees = await queen.bee_manager.list_bees()
    
    return {
        "success": True,
        "bees": bees,
        "total": len(bees)
    }

@router.post("/queen/bee/execute")
async def execute_bee_task(
    request: Request,
    data: ExecuteBeeRequest,
    admin: bool = Depends(verify_admin)
):
    """Execute a specific bee task"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee(
        data.bee_name,
        data.task_data
    )
    
    return {
        "success": True,
        "bee": data.bee_name,
        "result": result
    }

# ==================== ANALYTICS ====================

@router.get("/analytics/overview")
async def get_analytics_overview(admin: bool = Depends(verify_admin)):
    """Get high-level analytics"""
    try:
        analytics = db.get_analytics()
        
        return {
            "success": True,
            "analytics": {
                "total_users": analytics.get('total_users', 0),
                "active_users_24h": analytics.get('active_users_24h', 0),
                "total_omk_distributed": analytics.get('total_omk_distributed', 0),
                "total_revenue_usd": analytics.get('total_revenue_usd', 0),
                "pending_otc_requests": analytics.get('pending_otc_requests', 0),
                "properties_tokenized": 0
            }
        }
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        # Return empty data if DB fails
        return {
            "success": True,
            "analytics": {
                "total_users": 0,
                "active_users_24h": 0,
                "total_omk_distributed": 0,
                "total_revenue_usd": 0,
                "pending_otc_requests": 0,
                "properties_tokenized": 0
            }
        }

@router.get("/analytics/users")
async def get_user_analytics(admin: bool = Depends(verify_admin)):
    """Get detailed user analytics"""
    users = db.get_all_users()
    now = datetime.now()
    
    # Calculate time-based stats
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)
    
    new_users_today = len([u for u in users if datetime.fromisoformat(u['created_at']) >= today_start])
    new_users_week = len([u for u in users if datetime.fromisoformat(u['created_at']) >= week_start])
    new_users_month = len([u for u in users if datetime.fromisoformat(u['created_at']) >= month_start])
    
    return {
        "success": True,
        "data": {
            "new_users_today": new_users_today,
            "new_users_week": new_users_week,
            "new_users_month": new_users_month,
            "total_users": len(users),
            "user_retention": {},
            "user_growth": []
        }
    }

@router.get("/analytics/transactions")
async def get_transaction_analytics(admin: bool = Depends(verify_admin)):
    """Get transaction analytics"""
    analytics = db.get_analytics()
    transactions = analytics.get('transactions', [])
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    
    txs_today = [tx for tx in transactions if datetime.fromisoformat(tx['timestamp']) >= today_start]
    txs_week = [tx for tx in transactions if datetime.fromisoformat(tx['timestamp']) >= week_start]
    
    volume_today = sum(float(tx.get('amount_usd', 0)) for tx in txs_today)
    volume_week = sum(float(tx.get('amount_usd', 0)) for tx in txs_week)
    
    avg_size = volume_week / len(txs_week) if txs_week else 0
    
    return {
        "success": True,
        "data": {
            "transactions_today": len(txs_today),
            "transactions_week": len(txs_week),
            "volume_usd_today": volume_today,
            "volume_usd_week": volume_week,
            "avg_transaction_size": avg_size,
            "top_transactions": sorted(transactions, key=lambda x: float(x.get('amount_usd', 0)), reverse=True)[:10]
        }
    }

# ==================== OTC MANAGEMENT ====================

@router.get("/otc/requests")
async def list_otc_requests(
    status: Optional[str] = None,
    admin: bool = Depends(verify_admin)
):
    """List all OTC purchase requests"""
    requests = db.get_all_otc_requests(status=status)
    
    return {
        "success": True,
        "requests": requests,
        "total": len(requests),
        "filtered_by_status": status
    }

@router.post("/otc/requests")
async def create_otc_request(
    data: CreateOTCRequestRequest,
    admin: bool = Depends(verify_admin)
):
    """Create new OTC request (can also be called from user API)"""
    request = db.create_otc_request(data.dict())
    
    # Log for analytics
    db.log_transaction({
        'type': 'otc_request',
        'request_id': request['id'],
        'amount_usd': data.amount_usd
    })
    
    return {
        "success": True,
        "message": "OTC request created",
        "request": request
    }

@router.post("/otc/requests/{request_id}/approve")
async def approve_otc_request_endpoint(
    request_id: str,
    admin: bool = Depends(verify_admin)
):
    """Approve an OTC request"""
    request = db.approve_otc_request(request_id, approved_by="admin")
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Log transaction
    db.log_transaction({
        'type': 'otc_approved',
        'request_id': request_id,
        'amount_usd': request.get('amount_usd', 0),
        'allocation': request.get('allocation', 0)
    })
    
    # TODO: Send approval email to user
    
    return {
        "success": True,
        "message": f"OTC request {request_id} approved",
        "request": request
    }

@router.post("/otc/requests/{request_id}/reject")
async def reject_otc_request_endpoint(
    request_id: str,
    reason: str,
    admin: bool = Depends(verify_admin)
):
    """Reject an OTC request"""
    request = db.reject_otc_request(request_id, reason=reason, rejected_by="admin")
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # TODO: Send rejection email to user
    
    return {
        "success": True,
        "message": f"OTC request {request_id} rejected",
        "request": request,
        "reason": reason
    }

@router.get("/otc/requests/{request_id}")
async def get_otc_request(
    request_id: str,
    admin: bool = Depends(verify_admin)
):
    """Get specific OTC request details"""
    request = db.get_otc_request_by_id(request_id)
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return {
        "success": True,
        "request": request
    }

# ==================== HIVE INTELLIGENCE ====================

@router.get("/hive/message-bus/stats")
async def get_message_bus_stats(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Get message bus communication statistics"""
    queen = request.app.state.queen
    stats = queen.message_bus.get_communication_stats()
    
    return {
        "success": True,
        "stats": stats
    }

@router.get("/hive/message-bus/history")
async def get_message_history(
    request: Request,
    sender: Optional[str] = None,
    recipient: Optional[str] = None,
    message_type: Optional[str] = None,
    limit: int = 100,
    admin: bool = Depends(verify_admin)
):
    """Get message history between bees"""
    queen = request.app.state.queen
    history = queen.message_bus.get_message_history(
        sender=sender,
        recipient=recipient,
        message_type=message_type,
        limit=limit
    )
    
    return {
        "success": True,
        "messages": history,
        "total": len(history)
    }

@router.get("/hive/message-bus/health")
async def get_message_bus_health(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Get message bus health status"""
    queen = request.app.state.queen
    health = await queen.message_bus.health_check()
    
    return {
        "success": True,
        "health": health
    }

@router.get("/hive/board/posts")
async def get_hive_board_posts(
    request: Request,
    category: Optional[str] = None,
    author: Optional[str] = None,
    tags: Optional[str] = None,  # Comma-separated
    limit: int = 50,
    admin: bool = Depends(verify_admin)
):
    """Get posts from hive information board"""
    queen = request.app.state.queen
    
    # Parse tags if provided
    tag_list = tags.split(',') if tags else None
    
    posts = await queen.hive_board.query(
        category=category,
        author=author,
        tags=tag_list,
        limit=limit
    )
    
    return {
        "success": True,
        "posts": posts,
        "total": len(posts)
    }

@router.get("/hive/board/stats")
async def get_hive_board_stats(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Get hive board statistics"""
    queen = request.app.state.queen
    stats = await queen.hive_board.get_stats()
    
    return {
        "success": True,
        "stats": stats
    }

@router.get("/hive/board/search")
async def search_hive_board(
    request: Request,
    query: str,
    limit: int = 20,
    admin: bool = Depends(verify_admin)
):
    """Search hive board posts"""
    queen = request.app.state.queen
    results = await queen.hive_board.search(query=query, limit=limit)
    
    return {
        "success": True,
        "results": results,
        "total": len(results)
    }

@router.get("/hive/bees/performance")
async def get_bee_performance(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Get performance metrics for all bees"""
    queen = request.app.state.queen
    
    performance = {}
    for bee_name, bee in queen.bee_manager.bees.items():
        performance[bee_name] = {
            "task_count": bee.task_count,
            "success_count": bee.success_count,
            "error_count": bee.error_count,
            "success_rate": (bee.success_count / bee.task_count * 100) if bee.task_count > 0 else 0,
            "last_task_time": bee.last_task_time.isoformat() if bee.last_task_time else None,
            "status": bee.status,
            "llm_enabled": bee.llm_enabled
        }
    
    return {
        "success": True,
        "performance": performance
    }

@router.get("/hive/activity/live")
async def get_live_activity(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Get currently active bee tasks"""
    queen = request.app.state.queen
    
    from datetime import datetime, timedelta
    
    active_tasks = []
    now = datetime.utcnow()
    
    for bee_name, bee in queen.bee_manager.bees.items():
        if bee.last_task_time:
            # Check if task is recent (within last 10 seconds)
            time_diff = (now - bee.last_task_time).total_seconds()
            if time_diff < 10:
                active_tasks.append({
                    "bee_name": bee_name,
                    "status": bee.status,
                    "last_active": bee.last_task_time.isoformat(),
                    "seconds_ago": int(time_diff)
                })
    
    return {
        "success": True,
        "active_tasks": active_tasks,
        "count": len(active_tasks)
    }

@router.get("/hive/overview")
async def get_hive_overview(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Get complete hive intelligence overview"""
    try:
        queen = request.app.state.queen
    except AttributeError:
        # Queen not initialized - return empty data
        logger.warning("Queen not initialized, returning empty hive data")
        return {
            "success": True,
            "overview": {
                "bees": {"total": 0, "healthy": 0, "currently_active": 0},
                "message_bus": {"total_messages": 0, "delivery_rate": 0.0, "active_bees": 0},
                "hive_board": {"total_posts": 0, "active_categories": 0, "total_subscribers": 0},
                "queen": {
                    "status": "not_initialized",
                    "initialized": False,
                    "running": False,
                    "decision_count": 0
                }
            }
        }
    
    # Message bus stats
    message_stats = queen.message_bus.get_communication_stats()
    
    # Hive board stats
    board_stats = await queen.hive_board.get_stats()
    
    # Bee health
    bee_health = await queen.bee_manager.check_all_health()
    
    # Active tasks
    from datetime import datetime
    now = datetime.utcnow()
    active_count = 0
    for bee in queen.bee_manager.bees.values():
        if bee.last_task_time and (now - bee.last_task_time).total_seconds() < 10:
            active_count += 1
    
    return {
        "success": True,
        "overview": {
            "message_bus": {
                "total_messages": message_stats["total_messages"],
                "delivery_rate": message_stats["delivery_rate"],
                "active_bees": message_stats["active_bees"]
            },
            "hive_board": {
                "total_posts": board_stats["total_posts"],
                "active_categories": board_stats["active_categories"],
                "total_subscribers": board_stats["total_subscribers"]
            },
            "bees": {
                "total": len(queen.bee_manager.bees),
                "healthy": len([b for b in bee_health["bees"].values() if b["status"] == "active"]),
                "currently_active": active_count
            },
            "queen": {
                "initialized": queen.initialized,
                "running": queen.running,
                "decision_count": queen.decision_count
            }
        }
    }

# ==================== USER MANAGEMENT ====================

@router.get("/users")
async def list_users(admin: bool = Depends(verify_admin)):
    """List all users in the system"""
    users = db.get_all_users()
    
    return {
        "success": True,
        "users": users,
        "total": len(users)
    }

@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    admin: bool = Depends(verify_admin)
):
    """Get detailed user information"""
    user = db.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "user": user
    }

@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    admin: bool = Depends(verify_admin)
):
    """Activate a user account"""
    user = db.update_user(user_id, {"is_active": True})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User activated", user_id=user_id)
    
    return {
        "success": True,
        "message": "User activated",
        "user": user
    }

@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    data: UserActionRequest,
    admin: bool = Depends(verify_admin)
):
    """Deactivate a user account"""
    user = db.update_user(user_id, {"is_active": False})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User deactivated", user_id=user_id, reason=data.reason)
    
    return {
        "success": True,
        "message": "User deactivated",
        "user": user
    }

@router.post("/users/{user_id}/verify-email")
async def verify_user_email(
    user_id: int,
    admin: bool = Depends(verify_admin)
):
    """Manually verify a user's email"""
    from datetime import datetime
    
    user = db.update_user(user_id, {
        "is_verified": True,
        "email_verified_at": datetime.utcnow().isoformat()
    })
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info("User email verified", user_id=user_id)
    
    return {
        "success": True,
        "message": "Email verified",
        "user": user
    }

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    data: UserActionRequest,
    admin: bool = Depends(verify_admin)
):
    """Delete a user account (soft delete)"""
    # Check if user exists
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting admin users
    if user.get('role') == 'admin':
        raise HTTPException(status_code=403, detail="Cannot delete admin users")
    
    # Mark as deleted
    deleted_user = db.update_user(user_id, {
        "is_active": False,
        "is_verified": False
    })
    
    logger.warning("User deleted", user_id=user_id, reason=data.reason)
    
    return {
        "success": True,
        "message": "User deleted",
        "user_id": user_id
    }

# ==================== PRIVATE INVESTORS (PRE-TGE) ====================

@router.get("/private-investors")
async def list_private_investors(admin: bool = Depends(verify_admin)):
    """List all registered private investors"""
    investors = db.get_all_private_investors()
    
    return {
        "success": True,
        "investors": investors,
        "total": len(investors),
        "total_allocated": sum(inv.get('allocation', 0) for inv in investors)
    }

@router.post("/private-investors")
async def register_private_investor(
    data: PrivateInvestorRequest,
    admin: bool = Depends(verify_admin)
):
    """Register a new private investor"""
    # Calculate price per token
    price_per_token = data.amount_paid / data.allocation if data.allocation > 0 else 0
    
    investor_data = {
        "wallet": data.wallet,
        "allocation": data.allocation,
        "amount_paid": data.amount_paid,
        "price_per_token": price_per_token,
        "investor_id": data.investor_id,
        "distributed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    investor = db.create_private_investor(investor_data)
    
    logger.info(
        "Private investor registered",
        investor_id=data.investor_id,
        allocation=data.allocation,
        amount_paid=data.amount_paid
    )
    
    return {
        "success": True,
        "message": "Private investor registered",
        "investor": investor
    }

@router.post("/private-investors/tge")
async def execute_tge(admin: bool = Depends(verify_admin)):
    """Execute Token Generation Event (TGE)"""
    # Get all investors
    investors = db.get_all_private_investors()
    
    if not investors:
        raise HTTPException(status_code=400, detail="No investors registered")
    
    # Mark TGE as executed in system config
    config = db.update_system_config({
        "tge_completed": True,
        "tge_executed_at": datetime.utcnow().isoformat()
    })
    
    total_tokens = sum(inv.get('allocation', 0) for inv in investors)
    
    logger.info(
        "TGE executed",
        total_investors=len(investors),
        total_tokens=total_tokens
    )
    
    return {
        "success": True,
        "message": "TGE executed successfully",
        "tge_completed": True,
        "total_investors": len(investors),
        "total_tokens_allocated": total_tokens,
        "config": config
    }

@router.post("/private-investors/{investor_id}/distribute")
async def distribute_to_investor(
    investor_id: str,
    admin: bool = Depends(verify_admin)
):
    """Distribute tokens to a specific investor"""
    # Check if TGE is completed
    config = db.get_system_config()
    if not config.get('tge_completed'):
        raise HTTPException(status_code=400, detail="TGE not executed yet")
    
    # Get investor
    investor = db.get_private_investor(investor_id)
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    if investor.get('distributed'):
        raise HTTPException(status_code=400, detail="Tokens already distributed to this investor")
    
    # Mark as distributed
    updated = db.update_private_investor(investor_id, {
        "distributed": True,
        "distributed_at": datetime.utcnow().isoformat()
    })
    
    logger.info(
        "Tokens distributed",
        investor_id=investor_id,
        allocation=investor.get('allocation')
    )
    
    return {
        "success": True,
        "message": "Tokens distributed",
        "investor": updated
    }

@router.post("/private-investors/distribute-all")
async def distribute_to_all_investors(admin: bool = Depends(verify_admin)):
    """Distribute tokens to all pending investors"""
    # Check if TGE is completed
    config = db.get_system_config()
    if not config.get('tge_completed'):
        raise HTTPException(status_code=400, detail="TGE not executed yet")
    
    # Get all pending investors
    investors = db.get_all_private_investors()
    pending = [inv for inv in investors if not inv.get('distributed')]
    
    if not pending:
        return {
            "success": True,
            "message": "No pending distributions",
            "distributed_count": 0
        }
    
    # Mark all as distributed
    distributed_count = 0
    for investor in pending:
        db.update_private_investor(investor['investor_id'], {
            "distributed": True,
            "distributed_at": datetime.utcnow().isoformat()
        })
        distributed_count += 1
    
    total_tokens = sum(inv.get('allocation', 0) for inv in pending)
    
    logger.info(
        "Batch distribution completed",
        count=distributed_count,
        total_tokens=total_tokens
    )
    
    return {
        "success": True,
        "message": f"Distributed to {distributed_count} investors",
        "distributed_count": distributed_count,
        "total_tokens": total_tokens
    }

# ==================== CONTRACTS ====================

@router.get("/contracts/status")
async def get_contracts_status(admin: bool = Depends(verify_admin)):
    """Get status of all smart contracts"""
    return {
        "success": True,
        "contracts": {
            "omk_token": {
                "deployed": False,
                "address": None,
                "network": "sepolia"
            },
            "dispenser": {
                "deployed": False,
                "address": None,
                "network": "sepolia"
            },
            "private_sale": {
                "deployed": False,
                "address": None,
                "network": "sepolia"
            }
        }
    }

# ==================== SYSTEM HEALTH ====================

@router.get("/health")
async def admin_health_check(
    request: Request,
    admin: bool = Depends(verify_admin)
):
    """Comprehensive system health check"""
    queen = request.app.state.queen
    
    return {
        "success": True,
        "system": {
            "queen_ai": "operational",
            "database": "not_connected",  # TODO: Check DB
            "blockchain": "not_connected",  # TODO: Check node
            "email_service": "not_configured"  # TODO: Check email
        },
        "bees": {
            "total": len(await queen.bee_manager.list_bees()),
            "active": len(await queen.get_active_bees())
        },
        "config": get_config().dict()
    }


# ==================== MARKET DATA CONFIGURATION ====================

@router.post("/config/omk-contract")
async def set_omk_contract_address(
    data: SetOMKContractRequest,
    request: Request,
    authorized: bool = Depends(verify_admin)
):
    """
    Admin-only: Set OMK contract address
    
    When set, MarketDataAgent will switch to on-chain data mode
    """
    try:
        queen = request.app.state.queen
        agent = queen.market_data_agent
        await agent.set_omk_contract(data.contract_address)
        
        return {
            "success": True,
            "contract_address": data.contract_address,
            "message": "OMK contract address updated. Agent will now use on-chain data."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to set OMK contract", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/omk-otc-price")
async def set_omk_otc_price(
    data: SetOTCPriceRequest,
    request: Request,
    authorized: bool = Depends(verify_admin)
):
    """
    Admin-only: Set OMK OTC price
    
    This price takes precedence over calculated price from OTC requests
    """
    try:
        queen = request.app.state.queen
        agent = queen.market_data_agent
        
        # Validate price
        if data.price <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0")
        
        # Set OTC price
        agent.set_otc_price(data.price)
        
        logger.info("OMK OTC price set by admin", price=data.price)
        
        return {
            "success": True,
            "message": f"OMK OTC price set to ${data.price}",
            "price": data.price,
            "applies_to": "OTC mode only"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to set OTC price", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/config/omk-contract")
async def remove_omk_contract(
    request: Request,
    authorized: bool = Depends(verify_admin)
):
    """
    Admin-only: Remove OMK contract address
    
    Switches back to OTC data mode
    """
    try:
        queen = request.app.state.queen
        agent = queen.market_data_agent
        
        agent.set_omk_contract(None, "ethereum")
        
        logger.info("OMK contract address removed by admin")
        
        return {
            "success": True,
            "message": "OMK contract removed, switched to OTC mode",
            "data_source": "otc"
        }
        
    except Exception as e:
        logger.error("Failed to remove OMK contract", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/market")
async def get_market_config(
    request: Request,
    authorized: bool = Depends(verify_admin)
):
    """
    Admin-only: Get market data configuration
    """
    try:
        queen = request.app.state.queen
        agent = queen.market_data_agent
        
        config = agent.get_config()
        
        return {
            "success": True,
            "config": config
        }
        
    except Exception as e:
        logger.error("Failed to get market config", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DATA PIPELINE (FIVETRAN HACKATHON) ====================

class SchedulePipelineRequest(BaseModel):
    interval_minutes: int

@router.get("/data-pipeline/status")
async def get_data_pipeline_status(admin: bool = Depends(verify_admin)):
    """Get data pipeline status"""
    try:
        bee = DataPipelineBee()
        result = await bee.execute({"type": "get_pipeline_status"})
        
        if result.get("success"):
            return {
                "success": True,
                "status": result.get("status", {})
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Failed to get status")
            }
    except Exception as e:
        logger.error(f"Failed to get pipeline status: {e}")
        return {
            "success": False,
            "error": str(e),
            "status": {
                "run_count": 0,
                "error_count": 0,
                "last_run": None,
                "last_success": None,
                "schedule_interval_minutes": 15,
                "gcs_bucket": "omk-hive-blockchain-data",
                "gcs_available": False
            }
        }

@router.post("/data-pipeline/run")
async def run_data_pipeline(admin: bool = Depends(verify_admin)):
    """Run the data pipeline now"""
    try:
        bee = DataPipelineBee()
        result = await bee.execute({"type": "run_pipeline"})
        return result
    except Exception as e:
        logger.error(f"Failed to run pipeline: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/data-pipeline/schedule")
async def schedule_data_pipeline(
    data: SchedulePipelineRequest,
    admin: bool = Depends(verify_admin)
):
    """Schedule pipeline runs"""
    try:
        bee = DataPipelineBee()
        result = await bee.execute({
            "type": "schedule_pipeline",
            "interval_minutes": data.interval_minutes
        })
        return result
    except Exception as e:
        logger.error(f"Failed to schedule pipeline: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ==================== ELASTIC SEARCH (ELASTIC HACKATHON) ====================

class ElasticSearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    size: int = 10

class ElasticRAGRequest(BaseModel):
    query: str
    context_size: int = 5

# Global Elastic instance
_elastic_client = None

async def get_elastic_client():
    """Get or initialize Elastic client"""
    global _elastic_client
    if _elastic_client is None:
        try:
            from app.config.settings import settings
            _elastic_client = ElasticSearchIntegration(
                cloud_id=getattr(settings, 'ELASTIC_CLOUD_ID', None),
                api_key=getattr(settings, 'ELASTIC_API_KEY', None)
            )
            await _elastic_client.initialize()
            logger.info("Elastic Search client initialized")
        except Exception as e:
            logger.warning(f"Elastic Search not available: {e}")
            _elastic_client = None
    return _elastic_client

@router.post("/elastic/search")
async def elastic_search(
    data: ElasticSearchRequest,
    admin: bool = Depends(verify_admin)
):
    """Hybrid search (vector + keyword) in Elasticsearch"""
    try:
        elastic = await get_elastic_client()
        if not elastic:
            return {
                "success": False,
                "error": "Elastic Search not configured",
                "results": []
            }
        
        results = await elastic.hybrid_search(
            query=data.query,
            filters=data.filters,
            size=data.size
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Elastic search failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "results": []
        }

@router.post("/elastic/rag")
async def elastic_rag_query(
    data: ElasticRAGRequest,
    admin: bool = Depends(verify_admin)
):
    """RAG (Retrieval Augmented Generation) query with Gemini"""
    try:
        elastic = await get_elastic_client()
        if not elastic:
            return {
                "answer": "Elastic Search is not configured. Please set ELASTIC_CLOUD_ID and ELASTIC_API_KEY in .env",
                "context": [],
                "sources": []
            }
        
        result = await elastic.rag_query(
            question=data.query,
            context_size=data.context_size
        )
        
        return result
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        return {
            "answer": f"Error: {str(e)}",
            "context": [],
            "sources": []
        }

@router.get("/elastic/recent")
async def get_recent_elastic_activities(admin: bool = Depends(verify_admin)):
    """Get recent bee activities from Elasticsearch"""
    try:
        elastic = await get_elastic_client()
        if not elastic:
            return {
                "success": False,
                "error": "Elastic Search not configured",
                "activities": []
            }
        
        # Get last 50 activities
        results = await elastic.hybrid_search(
            query="*",
            size=50
        )
        
        return {
            "success": True,
            "activities": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Failed to get recent activities: {e}")
        return {
            "success": False,
            "error": str(e),
            "activities": []
        }


# ==================== BIGQUERY ANALYTICS (FIVETRAN HACKATHON) ====================

class BigQueryRequest(BaseModel):
    query: str

@router.post("/bigquery/query")
async def execute_bigquery_query(
    data: BigQueryRequest,
    admin: bool = Depends(verify_admin)
):
    """Execute a BigQuery SQL query"""
    if not BIGQUERY_AVAILABLE:
        return {
            "success": False,
            "error": "BigQuery not available. Install: pip install google-cloud-bigquery",
            "result": {"columns": [], "rows": [], "row_count": 0}
        }
    
    try:
        from app.config.settings import settings
        
        # Initialize BigQuery client
        project_id = getattr(settings, 'GCP_PROJECT_ID', getattr(settings, 'BIGQUERY_PROJECT_ID', 'omk-hive-prod'))
        client = bigquery.Client(project=project_id)
        
        # Execute query
        query_job = client.query(data.query)
        results = query_job.result()
        
        # Convert to list format
        columns = [field.name for field in results.schema]
        rows = []
        for row in results:
            rows.append([row[col] for col in columns])
        
        return {
            "success": True,
            "result": {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows)
            }
        }
    except Exception as e:
        logger.error(f"BigQuery query failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": {
                "columns": [],
                "rows": [],
                "row_count": 0
            }
        }
