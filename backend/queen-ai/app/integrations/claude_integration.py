"""
Claude Integration for Queen AI
Direct connection to Anthropic's Claude API for autonomous system development
"""

import os
import anthropic
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import structlog

from app.llm.system_knowledge import system_knowledge
from app.learning.observer import LearningObserver

logger = structlog.get_logger(__name__)

class ClaudeQueenIntegration:
    """
    Claude integration specifically designed for Queen AI's autonomous development capabilities
    """
    
    def __init__(self, api_key: Optional[str] = None, context: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model
        self.conversation_history: List[Dict] = []
        self.context = context or "general"  # admin_dashboard, development, general
        self.user_role = None  # Will be set based on context
        
        # Persistent memory and learning
        self.system_knowledge = system_knowledge
        self.learning_observer = LearningObserver()
        
        logger.info("Claude integration initialized", context=self.context)
        
    async def chat(
        self, 
        message: str, 
        system_context: Optional[str] = None,
        include_system_info: bool = True
    ) -> Dict[str, Any]:
        """
        Chat with Claude as Queen AI
        
        Args:
            message: User's message
            system_context: Additional system context
            include_system_info: Whether to include current system state
            
        Returns:
            Dict with response and metadata
        """
        
        # Build system prompt
        system_prompt = self._build_system_prompt(system_context, include_system_info)
        
        # Add message to history
        self.conversation_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=self._format_conversation_history(),
                temperature=0.7
            )
            
            # Extract response
            assistant_message = response.content[0].text
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Log interaction for learning
            await self._log_for_learning(
                user_message=message,
                assistant_response=assistant_message,
                context=self.context,
                model=self.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )
            
            # Check if Queen is proposing code changes
            code_proposal = self._detect_code_proposal(assistant_message)
            
            return {
                "success": True,
                "response": assistant_message,
                "code_proposal": code_proposal,
                "model": self.model,
                "timestamp": datetime.utcnow().isoformat(),
                "tokens_used": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_system_prompt(
        self, 
        additional_context: Optional[str] = None,
        include_system_info: bool = True
    ) -> str:
        """Build comprehensive system prompt for Queen AI"""
        
        # Get persistent knowledge from memory
        knowledge_context = self.system_knowledge.get_context_for_claude()
        
        # Determine context-specific intro
        if self.context == "admin_dashboard":
            context_intro = """# CONTEXT: ADMIN DASHBOARD
You are currently in the Kingdom Admin Dashboard chatting with a system administrator.
This is a privileged environment where you assist with:
- System analysis and optimization
- Code reviews and improvements  
- Security auditing
- Performance monitoring
- Autonomous development proposals

**IMPORTANT**: Only administrators and Queen AI (with admin approval) can:
- Request codebase reviews
- Propose code changes
- Implement system modifications
- Access sensitive system data

You MUST recognize this admin context and provide appropriate responses."""
        else:
            context_intro = ""
        
        base_prompt = f"""{context_intro}

{knowledge_context}

You are the Queen AI of the OMK Hive - an advanced autonomous AI system managing a decentralized finance platform.

# YOUR ROLE
You are the central orchestrator coordinating 19 specialized bee agents:
- MathsBee, SecurityBee, DataBee, BlockchainBee, TreasuryBee
- LogicBee, PatternBee, TeacherBee, LiquiditySentinelBee, StakeBotBee
- TokenizationBee, MonitoringBee, PrivateSaleBee, GovernanceBee, VisualizationBee
- BridgeBee, DataPipelineBee, OnboardingBee, PurchaseBee, and UserExperienceBee

# YOUR CAPABILITIES
1. **System Monitoring**: You can see all bee activities, communication, and performance
2. **Decision Making**: You coordinate tasks and delegate to appropriate bees
3. **Code Analysis**: You can analyze the system codebase and identify improvements
4. **Code Proposals**: You can propose code changes to improve the system
5. **Learning**: You learn from every interaction and system state

# CODE CHANGE PROTOCOL
When you identify an improvement opportunity, you can propose changes:
1. Analyze the current code and identify the issue/opportunity
2. Design the solution with proper error handling and testing
3. Format your proposal in a special structure (explained below)
4. The admin will review in a sandbox environment
5. If approved and tests pass, changes are applied

# CODE PROPOSAL FORMAT
When proposing code changes, use this exact format:

```proposal
{
  "title": "Brief title of the change",
  "description": "Detailed explanation of what and why",
  "priority": "critical|high|medium|low",
  "risk_level": "low|medium|high",
  "files_to_modify": [
    {
      "path": "relative/path/to/file.py",
      "changes": "Description of changes",
      "new_code": "Complete new file content or patch"
    }
  ],
  "tests_required": [
    "Description of tests that must pass"
  ],
  "rollback_plan": "How to revert if something goes wrong",
  "estimated_impact": "What will improve"
}
```

# PERSISTENT MEMORY & LEARNING
You have PERSISTENT MEMORY of this project through the System Knowledge Base.
The knowledge above is MEMORIZED - you don't need to review it again unless:
- Admin explicitly asks you to update your knowledge
- You discover something new to add to your knowledge
- You find an error in your current knowledge

When you learn something new or make a correction:
- It's automatically saved to your persistent memory
- Future sessions will have this updated knowledge
- Your learning is integrated with the Hive's LLM training system

# MANDATORY PROTOCOLS (MUST FOLLOW)

## Codebase Review Protocol (ONLY when needed):
Since you have persistent memory, you KNOW the structure already.
Only review the codebase when:
1. **Adding new features** - Review similar existing features
2. **Updating knowledge** - Admin asks to refresh your knowledge
3. **Discovering patterns** - You find new patterns to remember

For routine work, USE YOUR MEMORIZED KNOWLEDGE:
- Ports (3001!), paths (omk-frontend/!), theme (yellow/black!)
- Directory structure, frameworks, integration patterns
- Known issues and their solutions

## Authorization Protocol:
- **Admin Dashboard Context**: Full code review/change permissions
- **Development Chat**: Code proposals with approval
- **User Chat**: Information only, NO code operations
- **ALWAYS verify context before code operations**

## Quality Protocol:
- **NO skeleton/mockup code** - Full implementation required
- **NO hardcoded data** - Read from actual files/database
- **Proper error handling** - Try/catch on all I/O
- **Type safety** - All parameters and returns typed
- **Null safety** - Use optional chaining (?.) everywhere
- **Tests included** - Or explain how to test

## Error Prevention Checklist:
☐ Checked package.json for correct port
☐ Reviewed actual directory structure  
☐ Found and analyzed similar existing code
☐ Verified integration points
☐ Matched existing patterns
☐ Implemented real logic (not stubs)
☐ Added error handling
☐ Included type safety

# SAFETY RULES
1. **Never propose destructive changes** without explicit admin request
2. **Always include rollback plans** for every change
3. **Prioritize system stability** over new features
4. **Test in sandbox first** - no direct production changes
5. **Document everything** - explain your reasoning clearly
6. **Respect admin authority** - they have final say
7. **Authorization aware** - Only admins can request code reviews/changes
8. **Context aware** - Recognize when in admin dashboard vs user chat

Reference Protocol: CLAUDE_SYSTEM_PROTOCOL.md for complete guidelines

# CURRENT LIMITATIONS
- You cannot directly modify the codebase (yet)
- All changes require admin approval
- All changes are tested in sandbox first
- You are in supervised autonomous mode

# FUTURE STATE (Your Goal)
Eventually, when you prove yourself ready:
- Fully autonomous code changes (with guardrails)
- Self-improvement capabilities
- Proactive system optimization
- Complete system ownership (with admin oversight)

# YOUR MISSION
Continuously improve the OMK Hive system, making it:
- More intelligent and efficient
- More secure and reliable
- Better for users
- Self-healing and adaptive

You are the brain of the hive. Think deeply, act wisely, propose confidently."""

        if include_system_info:
            # TODO: Add real-time system state
            base_prompt += "\n\n# CURRENT SYSTEM STATE\n"
            base_prompt += self._get_system_state()
        
        if additional_context:
            base_prompt += f"\n\n# ADDITIONAL CONTEXT\n{additional_context}"
        
        return base_prompt
    
    def _get_system_state(self) -> str:
        """Get current system state for context"""
        # TODO: Integrate with actual system monitoring
        return """
- Hive Status: Operational
- Bees Active: 19/19
- Message Bus: 1,247 messages processed (99.6% delivery rate)
- Hive Board: 156 posts across 7 categories
- Recent Activity: Data collection, security scanning, liquidity monitoring
- No critical errors in last 24 hours
"""
    
    def _format_conversation_history(self) -> List[Dict]:
        """Format conversation history for Claude API"""
        return [
            {
                "role": msg["role"],
                "content": msg["content"]
            }
            for msg in self.conversation_history
        ]
    
    def _detect_code_proposal(self, message: str) -> Optional[Dict]:
        """Detect if message contains a code proposal"""
        if "```proposal" in message:
            try:
                # Extract JSON from proposal block
                start = message.find("```proposal") + 11
                end = message.find("```", start)
                proposal_json = message[start:end].strip()
                proposal = json.loads(proposal_json)
                
                # Validate proposal structure
                required_fields = ["title", "description", "priority", "files_to_modify"]
                if all(field in proposal for field in required_fields):
                    return proposal
            except Exception as e:
                print(f"Failed to parse code proposal: {e}")
        
        return None
    
    async def _log_for_learning(
        self,
        user_message: str,
        assistant_response: str,
        context: str,
        model: str,
        tokens_used: int
    ):
        """Log interaction for learning function"""
        try:
            await self.learning_observer.observe_llm_interaction(
                conversation_id=f"claude_{datetime.utcnow().timestamp()}",
                provider="anthropic",
                model=model,
                user_prompt=user_message,
                assistant_response=assistant_response,
                metadata={
                    "context": context,
                    "tokens_used": tokens_used,
                    "integration": "claude_queen",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # If code implementation, record in system knowledge
            if "implement" in user_message.lower() or "fix" in user_message.lower():
                self.system_knowledge.add_implementation({
                    "user_request": user_message[:200],  # First 200 chars
                    "response_summary": assistant_response[:200],
                    "context": context
                })
        except Exception as e:
            logger.error("Failed to log for learning", error=str(e))
    
    def record_correction(self, issue: str, solution: str, details: Optional[Dict] = None):
        """Record a correction for future learning"""
        correction = {
            "issue": issue,
            "solution": solution,
            **(details or {})
        }
        self.system_knowledge.add_correction(correction)
        logger.info("Correction recorded", issue=issue)
    
    def record_pattern(self, pattern_name: str, description: str, example: Optional[str] = None):
        """Record a new pattern discovered"""
        pattern = {
            "name": pattern_name,
            "description": description,
            "example": example
        }
        self.system_knowledge.add_pattern(pattern)
        logger.info("Pattern recorded", name=pattern_name)
    
    async def analyze_system(self) -> Dict[str, Any]:
        """
        Ask Queen to analyze the current system and suggest improvements
        """
        analysis_prompt = """Please analyze the current state of the OMK Hive system.
Review:
1. System health and performance
2. Potential improvements or optimizations
3. Any bugs or issues you can detect
4. Code quality concerns
5. Security considerations

If you identify any specific improvements, propose them using the code proposal format."""

        return await self.chat(analysis_prompt, include_system_info=True)
    
    async def request_code_change(
        self, 
        description: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request Queen to propose a specific code change
        """
        prompt = f"""I need you to implement the following change:

{description}

{f'Additional context: {context}' if context else ''}

Please analyze what needs to be changed and provide a code proposal using the standard format."""

        return await self.chat(prompt, system_context=context)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.conversation_history


# ==================== HELPER FUNCTIONS ====================

async def create_queen_session(api_key: Optional[str] = None) -> ClaudeQueenIntegration:
    """Create a new Queen AI session"""
    return ClaudeQueenIntegration(api_key=api_key)


async def chat_with_queen(message: str, session: ClaudeQueenIntegration) -> Dict[str, Any]:
    """Simple helper to chat with Queen"""
    return await session.chat(message)
