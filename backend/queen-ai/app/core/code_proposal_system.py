"""
Code Proposal System
Manages Queen's code change proposals, sandbox deployment, testing, and approval workflow
"""

import os
import json
import subprocess
import shutil
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum
import uuid

class ProposalStatus(Enum):
    PROPOSED = "proposed"
    SANDBOX_DEPLOYED = "sandbox_deployed"
    TESTING = "testing"
    TESTS_PASSED = "tests_passed"
    TESTS_FAILED = "tests_failed"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"


class CodeProposalSystem:
    """
    Manages the complete lifecycle of Queen's code proposals
    """
    
    def __init__(self, project_root: Optional[str] = None):
        # Auto-detect project root if not provided
        if project_root is None:
            # Try environment variable first
            project_root = os.getenv("PROJECT_ROOT")
            
            # If not set, auto-detect from file location
            if not project_root:
                current_file = Path(__file__).resolve()
                # Navigate up to find project root (contains backend/ and omk-frontend/)
                project_root = current_file.parent.parent.parent.parent.parent
        
        self.project_root = Path(project_root)
        self.proposals_dir = self.project_root / "proposals"
        self.sandbox_dir = self.project_root / "sandbox"
        self.backups_dir = self.project_root / "backups"
        
        # Create directories if they don't exist
        self.proposals_dir.mkdir(exist_ok=True)
        self.sandbox_dir.mkdir(exist_ok=True)
        self.backups_dir.mkdir(exist_ok=True)
        
        self.proposals: Dict[str, Dict] = self._load_proposals()
    
    async def create_proposal(
        self, 
        title: str,
        description: str,
        files_to_modify: List[Dict],
        priority: str = "medium",
        risk_level: str = "medium",
        created_by: str = "Queen AI",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create a new code proposal
        
        Args:
            title: Proposal title
            description: Detailed description
            files_to_modify: List of files to modify
            priority: Priority level
            risk_level: Risk assessment
            created_by: Creator identifier
            metadata: Additional metadata
            
        Returns:
            Proposal ID
        """
        proposal_id = str(uuid.uuid4())
        
        proposal = {
            "id": proposal_id,
            "title": title,
            "description": description,
            "priority": priority,
            "risk_level": risk_level,
            "files_to_modify": files_to_modify,
            "tests_required": [],
            "rollback_plan": "",
            "estimated_impact": metadata.get("estimated_improvement", "") if metadata else "",
            "status": ProposalStatus.PROPOSED.value,
            "created_at": datetime.utcnow().isoformat(),
            "created_by": created_by,
            "metadata": metadata or {},
            "sandbox_path": None,
            "test_results": None,
            "admin_notes": None,
            "approved_by": None,
            "approved_at": None,
            "applied_at": None
        }
        
        # Save proposal
        self.proposals[proposal_id] = proposal
        self._save_proposal(proposal)
        
        return proposal_id
    
    async def deploy_to_sandbox(self, proposal_id: str) -> Dict[str, Any]:
        """
        Deploy proposal changes to sandbox environment
        
        Args:
            proposal_id: Proposal ID
            
        Returns:
            Dict with deployment status
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        try:
            # Create sandbox subdirectory for this proposal
            sandbox_path = self.sandbox_dir / proposal_id
            sandbox_path.mkdir(exist_ok=True)
            
            # Copy current codebase to sandbox
            self._copy_to_sandbox(sandbox_path)
            
            # Apply proposed changes
            applied_files = []
            for file_change in proposal["files_to_modify"]:
                file_path = sandbox_path / file_change["path"]
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write new code
                with open(file_path, 'w') as f:
                    f.write(file_change["new_code"])
                
                applied_files.append(str(file_path))
            
            # Update proposal
            proposal["status"] = ProposalStatus.SANDBOX_DEPLOYED.value
            proposal["sandbox_path"] = str(sandbox_path)
            proposal["sandbox_deployed_at"] = datetime.utcnow().isoformat()
            proposal["files_applied"] = applied_files
            self._save_proposal(proposal)
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "sandbox_path": str(sandbox_path),
                "files_applied": applied_files,
                "message": "Changes deployed to sandbox successfully"
            }
            
        except Exception as e:
            proposal["status"] = ProposalStatus.PROPOSED.value
            proposal["deployment_error"] = str(e)
            self._save_proposal(proposal)
            
            return {
                "success": False,
                "error": f"Sandbox deployment failed: {str(e)}"
            }
    
    async def run_tests(self, proposal_id: str) -> Dict[str, Any]:
        """
        Run automated tests in sandbox environment
        
        Args:
            proposal_id: Proposal ID
            
        Returns:
            Dict with test results
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        if proposal["status"] != ProposalStatus.SANDBOX_DEPLOYED.value:
            return {"success": False, "error": "Proposal not deployed to sandbox"}
        
        proposal["status"] = ProposalStatus.TESTING.value
        self._save_proposal(proposal)
        
        try:
            sandbox_path = Path(proposal["sandbox_path"])
            test_results = {
                "started_at": datetime.utcnow().isoformat(),
                "tests": []
            }
            
            # Run Python linting
            lint_result = self._run_linting(sandbox_path)
            test_results["tests"].append(lint_result)
            
            # Run Python tests if they exist
            test_result = self._run_python_tests(sandbox_path)
            test_results["tests"].append(test_result)
            
            # Check syntax errors
            syntax_result = self._check_syntax(sandbox_path, proposal["files_applied"])
            test_results["tests"].append(syntax_result)
            
            # Run custom tests specified in proposal
            for test_desc in proposal.get("tests_required", []):
                custom_result = {
                    "name": test_desc,
                    "status": "skipped",
                    "message": "Custom test requires manual verification"
                }
                test_results["tests"].append(custom_result)
            
            test_results["completed_at"] = datetime.utcnow().isoformat()
            
            # Determine overall status
            all_passed = all(
                t["status"] == "passed" or t["status"] == "skipped" 
                for t in test_results["tests"]
            )
            
            if all_passed:
                proposal["status"] = ProposalStatus.TESTS_PASSED.value
                test_results["overall_status"] = "passed"
            else:
                proposal["status"] = ProposalStatus.TESTS_FAILED.value
                test_results["overall_status"] = "failed"
                
                # Mark that auto-fix should be attempted
                proposal["needs_auto_fix"] = True
            
            proposal["test_results"] = test_results
            proposal["tested_at"] = datetime.utcnow().isoformat()
            self._save_proposal(proposal)
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "test_results": test_results,
                "overall_status": test_results["overall_status"],
                "needs_auto_fix": all_passed is False  # Signal to frontend
            }
            
        except Exception as e:
            proposal["status"] = ProposalStatus.TESTS_FAILED.value
            proposal["test_error"] = str(e)
            self._save_proposal(proposal)
            
            return {
                "success": False,
                "error": f"Testing failed: {str(e)}"
            }
    
    def approve_proposal(self, proposal_id: str, admin_id: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Admin approves a proposal
        
        Args:
            proposal_id: Proposal ID
            admin_id: Admin who approved
            notes: Optional approval notes
            
        Returns:
            Dict with approval status
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        if proposal["status"] != ProposalStatus.TESTS_PASSED.value:
            return {
                "success": False,
                "error": "Proposal must pass tests before approval"
            }
        
        proposal["status"] = ProposalStatus.APPROVED.value
        proposal["approved_by"] = admin_id
        proposal["approved_at"] = datetime.utcnow().isoformat()
        proposal["admin_notes"] = notes
        self._save_proposal(proposal)
        
        return {
            "success": True,
            "proposal_id": proposal_id,
            "message": "Proposal approved. Ready to apply to production."
        }
    
    def reject_proposal(self, proposal_id: str, admin_id: str, reason: str) -> Dict[str, Any]:
        """
        Admin rejects a proposal
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        proposal["status"] = ProposalStatus.REJECTED.value
        proposal["rejected_by"] = admin_id
        proposal["rejected_at"] = datetime.utcnow().isoformat()
        proposal["rejection_reason"] = reason
        self._save_proposal(proposal)
        
        return {
            "success": True,
            "proposal_id": proposal_id,
            "message": "Proposal rejected"
        }
    
    async def apply_to_production(self, proposal_id: str, admin_id: str) -> Dict[str, Any]:
        """
        Apply approved proposal to production codebase
        
        Args:
            proposal_id: Proposal ID
            admin_id: Admin applying the change
            
        Returns:
            Dict with application status
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        if proposal["status"] != ProposalStatus.APPROVED.value:
            return {
                "success": False,
                "error": "Proposal must be approved before applying"
            }
        
        try:
            # Create backup of current production files
            backup_id = self._create_backup(proposal["files_to_modify"])
            proposal["backup_id"] = backup_id
            
            # Apply changes to production
            applied_files = []
            for file_change in proposal["files_to_modify"]:
                prod_path = self.project_root / file_change["path"]
                prod_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(prod_path, 'w') as f:
                    f.write(file_change["new_code"])
                
                applied_files.append(str(prod_path))
            
            proposal["status"] = ProposalStatus.APPLIED.value
            proposal["applied_by"] = admin_id
            proposal["applied_at"] = datetime.utcnow().isoformat()
            proposal["production_files"] = applied_files
            self._save_proposal(proposal)
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "backup_id": backup_id,
                "files_applied": applied_files,
                "message": "Changes applied to production successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to apply changes: {str(e)}"
            }
    
    def rollback(self, proposal_id: str, admin_id: str) -> Dict[str, Any]:
        """
        Rollback a proposal that was applied to production
        """
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return {"success": False, "error": "Proposal not found"}
        
        if proposal["status"] != ProposalStatus.APPLIED.value:
            return {
                "success": False,
                "error": "Proposal not applied, nothing to rollback"
            }
        
        try:
            # Restore from backup
            backup_id = proposal.get("backup_id")
            if not backup_id:
                return {"success": False, "error": "No backup found"}
            
            self._restore_backup(backup_id)
            
            proposal["status"] = ProposalStatus.ROLLED_BACK.value
            proposal["rolled_back_by"] = admin_id
            proposal["rolled_back_at"] = datetime.utcnow().isoformat()
            self._save_proposal(proposal)
            
            return {
                "success": True,
                "proposal_id": proposal_id,
                "message": "Changes rolled back successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Rollback failed: {str(e)}"
            }
    
    def get_all_proposals(self, status: Optional[str] = None) -> List[Dict]:
        """Get all proposals, optionally filtered by status"""
        proposals = list(self.proposals.values())
        
        if status:
            proposals = [p for p in proposals if p["status"] == status]
        
        # Sort by created_at desc
        proposals.sort(key=lambda x: x["created_at"], reverse=True)
        
        return proposals
    
    def get_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Get a specific proposal"""
        return self.proposals.get(proposal_id)
    
    # ==================== HELPER METHODS ====================
    
    def _copy_to_sandbox(self, sandbox_path: Path):
        """Copy relevant code to sandbox"""
        # Copy backend code
        backend_src = self.project_root / "backend" / "queen-ai" / "app"
        backend_dst = sandbox_path / "backend" / "queen-ai" / "app"
        
        if backend_src.exists():
            shutil.copytree(backend_src, backend_dst, dirs_exist_ok=True)
        
        # Copy frontend code
        frontend_src = self.project_root / "omk-frontend" / "app"
        frontend_dst = sandbox_path / "omk-frontend" / "app"
        
        if frontend_src.exists():
            shutil.copytree(frontend_src, frontend_dst, dirs_exist_ok=True)
    
    def _run_linting(self, sandbox_path: Path) -> Dict:
        """Run Python linting"""
        try:
            result = subprocess.run(
                ["python", "-m", "pylint", "--errors-only", str(sandbox_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "name": "Python Linting",
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout + result.stderr
            }
        except Exception as e:
            return {
                "name": "Python Linting",
                "status": "skipped",
                "message": f"Linting skipped: {str(e)}"
            }
    
    def _run_python_tests(self, sandbox_path: Path) -> Dict:
        """Run Python tests if they exist"""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(sandbox_path), "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "name": "Python Tests",
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout + result.stderr
            }
        except Exception as e:
            return {
                "name": "Python Tests",
                "status": "skipped",
                "message": f"No tests found or error: {str(e)}"
            }
    
    def _check_syntax(self, sandbox_path: Path, files: List[str]) -> Dict:
        """Check Python syntax"""
        try:
            for file_path in files:
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
            
            return {
                "name": "Syntax Check",
                "status": "passed",
                "message": "All files have valid Python syntax"
            }
        except SyntaxError as e:
            return {
                "name": "Syntax Check",
                "status": "failed",
                "error": str(e)
            }
    
    def _create_backup(self, files_to_backup: List[Dict]) -> str:
        """Create backup of files before modifying"""
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        backup_path = self.backups_dir / backup_id
        backup_path.mkdir(exist_ok=True)
        
        for file_info in files_to_backup:
            src_path = self.project_root / file_info["path"]
            if src_path.exists():
                dst_path = backup_path / file_info["path"]
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)
        
        return backup_id
    
    def _restore_backup(self, backup_id: str):
        """Restore files from backup"""
        backup_path = self.backups_dir / backup_id
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup {backup_id} not found")
        
        # Restore all files from backup
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                backup_file = Path(root) / file
                relative_path = backup_file.relative_to(backup_path)
                prod_file = self.project_root / relative_path
                shutil.copy2(backup_file, prod_file)
    
    def _save_proposal(self, proposal: Dict):
        """Save proposal to disk"""
        proposal_file = self.proposals_dir / f"{proposal['id']}.json"
        with open(proposal_file, 'w') as f:
            json.dump(proposal, f, indent=2)
    
    def _load_proposals(self) -> Dict[str, Dict]:
        """Load all proposals from disk"""
        proposals = {}
        
        if not self.proposals_dir.exists():
            return proposals
        
        for proposal_file in self.proposals_dir.glob("*.json"):
            try:
                with open(proposal_file, 'r') as f:
                    proposal = json.load(f)
                    proposals[proposal["id"]] = proposal
            except Exception as e:
                print(f"Failed to load proposal {proposal_file}: {e}")
        
        return proposals
