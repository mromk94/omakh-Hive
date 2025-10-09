"""
UserExperienceBee - Frontend AI Interaction & Conversational UX

Responsibilities:
- Handle all conversational AI interactions with frontend
- Generate contextual responses based on user journey
- Provide multilingual greetings and support
- Guide users through onboarding flow
- Present information in chat-style format
- Manage conversation state and context
- Generate personalized recommendations
- Handle menu interactions conversationally
"""
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime
from app.bees.base import BaseBee

logger = structlog.get_logger(__name__)


class UserExperienceBee(BaseBee):
    """
    Conversational UX Bee - The Voice of the Hive
    
    Provides immersive, chat-based user experience:
    - Multilingual greetings
    - Contextual AI responses
    - Conversational onboarding
    - Information presentation as dialogue
    - Personalized user journeys
    """
    
    def __init__(self, bee_id: int = None):
        super().__init__(bee_id=bee_id, name="UserExperienceBee")
        
        # Conversation state tracking
        self.conversations: Dict[str, Dict[str, Any]] = {}
        
        # Multilingual greetings
        self.greetings = {
            "en": {"text": "Hello", "flag": "🇬🇧", "name": "English"},
            "es": {"text": "Hola", "flag": "🇪🇸", "name": "Spanish"},
            "zh": {"text": "你好", "flag": "🇨🇳", "name": "Chinese"},
            "ja": {"text": "こんにちは", "flag": "🇯🇵", "name": "Japanese"},
            "pcm": {"text": "How far", "flag": "🇳🇬", "name": "Nigerian Pidgin"},
            "fr": {"text": "Bonjour", "flag": "🇫🇷", "name": "French"},
            "ru": {"text": "Привет", "flag": "🇷🇺", "name": "Russian"},
            "ar": {"text": "مرحبا", "flag": "🇸🇦", "name": "Arabic"}
        }
        
        # Onboarding info snippets (chat-style)
        self.info_snippets = {
            "what_is_omk": {
                "icon": "💎",
                "title": "What is OMK?",
                "messages": [
                    "OMK is an AI-governed token ecosystem 🤖",
                    "Think of it as a smart, self-managing crypto investment 💰",
                    "Our Queen AI makes decisions 24/7 to grow your investment 📈"
                ]
            },
            "how_it_works": {
                "icon": "⚙️",
                "title": "How It Works",
                "messages": [
                    "You buy OMK tokens 💵",
                    "Our AI manages liquidity, staking, and yield farming 🔄",
                    "You earn passive returns automatically 💸",
                    "Watch your ROI grow in real-time! 📊"
                ]
            },
            "security": {
                "icon": "🛡️",
                "title": "Is It Safe?",
                "messages": [
                    "Absolutely! Here's why: ✅",
                    "✓ Audited smart contracts",
                    "✓ Multi-layer security protocols",
                    "✓ Transparent AI decision logging",
                    "✓ Emergency pause mechanisms"
                ]
            },
            "roi": {
                "icon": "📈",
                "title": "Expected Returns",
                "messages": [
                    "Our AI targets 8-15% APY 💰",
                    "This is dynamic based on market conditions 📊",
                    "Historical average: 12.3% APY 🎯",
                    "Plus bonus rewards from liquidity mining! 🎁"
                ]
            }
        }
        
        # Stats
        self.total_conversations = 0
        self.active_conversations = 0
    
    async def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute UX interaction"""
        task_type = task_data.get("type")
        
        # Greetings & Initial Flow
        if task_type == "get_greetings":
            return await self._get_greetings(task_data)
        elif task_type == "get_initial_welcome":
            return await self._get_initial_welcome(task_data)
        
        # Onboarding Flow
        elif task_type == "start_conversation":
            return await self._start_conversation(task_data)
        elif task_type == "get_theme_selection":
            return await self._get_theme_selection(task_data)
        elif task_type == "ask_has_account":
            return await self._ask_has_account(task_data)
        elif task_type == "get_user_type_options":
            return await self._get_user_type_options(task_data)
        elif task_type == "get_info_snippet":
            return await self._get_info_snippet(task_data)
        
        # Conversational Responses
        elif task_type == "generate_response":
            return await self._generate_contextual_response(task_data)
        elif task_type == "handle_menu_click":
            return await self._handle_menu_interaction(task_data)
        
        # User Journey
        elif task_type == "get_welcome_back":
            return await self._get_welcome_back_message(task_data)
        elif task_type == "get_dashboard_intro":
            return await self._get_dashboard_intro(task_data)
        
        # Help & Information
        elif task_type == "explain_feature":
            return await self._explain_feature(task_data)
        elif task_type == "get_quick_help":
            return await self._get_quick_help(task_data)
        
        else:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
    
    # ============ GREETINGS & WELCOME ============
    
    async def _get_greetings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get multilingual greetings for animated display"""
        return {
            "success": True,
            "greetings": self.greetings,
            "animation_config": {
                "duration_per_greeting": 3000,  # 3 seconds
                "transition": "fade-scale",
                "loop": True
            }
        }
    
    async def _get_initial_welcome(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get initial welcome message after language selection"""
        language = data.get("language", "en")
        
        messages = {
            "en": "Hi there 👋, welcome! Before we begin, how do you prefer your world to look?",
            "es": "¡Hola! 👋 ¡Bienvenido! Antes de comenzar, ¿cómo prefieres que se vea tu mundo?",
            "zh": "你好 👋，欢迎！在开始之前，你喜欢什么样的界面？",
            "ja": "こんにちは 👋、ようこそ！始める前に、どんな見た目が好きですか？",
            "pcm": "How far! 👋 Welcome o! Before we start, how you wan make your world look?",
            "fr": "Salut 👋, bienvenue! Avant de commencer, comment préférez-vous votre interface?",
            "ru": "Привет 👋, добро пожаловать! Прежде чем начать, как вы хотите видеть свой мир?",
            "ar": "مرحبا 👋، مرحبا بك! قبل أن نبدأ، كيف تفضل أن يبدو عالمك؟"
        }
        
        return {
            "success": True,
            "message": messages.get(language, messages["en"]),
            "show_theme_selection": True
        }
    
    # ============ CONVERSATION FLOW ============
    
    async def _start_conversation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new conversation"""
        session_id = data.get("session_id", self._generate_session_id())
        language = data.get("language", "en")
        theme = data.get("theme", "light")
        
        self.conversations[session_id] = {
            "session_id": session_id,
            "language": language,
            "theme": theme,
            "stage": "initial",
            "started_at": datetime.utcnow().isoformat(),
            "messages": []
        }
        
        self.total_conversations += 1
        self.active_conversations += 1
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Conversation started!"
        }
    
    async def _get_theme_selection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get theme selection prompt"""
        language = data.get("language", "en")
        
        return {
            "success": True,
            "message": "Awesome! Let's get you started properly.",
            "options": [
                {
                    "id": "light",
                    "label": "🌞 White Theme (Default)",
                    "description": "Clean, bright, and easy on the eyes"
                },
                {
                    "id": "dark",
                    "label": "🌚 Dark Theme",
                    "description": "Sleek, modern, and easy at night"
                }
            ]
        }
    
    async def _ask_has_account(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ask if user has an account"""
        return {
            "success": True,
            "message": "Great choice! ✨\n\nDo you already have an account with us?",
            "options": [
                {"id": "yes", "label": "🟢 Yes, I have an account", "action": "login"},
                {"id": "no", "label": "🔵 No, I'm new here", "action": "onboard"}
            ]
        }
    
    async def _get_user_type_options(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get user type selection for new users"""
        return {
            "success": True,
            "message": "Perfect! Let's get to know you quickly 👇\n\nWhat brings you here?",
            "options": [
                {
                    "id": "explorer",
                    "label": "🧭 Just exploring / Curious Investor",
                    "description": "Want to learn and maybe invest a small amount"
                },
                {
                    "id": "investor",
                    "label": "💼 Serious Investor",
                    "description": "Ready to invest and grow my portfolio"
                },
                {
                    "id": "institutional",
                    "label": "🏢 Institutional / Partner / Bulk Buyer",
                    "description": "Large investment or partnership interest"
                }
            ]
        }
    
    async def _get_info_snippet(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get information snippet for onboarding"""
        snippet_id = data.get("snippet_id")
        show_more = data.get("show_more", False)
        
        if snippet_id not in self.info_snippets:
            snippet_id = "what_is_omk"
        
        snippet = self.info_snippets[snippet_id]
        
        messages = snippet["messages"]
        if not show_more:
            messages = messages[:2]  # Show first 2 by default
        
        return {
            "success": True,
            "snippet": {
                "id": snippet_id,
                "icon": snippet["icon"],
                "title": snippet["title"],
                "messages": messages,
                "has_more": len(snippet["messages"]) > 2 and not show_more
            },
            "delay_between_messages": 2000  # 2 seconds
        }
    
    # ============ CONTEXTUAL RESPONSES ============
    
    async def _generate_contextual_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual AI response based on user input"""
        user_input = data.get("user_input", "").lower()
        context = data.get("context", {})
        
        # Simple keyword-based responses (in production, use LLM)
        if "help" in user_input or "stuck" in user_input:
            return await self._get_quick_help(data)
        
        elif "price" in user_input or "cost" in user_input:
            return {
                "success": True,
                "message": "Great question! 💰\n\nOMK token current price: **$0.12**\nMinimum investment: **$10 (83 OMK)**\n\nWant to see our pricing tiers?",
                "show_options": True,
                "options": [
                    {"id": "yes", "label": "Yes, show me pricing"},
                    {"id": "no", "label": "No thanks, continue"}
                ]
            }
        
        elif "roi" in user_input or "return" in user_input:
            return await self._get_info_snippet({"snippet_id": "roi"})
        
        elif "safe" in user_input or "security" in user_input:
            return await self._get_info_snippet({"snippet_id": "security"})
        
        elif "how" in user_input and "work" in user_input:
            return await self._get_info_snippet({"snippet_id": "how_it_works"})
        
        else:
            return {
                "success": True,
                "message": f"Interesting! Let me help you with that... 🤔\n\nCould you tell me more about what you'd like to know?",
                "suggestions": [
                    "What is OMK?",
                    "How does it work?",
                    "Is it safe?",
                    "Expected returns?"
                ]
            }
    
    async def _handle_menu_interaction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle sidebar menu clicks conversationally"""
        menu_item = data.get("menu_item")
        
        responses = {
            "about": {
                "message": "Sure! Here's a quick story about us 👇",
                "content": [
                    {
                        "type": "text",
                        "text": "🏰 **OMK Hive** was born from a simple idea:"
                    },
                    {
                        "type": "text",
                        "text": "What if AI could manage crypto investments better than humans? 🤖"
                    },
                    {
                        "type": "text",
                        "text": "So we built **Queen AI** - an autonomous system that:"
                    },
                    {
                        "type": "list",
                        "items": [
                            "Manages liquidity 24/7 💧",
                            "Optimizes yield farming 🌾",
                            "Adjusts staking rewards 💎",
                            "Monitors security constantly 🛡️"
                        ]
                    },
                    {
                        "type": "text",
                        "text": "All while you sit back and watch your investment grow! 📈✨"
                    }
                ]
            },
            "whitepaper": {
                "message": "Here's the link and highlights 📄",
                "content": [
                    {
                        "type": "text",
                        "text": "📑 **OMK Hive Whitepaper**"
                    },
                    {
                        "type": "link",
                        "text": "Download Full Whitepaper (PDF)",
                        "url": "/whitepaper.pdf"
                    },
                    {
                        "type": "text",
                        "text": "**Quick Highlights:**"
                    },
                    {
                        "type": "list",
                        "items": [
                            "🤖 AI-Governed Tokenomics",
                            "🔗 Multi-Chain Support (ETH + Solana)",
                            "💰 8-15% Target APY",
                            "🏦 $400M Treasury Allocation",
                            "🛡️ Multi-Layer Security"
                        ]
                    }
                ]
            },
            "contact": {
                "message": "I'd love to help you get in touch! 📬",
                "content": [
                    {
                        "type": "text",
                        "text": "📧 **Email:** support@omkhive.com"
                    },
                    {
                        "type": "text",
                        "text": "🐦 **Twitter:** @OMKHive"
                    },
                    {
                        "type": "text",
                        "text": "💬 **Discord:** discord.gg/omkhive"
                    },
                    {
                        "type": "text",
                        "text": "📱 **Telegram:** t.me/omkhive"
                    },
                    {
                        "type": "text",
                        "text": "\nOr ask me anything right here! I'm always listening 👂"
                    }
                ]
            },
            "explore": {
                "message": "Let's explore together! 🗺️ What interests you?",
                "options": [
                    {"id": "tokenomics", "label": "💎 Tokenomics", "icon": "💎"},
                    {"id": "ai_system", "label": "🤖 Queen AI System", "icon": "🤖"},
                    {"id": "staking", "label": "💰 Staking & Rewards", "icon": "💰"},
                    {"id": "roadmap", "label": "🗺️ Roadmap", "icon": "🗺️"}
                ]
            }
        }
        
        response = responses.get(menu_item, {
            "message": "Let me help you with that! 😊",
            "content": []
        })
        
        return {
            "success": True,
            **response
        }
    
    # ============ USER JOURNEY ============
    
    async def _get_welcome_back_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get welcome back message for returning users"""
        user_name = data.get("user_name", "User")
        last_login = data.get("last_login")
        
        return {
            "success": True,
            "message": f"Welcome back, {user_name}! 👋✨\n\nLoading your dashboard...",
            "loading_messages": [
                "Fetching your wallet balance 💰",
                "Calculating your ROI 📈",
                "Checking recent activities 📊",
                "Preparing your personalized insights 🤖"
            ]
        }
    
    async def _get_dashboard_intro(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get dashboard introduction for first-time dashboard view"""
        user_name = data.get("user_name", "")
        
        return {
            "success": True,
            "message": f"Here's your dashboard, {user_name}! 🎉",
            "tour_steps": [
                {
                    "target": "wallet-bubble",
                    "message": "💰 This shows your current balance and ROI in real-time"
                },
                {
                    "target": "ai-chat",
                    "message": "🤖 Ask me anything! I'm always here to help"
                },
                {
                    "target": "quick-actions",
                    "message": "⚡ Quick actions for buying, staking, or withdrawing"
                },
                {
                    "target": "activity-feed",
                    "message": "📊 See all your transaction history here"
                }
            ]
        }
    
    # ============ HELP & SUPPORT ============
    
    async def _explain_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Explain a specific feature"""
        feature = data.get("feature")
        
        explanations = {
            "staking": {
                "message": "Let me explain staking! 💎",
                "content": "Staking means locking your OMK tokens to earn rewards. Think of it like a high-yield savings account for crypto! You earn 8-15% APY automatically. 📈"
            },
            "liquidity": {
                "message": "Liquidity explained! 💧",
                "content": "Liquidity is how easily you can buy/sell OMK. Our AI manages liquidity pools to ensure you can always trade smoothly! 🔄"
            },
            "roi": {
                "message": "ROI = Return on Investment! 📊",
                "content": "It shows how much profit you've made. Green = you're winning! 🎉 Our AI works to maximize your ROI 24/7. 🤖"
            }
        }
        
        explanation = explanations.get(feature, {
            "message": "Good question! Let me help 🤔",
            "content": "I'm still learning about this feature. Could you ask in a different way?"
        })
        
        return {
            "success": True,
            **explanation
        }
    
    async def _get_quick_help(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get quick help menu"""
        return {
            "success": True,
            "message": "I'm here to help! What do you need? 🤗",
            "options": [
                {"id": "how_to_buy", "label": "💰 How to buy OMK?"},
                {"id": "how_to_stake", "label": "💎 How to stake?"},
                {"id": "check_balance", "label": "💵 Check my balance"},
                {"id": "withdraw", "label": "🏦 How to withdraw?"},
                {"id": "security", "label": "🛡️ Is my money safe?"},
                {"id": "support", "label": "📞 Talk to human support"}
            ]
        }
    
    # ============ HELPERS ============
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        import secrets
        return f"session_{secrets.token_hex(8)}"
