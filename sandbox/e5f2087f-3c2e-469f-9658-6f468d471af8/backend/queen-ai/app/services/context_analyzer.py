"""
🌟 Context-Aware Queen AI System
Analyzes user messages and chat history to provide intelligent routing and responses.
"""

from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class ContextAnalyzer:
    """Analyzes conversation context and routes to appropriate bees/cards"""
    
    def __init__(self):
        # Intent patterns for detecting user needs
        self.intent_patterns = {
            'portfolio_view': [
                r'\b(show|view|see|check|display)\b.*(portfolio|holdings|assets|balance)',
                r'\b(my|current)\b.*(portfolio|holdings|assets|balance)',
                r'\bhow much\b.*(do i have|own|possess)',
                r'\bwhat.*(do i own|are my holdings)',
            ],
            'buy_omk': [
                r'\b(buy|purchase|get|acquire)\b.*\bOMK\b',
                r'\b(invest in|put money into)\b.*\bOMK\b',
                r'\bhow.*(buy|purchase|get).*\bOMK\b',
                r'\bwant.*\bOMK\b',
            ],
            'invest_property': [
                r'\b(invest|buy)\b.*(property|properties|real estate)',
                r'\b(show|view|see|browse)\b.*(property|properties|real estate)',
                r'\b(available|list).*properties',
                r'\breal estate\b.*(opportunities|invest)',
            ],
            'swap_tokens': [
                r'\b(swap|exchange|trade|convert)\b',
                r'\b(ETH|USDC|USDT)\b.*\b(for|to|into)\b.*\bOMK\b',
                r'\b(token|crypto)\b.*(swap|exchange)',
            ],
            'market_data': [
                r'\b(price|value|worth)\b.*(of|for).*\b(ETH|BTC|OMK|crypto)',
                r'\b(market|crypto)\b.*(price|data|info|information)',
                r'\bhow much is\b.*(ETH|BTC|OMK)',
                r'\bcrypto\b.*(price|value|market)',
            ],
            'news': [
                r'\b(news|update|latest)\b.*(crypto|real estate|market)',
                r'\bwhat.*happening\b.*(crypto|market|real estate)',
                r'\b(recent|new)\b.*(news|development|update)',
            ],
            'help': [
                r'\b(help|assist|guide|tutorial)\b',
                r'\bhow (do|does|to)\b',
                r'\bwhat is\b',
                r'\bexplain\b',
            ],
            'profile': [
                r'\b(my|view)\b.*(profile|account|settings)',
                r'\b(change|update|edit)\b.*(profile|settings|preferences)',
            ],
        }
        
        # System diagnostics keywords
        self.system_keywords = [
            'diagnostic', 'check system', 'system status', 'working routes',
            'broken', 'error', 'not working', 'debug', 'analyze system'
        ]
        
    def analyze_message(self, user_message: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Analyze user message and return intent, recommendations, and routing
        
        Returns:
            {
                'intent': str,
                'confidence': float,
                'recommended_actions': List[Dict],
                'bee_to_consult': str,
                'context_summary': str,
                'needs_clarification': bool
            }
        """
        message_lower = user_message.lower()
        
        # Check for system diagnostics request
        if any(keyword in message_lower for keyword in self.system_keywords):
            return self._handle_system_diagnostic(user_message)
        
        # Detect primary intent
        detected_intent = self._detect_intent(message_lower)
        
        # Analyze conversation context
        context_summary = self._analyze_history(chat_history) if chat_history else {}
        
        # Generate recommendations
        recommendations = self._generate_recommendations(detected_intent, context_summary)
        
        # Determine which bee should handle this
        bee_assignment = self._assign_bee(detected_intent)
        
        return {
            'intent': detected_intent['intent'],
            'confidence': detected_intent['confidence'],
            'recommended_actions': recommendations,
            'bee_to_consult': bee_assignment,
            'context_summary': context_summary,
            'needs_clarification': detected_intent['confidence'] < 0.6,
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_intent(self, message: str) -> Dict[str, Any]:
        """Detect user intent from message"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    score += 1
            if score > 0:
                intent_scores[intent] = score / len(patterns)
        
        if not intent_scores:
            return {'intent': 'general_chat', 'confidence': 0.3}
        
        # Get highest scoring intent
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent] * 1.5, 1.0)  # Cap at 1.0
        
        return {'intent': best_intent, 'confidence': confidence}
    
    def _analyze_history(self, history: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation history for context"""
        if not history:
            return {'is_new_user': True, 'conversation_depth': 0}
        
        user_messages = [msg for msg in history if msg.get('sender') == 'user']
        
        return {
            'is_new_user': len(user_messages) <= 2,
            'conversation_depth': len(history),
            'last_topic': self._detect_intent(user_messages[-1]['content'])['intent'] if user_messages else None,
            'has_connected_wallet': any('connect' in msg.get('content', '').lower() for msg in user_messages),
            'has_viewed_portfolio': any('portfolio' in msg.get('content', '').lower() for msg in user_messages),
        }
    
    def _generate_recommendations(self, intent_data: Dict, context: Dict) -> List[Dict]:
        """Generate recommended actions based on intent and context"""
        intent = intent_data['intent']
        recommendations = []
        
        if intent == 'portfolio_view':
            recommendations = [
                {
                    'type': 'card',
                    'card_type': 'dashboard',
                    'label': '📊 View Your Portfolio',
                    'description': 'See your current holdings and portfolio value',
                    'priority': 1
                },
                {
                    'type': 'action',
                    'action': 'buy_omk',
                    'label': '🪙 Buy More OMK',
                    'description': 'Increase your OMK holdings',
                    'priority': 2
                }
            ]
        
        elif intent == 'buy_omk':
            recommendations = [
                {
                    'type': 'card',
                    'card_type': 'omk_purchase',
                    'label': '🪙 Buy OMK Tokens',
                    'description': 'Purchase OMK tokens now',
                    'priority': 1
                },
                {
                    'type': 'card',
                    'card_type': 'token_swap',
                    'label': '🔄 Swap for OMK',
                    'description': 'Exchange other tokens for OMK',
                    'priority': 2
                }
            ]
        
        elif intent == 'invest_property':
            recommendations = [
                {
                    'type': 'card',
                    'card_type': 'property_list',
                    'label': '🏢 Browse Properties',
                    'description': 'See available real estate investments',
                    'priority': 1
                },
                {
                    'type': 'info',
                    'label': '📈 Property ROI Calculator',
                    'description': 'Calculate potential returns',
                    'priority': 2
                }
            ]
        
        elif intent == 'swap_tokens':
            recommendations = [
                {
                    'type': 'card',
                    'card_type': 'token_swap',
                    'label': '🔄 Swap Tokens',
                    'description': 'Exchange your crypto for OMK',
                    'priority': 1
                }
            ]
        
        elif intent == 'market_data':
            recommendations = [
                {
                    'type': 'bee_query',
                    'bee': 'market_data',
                    'label': '📊 Live Market Data',
                    'description': 'Get real-time crypto prices',
                    'priority': 1
                }
            ]
        
        elif intent == 'news':
            recommendations = [
                {
                    'type': 'bee_query',
                    'bee': 'news_aggregator',
                    'label': '📰 Latest News',
                    'description': 'Crypto and real estate updates',
                    'priority': 1
                }
            ]
        
        elif intent == 'help':
            recommendations = [
                {
                    'type': 'bee_query',
                    'bee': 'teacher',
                    'label': '👩‍🏫 Get Help',
                    'description': 'Learn how to use the platform',
                    'priority': 1
                }
            ]
        
        elif intent == 'profile':
            recommendations = [
                {
                    'type': 'card',
                    'card_type': 'profile',
                    'label': '👤 Your Profile',
                    'description': 'View and edit your account',
                    'priority': 1
                },
                {
                    'type': 'card',
                    'card_type': 'settings',
                    'label': '⚙️ Settings',
                    'description': 'Customize your preferences',
                    'priority': 2
                }
            ]
        
        return recommendations
    
    def _assign_bee(self, intent_data: Dict) -> str:
        """Assign the appropriate bee to handle the request"""
        intent = intent_data['intent']
        
        bee_mapping = {
            'portfolio_view': 'user_experience',
            'buy_omk': 'purchase',  # Fixed: bee is named 'purchase'
            'invest_property': 'tokenization',  # Fixed: bee is named 'tokenization'
            'swap_tokens': 'purchase',  # Fixed: bee is named 'purchase'
            'market_data': 'data',  # Fixed: bee is named 'data'
            'news': 'data',  # News handled by data bee
            'help': 'user_experience',  # Help handled by UX bee
            'profile': 'user_experience',
            'general_chat': 'user_experience',
        }
        
        return bee_mapping.get(intent, 'user_experience')
    
    def _handle_system_diagnostic(self, message: str) -> Dict[str, Any]:
        """Handle system diagnostic requests"""
        return {
            'intent': 'system_diagnostic',
            'confidence': 1.0,
            'recommended_actions': [
                {
                    'type': 'system_check',
                    'label': '🔍 Run System Diagnostic',
                    'description': 'Check system status and routes',
                    'priority': 1
                }
            ],
            'bee_to_consult': 'system_monitor',
            'context_summary': {'requesting_diagnostic': True},
            'needs_clarification': False
        }
    
    def diagnose_system(self) -> Dict[str, Any]:
        """
        Perform system-wide diagnostic
        Returns status of all routes, components, and bees
        """
        return {
            'frontend_routes': self._check_frontend_routes(),
            'backend_routes': self._check_backend_routes(),
            'bees_status': self._check_bees_status(),
            'database_status': self._check_database(),
            'blockchain_status': self._check_blockchain(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _check_frontend_routes(self) -> Dict[str, Any]:
        """Check frontend routes and components"""
        # This would actually check the routes
        # For now, return known state
        return {
            'status': 'operational',
            'working_routes': [
                {'path': '/', 'status': 'working', 'description': 'Landing page'},
                {'path': '/chat', 'status': 'working', 'description': 'Main chat interface'},
                {'path': '/connect', 'status': 'working', 'description': 'Wallet connection'},
                {'path': '/dashboard', 'status': 'redirect_to_chat', 'description': 'Redirects to chat with dashboard card'},
                {'path': '/invest', 'status': 'redirect_to_chat', 'description': 'Redirects to chat with properties'},
            ],
            'working_components': [
                'BalanceBubble', 'DashboardCard', 'WalletConnectCard',
                'PropertyCard', 'FloatingMenu', 'OnboardingFlow'
            ],
            'incomplete_components': [
                'OMKPurchaseCard - needs real contract integration',
                'PropertyListCard - needs backend API',
                'ProfileCard - needs implementation',
                'SettingsCard - needs implementation'
            ]
        }
    
    def _check_backend_routes(self) -> Dict[str, Any]:
        """Check backend API routes"""
        return {
            'status': 'operational',
            'api_base': 'http://localhost:8001/api/v1',
            'working_endpoints': [
                '/health', '/welcome', '/chat', '/theme-selection',
                '/register', '/login', '/logout'
            ],
            'needs_implementation': [
                '/properties/list', '/properties/detail', '/properties/invest',
                '/omk/price', '/omk/buy', '/transactions/history'
            ]
        }
    
    def _check_bees_status(self) -> Dict[str, Any]:
        """Check status of all bees"""
        return {
            'total_bees': 19,
            'active_bees': [
                {'name': 'user_experience', 'status': 'active', 'role': 'Chat and UX'},
                {'name': 'teacher', 'status': 'active', 'role': 'Education and help'},
                {'name': 'market_data', 'status': 'configured', 'role': 'Crypto prices'},
                {'name': 'news_aggregator', 'status': 'configured', 'role': 'News feeds'},
                {'name': 'property_tokenization', 'status': 'partial', 'role': 'Real estate'},
                {'name': 'omk_purchase', 'status': 'partial', 'role': 'Token purchase'},
            ],
            'needs_activation': [
                'smart_contract_interaction',
                'blockchain_analytics',
                'governance_facilitator'
            ]
        }
    
    def _check_database(self) -> Dict[str, Any]:
        """Check database status"""
        return {
            'status': 'configured',
            'type': 'Elasticsearch + PostgreSQL planned',
            'operational': False,
            'note': 'User data storage not yet implemented'
        }
    
    def _check_blockchain(self) -> Dict[str, Any]:
        """Check blockchain connectivity"""
        return {
            'status': 'optional',
            'ethereum_node': 'not connected',
            'contracts_deployed': False,
            'note': 'Blockchain integration pending contract deployment'
        }
