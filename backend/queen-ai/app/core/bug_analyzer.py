"""
Bug Analyzer for Queen AI

Analyzes bug reports and suggests fixes using Claude and codebase navigation.
"""

import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.tools.codebase_navigator import CodebaseNavigator
from app.integrations.claude_integration import ClaudeQueenIntegration

logger = structlog.get_logger(__name__)


class BugAnalyzer:
    """
    Analyze bug reports and suggest potential fixes
    
    Workflow:
    1. Parse bug description
    2. Find likely locations in codebase
    3. Analyze relevant code
    4. Generate potential fixes
    """
    
    def __init__(self):
        self.codebase_nav = CodebaseNavigator()
        self.claude = ClaudeQueenIntegration(context="autonomous_dev")
    
    async def analyze_bug(
        self,
        bug_description: str,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze a bug report
        
        Args:
            bug_description: Description of the bug
            user_context: Additional context (error logs, steps to reproduce, etc.)
        
        Returns:
            {
                "likely_locations": [...],
                "root_cause_analysis": "...",
                "suggested_fixes": [...],
                "severity": "critical|high|medium|low",
                "affected_users": "estimate"
            }
        """
        logger.info(f"Analyzing bug: {bug_description[:100]}...")
        
        # Step 1: Find likely bug locations
        likely_locations = await self.codebase_nav.find_bug_location(bug_description)
        
        logger.info(f"Found {len(likely_locations)} potential locations")
        
        # Step 2: Read relevant code
        code_context = await self._gather_code_context(likely_locations[:5])
        
        # Step 3: Ask Claude to analyze
        analysis_prompt = f"""# BUG ANALYSIS REQUEST

**Bug Description:**
{bug_description}

**User Context:**
{user_context if user_context else "None provided"}

**Potentially Affected Files:**
{self._format_locations(likely_locations[:5])}

**Code Context:**
{code_context}

---

Please analyze this bug and provide:

1. **Root Cause Analysis**: What's likely causing this bug?
2. **Severity Assessment**: critical, high, medium, or low?
3. **Affected Scope**: How many users/features affected?
4. **Suggested Fixes**: 2-3 potential approaches to fix this
5. **Testing Strategy**: How to verify the fix works

Format your response as JSON:
```json
{{
  "root_cause": "...",
  "severity": "high",
  "affected_scope": "...",
  "suggested_fixes": [
    {{
      "approach": "...",
      "files_to_modify": ["..."],
      "risk_level": "low|medium|high",
      "effort": "small|medium|large"
    }}
  ],
  "testing_strategy": "..."
}}
```
"""
        
        # Get Claude's analysis
        claude_response = await self.claude.chat(
            message=analysis_prompt,
            include_system_info=False
        )
        
        # Parse response
        analysis = self._parse_claude_analysis(claude_response)
        
        # Enhance with our findings
        analysis["likely_locations"] = likely_locations[:10]
        analysis["analyzed_at"] = datetime.utcnow().isoformat()
        analysis["bug_description"] = bug_description
        
        logger.info(
            "Bug analysis complete",
            severity=analysis.get("severity"),
            fixes=len(analysis.get("suggested_fixes", []))
        )
        
        return analysis
    
    async def _gather_code_context(self, locations: List[Dict]) -> str:
        """Gather code snippets from likely bug locations"""
        context = []
        
        for loc in locations[:5]:  # Top 5 files
            file_path = loc["file"]
            content = await self.codebase_nav.get_file_content(file_path)
            
            if content:
                # Show first 50 lines or full file if smaller
                lines = content.split('\n')
                preview = '\n'.join(lines[:50])
                
                context.append(f"""
### File: {file_path}
```
{preview}
{'...' if len(lines) > 50 else ''}
```
""")
        
        return '\n\n'.join(context)
    
    def _format_locations(self, locations: List[Dict]) -> str:
        """Format file locations for display"""
        formatted = []
        for i, loc in enumerate(locations, 1):
            formatted.append(
                f"{i}. {loc['file']} (relevance: {loc['relevance']}, "
                f"{loc['lines']} lines, {loc['functions']} functions)"
            )
        return '\n'.join(formatted)
    
    def _parse_claude_analysis(self, claude_response: Dict) -> Dict[str, Any]:
        """Parse Claude's analysis response"""
        import json
        import re
        
        response_text = claude_response.get("response", "")
        
        # Try to extract JSON from response
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                logger.warning("Failed to parse Claude's JSON response")
        
        # Fallback to basic parsing
        return {
            "root_cause": "Analysis failed - please review manually",
            "severity": "medium",
            "affected_scope": "Unknown",
            "suggested_fixes": [],
            "testing_strategy": "Manual testing required",
            "raw_response": response_text
        }
    
    async def create_test_case(self, bug_description: str, analysis: Dict) -> str:
        """Generate a test case that reproduces the bug"""
        test_prompt = f"""# TEST CASE GENERATION

**Bug:** {bug_description}

**Root Cause:** {analysis.get('root_cause', 'Unknown')}

**Affected Files:** {', '.join([f['file'] for f in analysis.get('likely_locations', [])[:3]])}

Please generate a test case (Python pytest or TypeScript Jest) that:
1. Reproduces this bug
2. Will pass once the bug is fixed
3. Includes clear assertions

Provide the complete test code.
"""
        
        response = await self.claude.chat(
            message=test_prompt,
            include_system_info=False
        )
        
        return response.get("response", "# Test case generation failed")
    
    async def suggest_quick_fix(self, analysis: Dict) -> Optional[Dict]:
        """Suggest the quickest, lowest-risk fix"""
        fixes = analysis.get("suggested_fixes", [])
        
        if not fixes:
            return None
        
        # Sort by risk and effort
        quick_fixes = sorted(
            fixes,
            key=lambda f: (
                {"low": 1, "medium": 2, "high": 3}.get(f.get("risk_level", "medium"), 2),
                {"small": 1, "medium": 2, "large": 3}.get(f.get("effort", "medium"), 2)
            )
        )
        
        return quick_fixes[0] if quick_fixes else None
