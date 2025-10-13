"""
Frontend API Endpoints - User-facing conversational interface
"""
from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, EmailStr
import app.models.database as db
from app.bees.enhanced_security_bee import EnhancedSecurityBee
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/frontend", tags=["Frontend"])

# Initialize security bee
_security_bee = None

def get_security_bee():
    global _security_bee
    if not _security_bee:
        _security_bee = EnhancedSecurityBee()
    return _security_bee

# ============ REQUEST MODELS ============

class LanguageSelectionRequest(BaseModel):
    language: str

class ThemeSelectionRequest(BaseModel):
    theme: str
    language: Optional[str] = "en"

class EmailCheckRequest(BaseModel):
    email: EmailStr

class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = ""
    user_type: str = "explorer"  # explorer, investor, institutional
    language: str = "en"
    theme: str = "light"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SessionRequest(BaseModel):
    session_token: str

class ConversationRequest(BaseModel):
    user_input: str
    session_token: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    chat_history: Optional[List[Dict[str, Any]]] = []  # Full conversation history
    wallet_address: Optional[str] = None  # User's wallet for context

class MenuInteractionRequest(BaseModel):
    menu_item: str
    session_token: Optional[str] = None


# ============ GREETING & INITIAL FLOW ============

@router.get("/greetings")
async def get_greetings(request: Request):
    """Get multilingual greetings for animated display"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "get_greetings"
    })
    
    return result

@router.post("/welcome")
async def get_welcome_message(data: LanguageSelectionRequest, request: Request):
    """Get initial welcome message after language selection"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "get_initial_welcome",
        "language": data.language
    })
    
    return result

@router.post("/theme-selection")
async def get_theme_selection(data: LanguageSelectionRequest, request: Request):
    """Get theme selection prompt"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "get_theme_selection",
        "language": data.language
    })
    
    return result

@router.post("/ask-account")
async def ask_has_account(data: ThemeSelectionRequest, request: Request):
    """Ask if user has an account"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "ask_has_account",
        "theme": data.theme,
        "language": data.language
    })
    
    return result


# ============ AUTHENTICATION ============

@router.post("/check-email")
async def check_email(data: EmailCheckRequest, request: Request):
    """Check if email exists in system"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("onboarding", {
        "type": "check_email",
        "email": data.email
    })
    
    return result

@router.post("/register")
async def register_user(data: UserRegistrationRequest, request: Request):
    """Register a new user"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("onboarding", {
        "type": "register_user",
        "email": data.email,
        "password": data.password,
        "full_name": data.full_name,
        "user_type": data.user_type,
        "language": data.language,
        "theme": data.theme
    })
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

@router.post("/login")
async def login_user(data: LoginRequest, request: Request):
    """Login existing user"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("onboarding", {
        "type": "login",
        "email": data.email,
        "password": data.password
    })
    
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error"))
    
    return result

@router.post("/logout")
async def logout_user(data: SessionRequest, request: Request):
    """Logout user"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("onboarding", {
        "type": "logout",
        "session_token": data.session_token
    })
    
    return result

@router.post("/verify-session")
async def verify_session(data: SessionRequest, request: Request):
    """Verify if session is valid"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("onboarding", {
        "type": "verify_session",
        "session_token": data.session_token
    })
    
    return result


# ============ ONBOARDING FLOW ============

@router.post("/user-type-options")
async def get_user_type_options(request: Request):
    """Get user type selection options"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "get_user_type_options"
    })
    
    return result

