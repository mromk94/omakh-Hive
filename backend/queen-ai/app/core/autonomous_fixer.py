"""
Autonomous Fixer for Queen AI

Complete autonomous bug fixing workflow:
1. Analyze bug
2. Generate multiple fix approaches
3. Test each in sandbox
4. Present best fix to admin
5. Apply on approval
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import uuid

from app.core.bug_analyzer import BugAnalyzer
from app.core.code_proposal_system import CodeProposalSystem, ProposalStatus
from app.core.enhanced_sandbox_system import SandboxEnvironment
from app.integrations.claude_integration import ClaudeQueenIntegration
from app.tools.codebase_navigator import CodebaseNavigator

logger = structlog.get_logger(__name__)


class FixApproach:
    """Represents one potential fix approach"""
    def __init__(self, approach_id: str, description: str, files: List[Dict], risk_level: str):
        self.id = approach_id
        self.description = description
        self.files_to_modify = files
        self.risk_level = risk_level
        self.test_results = None
        self.success_rate = 0.0
        self.errors = []


class AutonomousFixer:
    """
    Autonomous bug fixing system
    
    This is the core of Queen's self-healing capability.
    """
    
    def __init__(self, project_root: Optional[str] = None):
        self.bug_analyzer = BugAnalyzer()
        self.proposal_system = CodeProposalSystem(project_root)
        self.claude = ClaudeQueenIntegration(context="autonomous_dev")
        self.codebase_nav = CodebaseNavigator(project_root)
        
        self.active_fixes: Dict[str, Dict] = {}  # fix_id -> fix_info
    
    async def fix_bug(
        self,
        bug_description: str,
        admin_id: str,
        user_context: Optional[Dict] = None,
        num_approaches: int = 3,
        auto_apply_if_safe: bool = False
    ) -> Dict[str, Any]:
        """
        Complete autonomous bug fixing workflow
        
        Args:
            bug_description: Description of the bug to fix
            admin_id: Admin who reported the bug
            user_context: Additional context (logs, screenshots, etc.)
            num_approaches: Number of different fix approaches to try
            auto_apply_if_safe: Auto-apply if all tests pass and risk is low
        
        Returns:
            {
                "fix_id": "...",
                "status": "testing|awaiting_approval|applied|failed",
                "analysis": {...},
                "approaches_tested": 3,
                "best_approach": {...},
                "proposal_id": "...",
                "test_results": {...}
            }
        """
        fix_id = str(uuid.uuid4())
        
        logger.info(
            "Starting autonomous bug fix",
            fix_id=fix_id,
            bug=bug_description[:100]
        )
        
        try:
            # ========== STEP 1: ANALYZE BUG ==========
            logger.info(f"[{fix_id}] Step 1: Analyzing bug...")
            
            analysis = await self.bug_analyzer.analyze_bug(
                bug_description=bug_description,
                user_context=user_context
            )
            
            logger.info(
                f"[{fix_id}] Analysis complete",
                severity=analysis.get("severity"),
                locations=len(analysis.get("likely_locations", []))
            )
            
            # ========== STEP 2: GENERATE FIX APPROACHES ==========
            logger.info(f"[{fix_id}] Step 2: Generating {num_approaches} fix approaches...")
            
            approaches = []
            for i in range(num_approaches):
                approach = await self._generate_fix_approach(
                    analysis=analysis,
                    approach_number=i + 1,
                    previous_approaches=approaches
                )
                if approach:
                    approaches.append(approach)
            
            logger.info(f"[{fix_id}] Generated {len(approaches)} approaches")
            
            if not approaches:
                return {
                    "success": False,
                    "error": "Failed to generate any fix approaches",
                    "analysis": analysis
                }
            
            # ========== STEP 3: TEST EACH APPROACH IN SANDBOX ==========
            logger.info(f"[{fix_id}] Step 3: Testing approaches in sandbox...")
            
            test_results = []
            for i, approach in enumerate(approaches, 1):
                logger.info(f"[{fix_id}] Testing approach {i}/{len(approaches)}...")
                
                result = await self._test_approach_in_sandbox(
                    fix_id=fix_id,
                    approach=approach,
                    bug_description=bug_description
                )
                
                approach.test_results = result
                test_results.append(result)
                
                logger.info(
                    f"[{fix_id}] Approach {i} test complete",
                    success=result.get("success"),
                    tests_passed=result.get("tests_passed", 0)
                )
            
            # ========== STEP 4: SELECT BEST FIX ==========
            logger.info(f"[{fix_id}] Step 4: Selecting best fix...")
            
            best_approach = self._select_best_approach(approaches, test_results)
            
            if not best_approach:
                return {
                    "success": False,
                    "error": "No approach passed all tests",
                    "analysis": analysis,
                    "approaches_tested": len(approaches),
                    "test_results": test_results
                }
            
            logger.info(
                f"[{fix_id}] Best approach selected",
                approach=best_approach.description,
                success_rate=best_approach.success_rate
            )
            
            # ========== STEP 5: CREATE PROPOSAL ==========
            logger.info(f"[{fix_id}] Step 5: Creating code proposal...")
            
            proposal_data = await self._create_proposal_from_approach(
                approach=best_approach,
                analysis=analysis,
                bug_description=bug_description
            )
            
            proposal_result = self.proposal_system.create_proposal(
                proposal_data=proposal_data,
                queen_session_id=f"autonomous_fix_{fix_id}"
            )
            
            proposal_id = proposal_result.get("proposal_id")
            
            logger.info(f"[{fix_id}] Proposal created: {proposal_id}")
            
            # ========== STEP 6: AUTO-APPLY IF SAFE ==========
            auto_applied = False
            if auto_apply_if_safe:
                if (best_approach.risk_level == "low" and 
                    best_approach.success_rate >= 0.95):
                    
                    logger.info(f"[{fix_id}] Auto-applying safe fix...")
                    
                    apply_result = self.proposal_system.apply_to_production(
                        proposal_id=proposal_id,
                        applied_by=f"queen_auto_{admin_id}"
                    )
                    
                    auto_applied = apply_result.get("success", False)
            
            # ========== FINAL RESULT ==========
            result = {
                "success": True,
                "fix_id": fix_id,
                "status": "applied" if auto_applied else "awaiting_approval",
                "analysis": analysis,
                "approaches_tested": len(approaches),
                "test_results": [
                    {
                        "approach": a.description,
                        "success": a.test_results.get("success"),
                        "tests_passed": a.test_results.get("tests_passed"),
                        "risk_level": a.risk_level
                    }
                    for a in approaches
                ],
                "best_approach": {
                    "description": best_approach.description,
                    "risk_level": best_approach.risk_level,
                    "success_rate": best_approach.success_rate,
                    "files_modified": [f["path"] for f in best_approach.files_to_modify]
                },
                "proposal_id": proposal_id,
                "auto_applied": auto_applied,
                "requires_admin_approval": not auto_applied,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store for tracking
            self.active_fixes[fix_id] = result
            
            logger.info(
                f"[{fix_id}] Autonomous fix complete!",
                status=result["status"],
                proposal_id=proposal_id
            )
            
            return result
        
        except Exception as e:
            logger.error(f"[{fix_id}] Autonomous fix failed: {str(e)}")
            return {
                "success": False,
                "fix_id": fix_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _generate_fix_approach(
        self,
        analysis: Dict,
        approach_number: int,
        previous_approaches: List[FixApproach]
    ) -> Optional[FixApproach]:
        """Generate a single fix approach"""
        try:
            # Build prompt for Claude
            prompt = f"""# FIX GENERATION (Approach {approach_number})

