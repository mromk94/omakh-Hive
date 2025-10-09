"""
Frontend API Endpoints - User-facing conversational interface
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List

router = APIRouter(prefix="/frontend", tags=["Frontend"])


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
    """Send message to AI and get contextual response"""
    queen = request.app.state.queen
    
    result = await queen.bee_manager.execute_bee("user_experience", {
        "type": "generate_response",
        "user_input": data.user_input,
        "context": data.context
    })
    
    return result

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