@router.get("/info-snippet/{snippet_id}")
async def get_info_snippet(snippet_id: str, show_more: bool = False, request: Request = None):
    """Get information snippet for onboarding"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "get_info_snippet",
        "snippet_id": snippet_id,
        "show_more": show_more
    })
    
    return result


# ============ CONVERSATIONAL AI ============

@router.post("/chat")
async def chat_with_ai(data: ConversationRequest, request: Request):
    """
    🛡️ SECURED: Context-Aware Chat Endpoint
    Queen AI analyzes message, understands intent, and provides intelligent routing
    
    Security Gates:
    1. Input validation and sanitization
    2. Prompt injection detection
    3. Output filtering
    """
    queen = request.app.state.queen
    
    # Get user ID from session or generate temp ID
    user_id = data.session_token if data.session_token else f"anon_{hash(str(request.client))}"
    
    # === SECURITY GATE 1-3: Input Validation ===
    security_bee = get_security_bee()
    
    security_check = await security_bee.execute({
        "type": "validate_llm_input",
        "input": data.user_input,
        "user_id": user_id,
        "endpoint": "frontend_chat",
        "critical": False,  # User conversation, not critical
        "generates_code": False
    })
    
    # Check decision
    decision = security_check.get("decision")
    risk_score = security_check.get("risk_score", 0)
    
    if decision == "BLOCK":
        logger.warning(
            "User conversation input BLOCKED",
            user_id=user_id,
            risk_score=risk_score
        )
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Your message was blocked by our security system",
                "message": "Please rephrase your question without special instructions or commands."
            }
        )
    
    elif decision == "QUARANTINE":
        logger.warning(
            "User conversation input QUARANTINED",
            user_id=user_id,
            risk_score=risk_score
        )
        return {
            "success": True,
            "message": "Your message is being reviewed for safety. Please try a different question or contact support if you need immediate assistance.",
            "quarantined": True
        }
    
    # ALLOW - Proceed with sanitized input
    sanitized_input = security_check.get("sanitized_input")
    
    # Import context analyzer
    from app.services.context_analyzer import ContextAnalyzer
    analyzer = ContextAnalyzer()
    
    # Analyze user message with full context (using sanitized input)
    analysis = analyzer.analyze_message(
        user_message=sanitized_input,
        chat_history=data.chat_history
    )
    
    # If system diagnostic requested
    if analysis['intent'] == 'system_diagnostic':
        diagnostic = analyzer.diagnose_system()
        return {
            "success": True,
            "message": "🔍 System Diagnostic Complete!",
            "analysis": analysis,
            "diagnostic": diagnostic,
            "type": "system_diagnostic"
        }
    
    # For chat, always use UserExperience bee for conversational response
    # Other bees handle specific technical tasks
    intent = analysis['intent']
    
    # Generate AI response based on intent
    if intent == 'buy_omk':
        # Check which OTC flow is active
        import app.models.database as db
        
        otc_flow = db.get_active_otc_flow()
        
        if otc_flow == "private_sale":
            return {
                "success": True,
                "message": "Great! We're currently in our Private Sale phase (Pre-TGE). 🎯\n\nYou can secure your OMK tokens at $0.10 each with a minimum investment of $10,000.",
                "options": [{"type": "otc_purchase"}],  # OTCPurchaseCard - manual approval
                "analysis": analysis,
                "recommended_actions": analysis['recommended_actions'],
                "confidence": analysis['confidence'],
                "otc_flow": "private_sale"
            }
        elif otc_flow == "standard_otc":
            return {
                "success": True,
                "message": "Great! Let's get you some OMK tokens! 🪙\n\nYou can instantly swap ETH, USDT, or USDC for OMK.",
                "options": [{"type": "omk_purchase"}],  # SwapCard - instant swap
                "analysis": analysis,
                "recommended_actions": analysis['recommended_actions'],
                "confidence": analysis['confidence'],
                "otc_flow": "standard"
            }
        else:
            return {
                "success": True,
                "message": "OMK token purchases are currently unavailable. Please check back soon!",
                "analysis": analysis,
                "confidence": analysis['confidence'],
                "otc_flow": "disabled"
            }
    elif intent == 'invest_property':
        return {
            "success": True,
            "message": "Excellent choice! Here are our available properties 🏢",
            "options": [{"type": "property_list"}],
            "analysis": analysis,
            "recommended_actions": analysis['recommended_actions'],
            "confidence": analysis['confidence']
        }
    elif intent == 'portfolio_view':
        return {
            "success": True,
            "message": "Here's your portfolio overview! 📊",
            "options": [{"type": "dashboard"}],
            "analysis": analysis,
            "recommended_actions": analysis['recommended_actions'],
            "confidence": analysis['confidence']
        }
    elif intent == 'swap_tokens':
        return {
            "success": True,
            "message": "Let's swap some tokens! What would you like to swap?",
            "options": [{"type": "token_swap"}],
            "analysis": analysis,
            "recommended_actions": analysis['recommended_actions'],
            "confidence": analysis['confidence']
        }
    elif intent == 'market_data':
        return {
            "success": True,
            "message": "Let me get you the latest market data! 📊\n\n(Market data integration coming soon)",
            "analysis": analysis,
            "recommended_actions": analysis['recommended_actions'],
            "confidence": analysis['confidence']
        }
    elif intent == 'help':
        return {
            "success": True,
            "message": "I'm here to help! What would you like to learn about? 👩‍🏫",
            "options": [
                {"label": "🔐 How to connect wallet", "action": "wallet_help"},
                {"label": "💰 How to buy OMK", "action": "buy_help"},
                {"label": "🏠 How to invest", "action": "invest_help"},
            ],
            "analysis": analysis,
            "recommended_actions": analysis['recommended_actions'],
            "confidence": analysis['confidence']
        }
    else:
        # General chat - use UX bee
        result = await queen.bee_manager.execute_bee("user_experience", {
            "type": "generate_response",
            "user_input": data.user_input,
            "context": data.context,
            "analysis": analysis,
            "chat_history": data.chat_history,
            "wallet_address": data.wallet_address
        })
        
        # Enhance result with recommendations
        if result.get("success"):
            result["analysis"] = analysis
            result["recommended_actions"] = analysis['recommended_actions']
            result["confidence"] = analysis['confidence']
        
        return result

@router.post("/otc-request")
async def submit_otc_request(data: Dict[str, Any], request: Request):
    """Submit OTC purchase request with payment information"""
    try:
        # Validate required fields
        required_fields = ['name', 'email', 'wallet', 'allocation', 'price_per_token']
        for field in required_fields:
            if field not in data:
                raise HTTPException(status_code=400, detail=f"Missing field: {field}")
        
        # Calculate total USD
        allocation = float(data['allocation'])
        price = float(data['price_per_token'])
        amount_usd = allocation * price
        
        # Check whale threshold (20M OMK = $2M at $0.10)
        whale_threshold = 20000000  # 20 million OMK
        requires_approval = allocation >= whale_threshold
        
        # Create OTC request with payment data
        request_data = {
            'name': data['name'],
            'email': data['email'],
            'wallet': data['wallet'],
            'allocation': str(allocation),
            'amount_usd': str(amount_usd),
            'price_per_token': price,
            'payment_token': data.get('payment_token', 'USDT'),
            'tx_hash': data.get('tx_hash'),
            'requires_approval': requires_approval,
            'status': 'payment_received' if data.get('tx_hash') else 'pending'
        }
        
        # Add payment info if provided
        if data.get('tx_hash'):
            request_data['payment'] = {
                'token': data.get('payment_token', 'USDT'),
                'tx_hash': data.get('tx_hash'),
                'verified': False,  # Will be verified by admin/automated process
                'received_at': db.datetime.now().isoformat()
            }
        
        otc_request = db.create_otc_request(request_data)
        
        # Log transaction
        db.log_transaction({
            'type': 'otc_request_submitted',
            'request_id': otc_request['id'],
            'amount_usd': amount_usd,
            'user_email': data['email'],
            'requires_approval': requires_approval,
            'has_payment': bool(data.get('tx_hash'))
        })
        
        logger.info(
            "OTC request submitted",
            request_id=otc_request['id'],
            allocation=allocation,
            amount_usd=amount_usd,
            requires_approval=requires_approval,
            has_tx_hash=bool(data.get('tx_hash'))
        )
        
        return {
            "success": True,
            "message": "OTC request submitted successfully",
            "request_id": otc_request['id'],
            "requires_approval": requires_approval,
            "request": otc_request
        }
    
    except Exception as e:
        logger.error("OTC request submission failed", error=str(e))
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/menu-interaction")
async def handle_menu_click(data: MenuInteractionRequest, request: Request):
    """Handle sidebar menu interactions conversationally"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "handle_menu_click",
        "menu_item": data.menu_item
    })
    
    return result

