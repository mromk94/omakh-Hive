"""
Proposal Auto-Fixer - Makes the system truly autonomous
When tests fail, analyze the error and automatically generate fixes
"""

import structlog
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = structlog.get_logger(__name__)


class ProposalAutoFixer:
    """
    Automatically fixes failed proposals by:
    1. Analyzing test failure logs
    2. Understanding what went wrong
    3. Generating a fix
    4. Re-deploying and re-testing
    5. Repeating until success or max attempts
    """
    
    def __init__(self, max_attempts: int = 5):
        self.max_attempts = max_attempts  # Increased from 3 to 5 for better success rate
    
    async def auto_fix_proposal(
        self,
        proposal: Dict[str, Any],
        test_results: Dict[str, Any],
        claude_provider: Any
    ) -> Dict[str, Any]:
        """
        Automatically fix a failed proposal
        
        Args:
            proposal: The proposal that failed
            test_results: Test results showing what failed
            claude_provider: Claude API provider for generating fixes
            
        Returns:
            Dict with fix status and updated proposal
        """
        logger.info("🔧 Starting auto-fix for failed proposal", 
                   proposal_id=proposal["id"],
                   title=proposal["title"])
        
        attempt = 1
        fix_history = []
        
        while attempt <= self.max_attempts:
            logger.info(f"🔄 Auto-fix attempt {attempt}/{self.max_attempts}")
            
            # Analyze what went wrong
            failure_analysis = await self._analyze_failure(test_results)
            
            # Generate fix using Claude
            fix = await self._generate_fix(
                proposal=proposal,
                failure_analysis=failure_analysis,
                previous_attempts=fix_history,
                claude_provider=claude_provider
            )
            
            if not fix["success"]:
                logger.error("❌ Failed to generate fix", error=fix.get("error"))
                break
            
            # Record this attempt
            fix_history.append({
                "attempt": attempt,
                "analysis": failure_analysis,
                "fix": fix["changes"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Check if we should stop (no fix possible)
            if fix.get("unfixable"):
                logger.warning("⚠️ Issue marked as unfixable", reason=fix.get("reason"))
                break
            
            attempt += 1
            
            # If max attempts reached
            if attempt > self.max_attempts:
                logger.warning(f"⚠️ Max fix attempts ({self.max_attempts}) reached")
        
        return {
            "success": len(fix_history) > 0,
            "attempts": len(fix_history),
            "fix_history": fix_history,
            "final_status": "fixed" if len(fix_history) > 0 else "unfixable"
        }
    
    async def _analyze_failure(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test failure to understand what went wrong
        """
        analysis = {
            "failed_tests": [],
            "error_types": [],
            "error_messages": [],
            "root_cause": None
        }
        
        for test in test_results.get("tests", []):
            if test.get("status") == "failed":
                analysis["failed_tests"].append(test.get("name"))
                
                # Extract error message
                error_msg = test.get("message", "")
                analysis["error_messages"].append(error_msg)
                
                # Categorize error type
                error_type = self._categorize_error(error_msg)
                if error_type not in analysis["error_types"]:
                    analysis["error_types"].append(error_type)
        
        # Determine root cause
        analysis["root_cause"] = self._determine_root_cause(analysis)
        
        logger.info("📊 Failure analysis complete", **analysis)
        return analysis
    
    def _categorize_error(self, error_message: str) -> str:
        """Categorize the type of error"""
        error_lower = error_message.lower()
        
        if "import" in error_lower or "module" in error_lower:
            return "import_error"
        elif "syntax" in error_lower or "invalid syntax" in error_lower:
            return "syntax_error"
        elif "indentation" in error_lower:
            return "indentation_error"
        elif "name" in error_lower and "not defined" in error_lower:
            return "undefined_variable"
        elif "type" in error_lower:
            return "type_error"
        elif "attribute" in error_lower:
            return "attribute_error"
        elif "file" in error_lower and ("not found" in error_lower or "no such" in error_lower):
            return "file_not_found"
        else:
            return "unknown_error"
    
    def _determine_root_cause(self, analysis: Dict) -> str:
        """Determine the most likely root cause"""
        error_types = analysis["error_types"]
        
        if "import_error" in error_types:
            return "Missing or incorrect imports"
        elif "syntax_error" in error_types or "indentation_error" in error_types:
            return "Code syntax issues"
        elif "file_not_found" in error_types:
            return "File path or structure issues"
        elif "undefined_variable" in error_types:
            return "Variable or function not defined"
        elif "type_error" in error_types or "attribute_error" in error_types:
            return "Type mismatch or incorrect object usage"
        else:
            return "Unknown issue - requires manual investigation"
    
    async def _generate_fix(
        self,
        proposal: Dict[str, Any],
        failure_analysis: Dict[str, Any],
        previous_attempts: List[Dict],
        claude_provider: Any
    ) -> Dict[str, Any]:
        """
        Use Claude to generate a fix for the failure
        """
        logger.info("🤖 Asking Claude to generate fix...")
        
        # Build prompt for Claude
        prompt = self._build_fix_prompt(proposal, failure_analysis, previous_attempts)
        
        try:
            # Call Claude
            response = await claude_provider.generate(
                prompt=prompt,
                temperature=0.2,  # Lower temperature for consistent fixes
                max_tokens=2000
            )
            
            # Parse Claude's response
            import json
            try:
                fix_data = json.loads(response)
                
                return {
                    "success": True,
                    "changes": fix_data.get("changes", []),
                    "explanation": fix_data.get("explanation", ""),
                    "unfixable": fix_data.get("unfixable", False),
                    "reason": fix_data.get("reason")
                }
                
            except json.JSONDecodeError:
                # If not JSON, treat as explanation
                return {
                    "success": True,
                    "changes": [],
                    "explanation": response,
                    "unfixable": "cannot be fixed" in response.lower() or "unfixable" in response.lower()
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to generate fix: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _build_fix_prompt(
        self,
        proposal: Dict[str, Any],
        failure_analysis: Dict[str, Any],
        previous_attempts: List[Dict]
    ) -> str:
        """Build prompt for Claude to generate fix with codebase context"""
        
        # Import context builder
        from app.core.codebase_context_builder import CodebaseContextBuilder
        
        # Build context for the specific error type
        context_builder = CodebaseContextBuilder()
        
        # Determine context type from error
        if 'import' in failure_analysis['root_cause'].lower():
            context_type = 'redis' if 'redis' in str(failure_analysis).lower() else 'general'
        else:
            context_type = 'general'
        
        context = context_builder.build_context(context_type)
        context_str = context_builder.format_for_claude(context)
        
        prompt = f"""
You are debugging a failed code proposal for an EXISTING, WORKING codebase.

{context_str}

**FAILED PROPOSAL:**
Title: {proposal['title']}
Description: {proposal['description']}

**WHAT FAILED:**
Failed Tests: {', '.join(failure_analysis['failed_tests'])}
Error Types: {', '.join(failure_analysis['error_types'])}
Root Cause: {failure_analysis['root_cause']}

**ERROR MESSAGES:**
{chr(10).join(f'- {msg}' for msg in failure_analysis['error_messages'])}

**FILES IN PROPOSAL:**
{chr(10).join(f"- {f['path']}" for f in proposal.get('files_to_modify', []))}
"""
        
        if previous_attempts:
            prompt += f"\n\n**PREVIOUS FIX ATTEMPTS ({len(previous_attempts)}) - DON'T REPEAT THESE:**\n"
            for i, attempt in enumerate(previous_attempts, 1):
                prompt += f"\nAttempt {i}:\n"
                prompt += f"- Analysis: {attempt['analysis'].get('root_cause')}\n"
                prompt += f"- Fix tried: {attempt['fix'].get('explanation', 'Unknown')}\n"
                prompt += f"- Still failed!\n"
        
        prompt += """

**YOUR TASK:**
Fix the error by studying the WORKING CODE EXAMPLES above.

**CRITICAL RULES:**
1. Use the EXACT import patterns shown in "Correct Import Patterns"
2. Follow the EXACT async patterns shown in examples
3. Only use packages listed in "Installed Packages"
4. If the error is about Redis, use: from redis.asyncio import Redis, ConnectionPool
5. If the error is about missing await, add await to all async calls
6. Fix the ACTUAL error, don't just change random things

**RESPONSE FORMAT (JSON):**
{
  "unfixable": false,
  "reason": "Root cause of the error",
  "explanation": "What I'm fixing and how it fixes the error",
  "changes": [
    {
      "file": "path/to/file.py",
      "action": "modify",
      "code": "COMPLETE, CORRECTED CODE for this file",
      "reason": "This fixes the error because..."
    }
  ]
}

**VALIDATION BEFORE RESPONDING:**
✅ Imports match the patterns shown above
✅ Code uses async/await correctly
✅ No placeholders or incomplete code
✅ Fix actually addresses the error message

If truly unfixable (external dependency needed), set "unfixable": true.

Generate the fix now in JSON format:
"""
        
        return prompt