**Bug Analysis:**
- Root Cause: {analysis.get('root_cause')}
- Severity: {analysis.get('severity')}
- Affected Files: {', '.join([loc['file'] for loc in analysis.get('likely_locations', [])[:3]])}

**Previous Approaches:**
{self._format_previous_approaches(previous_approaches)}

**Your Task:**
Generate a DIFFERENT approach to fix this bug. Be creative and consider:
- Alternative locations to fix
- Different algorithms
- Edge cases the previous approaches might miss

**Output Format (JSON):**
```json
{{
  "approach_description": "Brief description of this approach",
  "risk_level": "low|medium|high",
  "files_to_modify": [
    {{
      "path": "relative/path/to/file.py",
      "changes_description": "What to change",
      "new_code": "The actual code changes (full file or diff)"
    }}
  ],
  "why_different": "How this differs from previous approaches",
  "edge_cases_handled": ["list of edge cases this handles"]
}}
```
"""
            
            response = await self.claude.chat(
                message=prompt,
                include_system_info=False
            )
            
            # Parse response
            import json
            import re
            
            response_text = response.get("response", "")
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            
            if not json_match:
                logger.warning(f"Failed to parse approach {approach_number}")
                return None
            
            approach_data = json.loads(json_match.group(1))
            
            # Create FixApproach object
            approach = FixApproach(
                approach_id=f"approach_{approach_number}",
                description=approach_data.get("approach_description", ""),
                files=approach_data.get("files_to_modify", []),
                risk_level=approach_data.get("risk_level", "medium")
            )
            
            return approach
        
        except Exception as e:
            logger.error(f"Failed to generate approach {approach_number}: {e}")
            return None
    
    def _format_previous_approaches(self, approaches: List[FixApproach]) -> str:
        """Format previous approaches for context"""
        if not approaches:
            return "None yet - this is the first approach"
        
        formatted = []
        for i, approach in enumerate(approaches, 1):
            formatted.append(f"{i}. {approach.description} (risk: {approach.risk_level})")
        
        return '\n'.join(formatted)
    
    async def _test_approach_in_sandbox(
        self,
        fix_id: str,
        approach: FixApproach,
        bug_description: str
    ) -> Dict[str, Any]:
        """Test a fix approach in isolated sandbox"""
        try:
            logger.info(f"Creating sandbox for {approach.id}...")
            
            # Create sandbox
            sandbox = SandboxEnvironment(
                proposal_id=f"{fix_id}_{approach.id}",
                project_root=self.proposal_system.project_root
            )
            
            sandbox_result = await sandbox.create()
            
            if not sandbox_result.get("success"):
                return {
                    "success": False,
                    "error": "Sandbox creation failed",
                    "tests_passed": 0
                }
            
            # Apply changes in sandbox
            for file_change in approach.files_to_modify:
                await sandbox.modify_file(
                    file_path=file_change["path"],
                    new_content=file_change.get("new_code", "")
                )
            
            # Run tests
            test_result = await sandbox.run_tests("all")
            
            # Cleanup
            await sandbox.cleanup()
            
            # Calculate success rate
            if test_result.get("success"):
                total_tests = test_result.get("total_tests", 1)
                passed_tests = test_result.get("tests_passed", 0)
                approach.success_rate = passed_tests / total_tests if total_tests > 0 else 0
            
            return test_result
        
        except Exception as e:
            logger.error(f"Sandbox testing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tests_passed": 0
            }
    
    def _select_best_approach(
        self,
        approaches: List[FixApproach],
        test_results: List[Dict]
    ) -> Optional[FixApproach]:
        """Select the best fix approach based on test results"""
        # Filter to successful approaches
        successful = [a for a in approaches if a.test_results and a.test_results.get("success")]
        
        if not successful:
            return None
        
        # Sort by success rate and risk level
        successful.sort(
            key=lambda a: (
                a.success_rate,
                -{"low": 3, "medium": 2, "high": 1}.get(a.risk_level, 2)
            ),
            reverse=True
        )
        
        return successful[0]
    
    async def _create_proposal_from_approach(
        self,
        approach: FixApproach,
        analysis: Dict,
        bug_description: str
    ) -> Dict[str, Any]:
        """Create a code proposal from a fix approach"""
        return {
            "title": f"Autonomous Fix: {bug_description[:100]}",
            "description": f"""# Autonomous Bug Fix

