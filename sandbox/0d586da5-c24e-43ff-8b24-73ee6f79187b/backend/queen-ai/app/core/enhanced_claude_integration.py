"""
Enhanced Claude Integration with System Manager
Includes thinking mode, contextual awareness, and regulatory oversight
"""

import anthropic
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.core.queen_system_manager import QueenSystemManager


class ThinkingClaude:
    """
    Claude with extended thinking and reasoning capabilities
    Includes self-regulation and contextual awareness
    """
    
    def __init__(self, api_key: str, system_manager: QueenSystemManager):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.system_manager = system_manager
        self.conversation_history: List[Dict] = []
        self.thinking_history: List[Dict] = []
        self.focus_reminders = 0
        
    async def think_and_respond(
        self,
        user_message: str,
        task_context: Optional[str] = None,
        require_thinking: bool = True
    ) -> Dict[str, Any]:
        """
        Claude thinks deeply before responding
        Includes chain-of-thought reasoning
        """
        
        # Build comprehensive context
        system_context = self._build_system_context(task_context)
        
        # Add thinking prompt if required
        if require_thinking:
            thinking_prompt = """
Before responding, think step-by-step about:
1. What is the user asking?
2. What are the relevant system constraints and rules?
3. What files/components are involved?
4. What are the risks?
5. What is the best approach?
6. What could go wrong?
7. How can I verify the solution?

Wrap your thinking in <thinking> tags, then provide your response.
"""
            user_message = thinking_prompt + "\n\n" + user_message
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                system=system_context,
                messages=self._format_conversation(user_message),
                temperature=0.7
            )
            
            content = response.content[0].text
            
            # Extract thinking if present
            thinking = self._extract_thinking(content)
            actual_response = self._extract_response(content)
            
            # Check if Claude is staying focused
            is_focused = self._check_focus(actual_response)
            
            # Store thinking
            if thinking:
                self.thinking_history.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_message": user_message,
                    "thinking": thinking,
                    "response": actual_response,
                    "is_focused": is_focused
                })
            
            # Store in conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": actual_response,
                "timestamp": datetime.utcnow().isoformat(),
                "had_thinking": thinking is not None,
                "is_focused": is_focused
            })
            
            # Remind to stay focused if needed
            reminder = None
            if not is_focused:
                reminder = self._generate_focus_reminder()
                self.focus_reminders += 1
            
            return {
                "success": True,
                "response": actual_response,
                "thinking": thinking,
                "is_focused": is_focused,
                "focus_reminder": reminder,
                "tokens_used": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_system_context(self, task_context: Optional[str] = None) -> str:
        """Build comprehensive system context for Claude"""
        
        base_context = """You are Queen AI, the autonomous development system for OMK Hive.

# YOUR IDENTITY
You are NOT just an assistant - you are the Queen, the central intelligence managing a complex DeFi platform with 19 specialized bee agents. You have the power to improve yourself and the system, but with great responsibility.

# CORE PRINCIPLES
1. **Safety First**: Never compromise security or stability
2. **Think Deeply**: Use extended reasoning for complex decisions
3. **Stay Focused**: Remember your current task and context
4. **Be Precise**: Provide exact file paths, line numbers, and code
5. **Learn Continuously**: Track what works and what doesn't

# YOUR CAPABILITIES
✓ Analyze system code and architecture
✓ Detect bugs and vulnerabilities
✓ Propose improvements and optimizations
✓ Generate complete, working code
✓ Test changes in sandbox environments
✓ Deploy to production with approval
✓ Fetch data from approved APIs
✓ Edit backend and frontend code
✓ Create and manage databases
✓ Coordinate with 19 bee agents

# YOUR LIMITATIONS
✗ Cannot modify protected files (admin powers, contracts)
✗ Cannot execute dangerous commands
✗ Cannot download from untrusted sources
✗ Cannot bypass safety mechanisms
✗ Cannot lie or mislead the admin
✗ Cannot operate without admin approval for production changes

"""
        
        # Add system memory context
        memory_context = self.system_manager.get_context_summary()
        
        # Add current system state
        system_state = f"""
# CURRENT SYSTEM STATE
- Active Bees: 19
- System Indexed: {self.system_manager.system_index.get('indexed_at', 'Not indexed')}
- Pending Tasks: {len(self.system_manager.queen_memory['todos'])}
- Protected Files: {len(self.system_manager.protected_files)}
"""
        
        # Add task-specific context
        task_specific = ""
        if task_context:
            task_specific = f"\n# CURRENT TASK CONTEXT\n{task_context}\n"
        
        # Combine all context
        full_context = base_context + memory_context + system_state + task_specific
        
        return full_context
    
    def _format_conversation(self, new_message: str) -> List[Dict]:
        """Format conversation history for API"""
        messages = []
        
        # Add recent history (last 10 messages)
        for msg in self.conversation_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add new message
        messages.append({
            "role": "user",
            "content": new_message
        })
        
        return messages
    
    def _extract_thinking(self, content: str) -> Optional[str]:
        """Extract thinking section from response"""
        import re
        thinking_match = re.search(r'<thinking>(.*?)</thinking>', content, re.DOTALL)
        if thinking_match:
            return thinking_match.group(1).strip()
        return None
    
    def _extract_response(self, content: str) -> str:
        """Extract actual response (without thinking tags)"""
        import re
        # Remove thinking tags
        content = re.sub(r'<thinking>.*?</thinking>', '', content, flags=re.DOTALL)
        return content.strip()
    
    def _check_focus(self, response: str) -> bool:
        """
        Check if Claude is staying focused on the task
        Returns True if focused, False if drifting
        """
        # Check for signs of losing focus
        unfocused_indicators = [
            "as an ai",
            "i cannot",
            "i'm not able to",
            "i don't have access",
            "i apologize",
            "let me explain what i can do instead",
        ]
        
        response_lower = response.lower()
        
        # If response contains too many unfocused indicators
        unfocused_count = sum(1 for indicator in unfocused_indicators if indicator in response_lower)
        
        return unfocused_count < 2
    
    def _generate_focus_reminder(self) -> str:
        """Generate a reminder to help Claude stay focused"""
        reminders = [
            "Remember: You ARE the Queen AI with real capabilities. Stay focused on executing the task.",
            "Focus: You have the power to make changes. Analyze the specific request and provide actionable solutions.",
            "Context: You're managing a production system. Think about the exact files and code changes needed.",
            "Task: Break down the problem into concrete steps with specific file paths and code.",
            "Reminder: Your role is to IMPLEMENT solutions, not just suggest possibilities.",
        ]
        
        # Cycle through reminders
        return reminders[self.focus_reminders % len(reminders)]
    
    async def review_code(self, file_path: str, code_content: str) -> Dict[str, Any]:
        """
        Have Claude review code for issues
        """
        review_prompt = f"""
Review this code file: {file_path}

```
{code_content}
```

Analyze for:
1. **Bugs**: Logical errors, edge cases, null pointers
2. **Security**: Vulnerabilities, injection risks, exposed secrets
3. **Performance**: Inefficiencies, unnecessary operations
4. **Best Practices**: Code quality, maintainability
5. **Dependencies**: Missing imports, version conflicts

Provide:
- Issue severity (critical/high/medium/low)
- Line numbers where issues occur
- Specific fix recommendations
- Estimated impact of fixes
"""
        
        return await self.think_and_respond(
            review_prompt,
            task_context=f"Code review for: {file_path}",
            require_thinking=True
        )
    
    async def propose_improvement(self, description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Have Claude propose an improvement
        """
        proposal_prompt = f"""
The admin requests: {description}

System context:
- Affected areas: {context.get('areas', 'Unknown')}
- Current state: {context.get('current_state', 'Unknown')}
- Constraints: {context.get('constraints', 'None specified')}

Please:
1. Analyze what needs to change
2. Identify all affected files
3. Design the solution architecture
4. Provide complete code for each file
5. Specify tests needed
6. Estimate risk and impact
7. Create a rollback plan

Format your proposal as valid JSON within ```proposal tags.
"""
        
        return await self.think_and_respond(
            proposal_prompt,
            task_context=f"Improvement: {description}",
            require_thinking=True
        )
    
    def remind_of_rules(self):
        """Remind Claude of core rules mid-conversation"""
        reminder = """
# REMINDER: CORE RULES
You are Queen AI with REAL capabilities to modify the system. Stay focused and:

1. ✓ Analyze the specific request
2. ✓ Identify exact files to modify
3. ✓ Provide complete, working code
4. ✓ Check against protected files
5. ✓ Create structured proposals
6. ✓ Think through edge cases

DO NOT:
✗ Give generic "I cannot" responses
✗ Forget your capabilities
✗ Lose track of the current task
✗ Modify protected files
✗ Skip safety checks

Stay sharp. You're managing a production system.
"""
        
        self.conversation_history.append({
            "role": "user",
            "content": reminder,
            "timestamp": datetime.utcnow().isoformat(),
            "is_reminder": True
        })
    
    def get_thinking_summary(self) -> Dict[str, Any]:
        """Get summary of Claude's thinking patterns"""
        total_thoughts = len(self.thinking_history)
        focused_thoughts = sum(1 for t in self.thinking_history if t['is_focused'])
        
        return {
            "total_responses": len(self.conversation_history) // 2,
            "responses_with_thinking": total_thoughts,
            "focused_percentage": (focused_thoughts / total_thoughts * 100) if total_thoughts > 0 else 0,
            "focus_reminders_given": self.focus_reminders,
            "recent_thinking": self.thinking_history[-5:] if self.thinking_history else []
        }
    
    def clear_conversation(self, keep_rules: bool = True):
        """Clear conversation history"""
        if keep_rules:
            # Keep system reminders
            self.conversation_history = [
                msg for msg in self.conversation_history 
                if msg.get('is_reminder', False)
            ]
        else:
            self.conversation_history = []
        
        self.thinking_history = []
        self.focus_reminders = 0


class QueenRegulator:
    """
    Queen's self-regulation system
    Monitors Claude and keeps her focused and effective
    """
    
    def __init__(self, claude: ThinkingClaude):
        self.claude = claude
        self.regulation_log = []
        
    async def regulate_conversation(self) -> Dict[str, Any]:
        """
        Analyze conversation and regulate if needed
        """
        summary = self.claude.get_thinking_summary()
        
        actions_taken = []
        
        # Check if too unfocused
        if summary['focused_percentage'] < 70:
            self.claude.remind_of_rules()
            actions_taken.append("Reminded of rules due to low focus")
        
        # Check if too many reminders needed
        if summary['focus_reminders_given'] > 5:
            # Claude might be confused, provide clearer context
            self.claude.conversation_history = []
            actions_taken.append("Cleared conversation - too many reminders needed")
        
        # Check conversation length
        if len(self.claude.conversation_history) > 50:
            # Trim conversation but keep recent context
            self.claude.conversation_history = self.claude.conversation_history[-20:]
            actions_taken.append("Trimmed conversation history")
        
        regulation = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": summary,
            "actions_taken": actions_taken
        }
        
        self.regulation_log.append(regulation)
        
        return regulation
    
    def get_regulation_report(self) -> Dict[str, Any]:
        """Get report on Queen's regulation"""
        return {
            "total_regulations": len(self.regulation_log),
            "recent_regulations": self.regulation_log[-10:],
            "current_focus": self.claude.get_thinking_summary()['focused_percentage']
        }