@router.post("/explain/{feature}")
async def explain_feature(feature: str, request: Request):
    """Get AI explanation of a feature"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "explain_feature",
        "feature": feature
    })
    
    return result

@router.get("/quick-help")
async def get_quick_help(request: Request):
    """Get quick help menu"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "get_quick_help"
    })
    
    return result


# ============ USER DASHBOARD ============

@router.post("/welcome-back")
async def get_welcome_back(data: SessionRequest, request: Request):
    """Get welcome back message for returning users"""
    queen = request.app.state.queen
    
    # Verify session first
    session_result = await queen.bee_manager.execute_bee("onboarding", {
        "type": "verify_session",
        "session_token": data.session_token
    })
    
    if not session_result.get("valid"):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user = session_result.get("user", {})
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "get_welcome_back",
        "user_name": user.get("full_name", "User"),
        "last_login": user.get("last_login")
    })
    
    return result

@router.post("/dashboard-intro")
async def get_dashboard_intro(data: SessionRequest, request: Request):
    """Get dashboard introduction for first-time view"""
    queen = request.app.state.queen
    
    # Verify session
    session_result = await queen.bee_manager.execute_bee("onboarding", {
        "type": "verify_session",
        "session_token": data.session_token
    })
    
    if not session_result.get("valid"):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user = session_result.get("user", {})
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "get_dashboard_intro",
        "user_name": user.get("full_name", "")
    })
    
    return result

@router.post("/wallet-balance")
async def get_wallet_balance(data: SessionRequest, request: Request):
    """Get user's wallet balance"""
    queen = request.app.state.queen
    
    # Verify session
    session_result = await queen.bee_manager.execute_bee("onboarding", {
        "type": "verify_session",
        "session_token": data.session_token
    })
    
    if not session_result.get("valid"):
        raise HTTPException(status_code=401, detail="Invalid session")
    
    user = session_result.get("user", {})
    
    result = await queen.bee_manager.execute_bee("onboarding", {
        "type": "get_wallet_balance",
        "email": user.get("email")
    })
    
    return result


# ============ HEALTH CHECK ============

@router.get("/health")
async def frontend_health():
    """Frontend API health check"""
    return {
        "status": "healthy",
        "service": "Frontend API",
        "bees": ["OnboardingBee", "UserExperienceBee"]
    }