**Bug:** {bug_description}

**Root Cause:** {analysis.get('root_cause')}

**Fix Approach:** {approach.description}

**Risk Level:** {approach.risk_level}

**Test Results:** {approach.success_rate * 100:.1f}% tests passed

**Files Modified:**
{chr(10).join([f"- {f['path']}" for f in approach.files_to_modify])}
""",
            "priority": "high" if analysis.get("severity") in ["critical", "high"] else "medium",
            "risk_level": approach.risk_level,
            "files_to_modify": approach.files_to_modify,
            "tests_required": [
                "All existing tests must pass",
                "Bug must be reproducible and fixed",
                "No regressions introduced"
            ],
            "rollback_plan": "Git revert + restore from backup",
            "estimated_impact": f"Fixes {analysis.get('severity')} bug affecting {analysis.get('affected_scope', 'unknown users')}"
        }
    
    async def approve_and_apply(
        self,
        fix_id: str,
        approved_by: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Admin approves and applies an autonomous fix
        
        Args:
            fix_id: The fix ID
            approved_by: Admin ID who approved
            notes: Optional approval notes
        """
        fix_info = self.active_fixes.get(fix_id)
        
        if not fix_info:
            return {
                "success": False,
                "error": "Fix ID not found"
            }
        
        proposal_id = fix_info.get("proposal_id")
        
        if not proposal_id:
            return {
                "success": False,
                "error": "No proposal ID associated with this fix"
            }
        
        # Apply to production
        result = self.proposal_system.apply_to_production(
            proposal_id=proposal_id,
            applied_by=approved_by
        )
        
        if result.get("success"):
            # Update fix status
            fix_info["status"] = "applied"
            fix_info["applied_by"] = approved_by
            fix_info["applied_at"] = datetime.utcnow().isoformat()
            fix_info["approval_notes"] = notes
            
            logger.info(
                "Autonomous fix applied!",
                fix_id=fix_id,
                proposal_id=proposal_id,
                approved_by=approved_by
            )
        
        return result
    
    async def reject_fix(
        self,
        fix_id: str,
        rejected_by: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Admin rejects an autonomous fix
        """
        fix_info = self.active_fixes.get(fix_id)
        
        if not fix_info:
            return {
                "success": False,
                "error": "Fix ID not found"
            }
        
        proposal_id = fix_info.get("proposal_id")
        
        if proposal_id:
            self.proposal_system.reject_proposal(
                proposal_id=proposal_id,
                rejected_by=rejected_by,
                reason=reason
            )
        
        # Update fix status
        fix_info["status"] = "rejected"
        fix_info["rejected_by"] = rejected_by
        fix_info["rejected_at"] = datetime.utcnow().isoformat()
        fix_info["rejection_reason"] = reason
        
        logger.info(
            "Autonomous fix rejected",
            fix_id=fix_id,
            reason=reason
        )
        
        return {
            "success": True,
            "message": "Fix rejected"
        }
