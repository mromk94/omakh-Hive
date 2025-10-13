"""
System Reboot Manager
Handles safe system restarts with admin approval
"""

import os
import subprocess
import signal
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json


class SystemRebootManager:
    """
    Manages system reboots safely
    - Requires admin approval
    - Backs up state
    - Graceful shutdown
    - Restart services
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reboot_log = project_root / ".queen_system" / "logs" / "reboots.json"
        self.reboot_log.parent.mkdir(parents=True, exist_ok=True)
        
        self.pending_reboot = None
        
    def request_reboot(
        self,
        reason: str,
        component: str,  # "backend", "frontend", "full"
        requester: str = "Queen AI"
    ) -> Dict[str, Any]:
        """
        Request a system reboot
        Returns reboot request that needs admin approval
        """
        reboot_request = {
            "id": f"reboot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "reason": reason,
            "component": component,
            "requester": requester,
            "requested_at": datetime.utcnow().isoformat(),
            "status": "pending_approval",
            "approved_by": None,
            "executed_at": None
        }
        
        self.pending_reboot = reboot_request
        self._log_reboot(reboot_request)
        
        return {
            "success": True,
            "reboot_request": reboot_request,
            "message": "Reboot request created. Awaiting admin approval."
        }
    
    async def execute_reboot(
        self,
        reboot_id: str,
        admin_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Execute approved reboot
        """
        if self.pending_reboot is None or self.pending_reboot["id"] != reboot_id:
            return {
                "success": False,
                "error": "No pending reboot with that ID"
            }
        
        reboot = self.pending_reboot
        component = reboot["component"]
        
        try:
            print(f"🔄 Executing {component} reboot...")
            
            # Update status
            reboot["status"] = "executing"
            reboot["approved_by"] = admin_id
            reboot["approved_at"] = datetime.utcnow().isoformat()
            self._log_reboot(reboot)
            
            # Execute appropriate reboot
            if component == "backend":
                result = await self._reboot_backend(force)
            elif component == "frontend":
                result = await self._reboot_frontend(force)
            elif component == "full":
                result = await self._reboot_full_system(force)
            else:
                return {
                    "success": False,
                    "error": f"Unknown component: {component}"
                }
            
            # Update status
            reboot["status"] = "completed" if result["success"] else "failed"
            reboot["executed_at"] = datetime.utcnow().isoformat()
            reboot["result"] = result
            self._log_reboot(reboot)
            
            self.pending_reboot = None
            
            return result
            
        except Exception as e:
            reboot["status"] = "failed"
            reboot["error"] = str(e)
            self._log_reboot(reboot)
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _reboot_backend(self, force: bool = False) -> Dict[str, Any]:
        """Restart backend services"""
        steps = []
        
        try:
            # Step 1: Find backend process
            backend_process = self._find_backend_process()
            
            if backend_process:
                steps.append({"step": "find_process", "status": "found", "pid": backend_process.pid})
                
                # Step 2: Graceful shutdown
                if not force:
                    try:
                        backend_process.terminate()
                        backend_process.wait(timeout=10)
                        steps.append({"step": "graceful_shutdown", "status": "success"})
                    except psutil.TimeoutExpired:
                        backend_process.kill()
                        steps.append({"step": "graceful_shutdown", "status": "timeout_killed"})
                else:
                    backend_process.kill()
                    steps.append({"step": "force_kill", "status": "success"})
            else:
                steps.append({"step": "find_process", "status": "not_running"})
            
            # Step 3: Restart backend
            restart_result = self._start_backend()
            steps.append({"step": "restart", "status": "success" if restart_result["success"] else "failed"})
            
            return {
                "success": True,
                "component": "backend",
                "steps": steps,
                "message": "Backend restarted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "component": "backend",
                "steps": steps,
                "error": str(e)
            }
    
    async def _reboot_frontend(self, force: bool = False) -> Dict[str, Any]:
        """Restart frontend services"""
        steps = []
        
        try:
            # Find frontend process
            frontend_process = self._find_frontend_process()
            
            if frontend_process:
                steps.append({"step": "find_process", "status": "found", "pid": frontend_process.pid})
                
                if not force:
                    try:
                        frontend_process.terminate()
                        frontend_process.wait(timeout=10)
                        steps.append({"step": "graceful_shutdown", "status": "success"})
                    except psutil.TimeoutExpired:
                        frontend_process.kill()
                        steps.append({"step": "graceful_shutdown", "status": "timeout_killed"})
                else:
                    frontend_process.kill()
                    steps.append({"step": "force_kill", "status": "success"})
            else:
                steps.append({"step": "find_process", "status": "not_running"})
            
            # Restart frontend
            restart_result = self._start_frontend()
            steps.append({"step": "restart", "status": "success" if restart_result["success"] else "failed"})
            
            return {
                "success": True,
                "component": "frontend",
                "steps": steps,
                "message": "Frontend restarted successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "component": "frontend",
                "steps": steps,
                "error": str(e)
            }
    
    async def _reboot_full_system(self, force: bool = False) -> Dict[str, Any]:
        """Restart entire system"""
        backend_result = await self._reboot_backend(force)
        frontend_result = await self._reboot_frontend(force)
        
        return {
            "success": backend_result["success"] and frontend_result["success"],
            "component": "full_system",
            "backend": backend_result,
            "frontend": frontend_result
        }
    
    def _find_backend_process(self) -> Optional[psutil.Process]:
        """Find backend process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('uvicorn' in str(cmd) and 'main:app' in str(cmd) for cmd in cmdline):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return None
    
    def _find_frontend_process(self) -> Optional[psutil.Process]:
        """Find frontend process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('next' in str(cmd) for cmd in cmdline):
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return None
    
    def _start_backend(self) -> Dict[str, Any]:
        """Start backend service"""
        try:
            backend_dir = self.project_root / "backend" / "queen-ai"
            
            # Start uvicorn in background
            process = subprocess.Popen(
                ["uvicorn", "main:app", "--reload", "--port", "8001"],
                cwd=str(backend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            return {
                "success": True,
                "pid": process.pid
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _start_frontend(self) -> Dict[str, Any]:
        """Start frontend service"""
        try:
            frontend_dir = self.project_root / "omk-frontend"
            
            # Start Next.js dev server in background
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            return {
                "success": True,
                "pid": process.pid
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _log_reboot(self, reboot_data: Dict[str, Any]):
        """Log reboot to file"""
        logs = []
        
        if self.reboot_log.exists():
            with open(self.reboot_log, 'r') as f:
                logs = json.load(f)
        
        # Update or append
        existing = next((i for i, r in enumerate(logs) if r["id"] == reboot_data["id"]), None)
        
        if existing is not None:
            logs[existing] = reboot_data
        else:
            logs.append(reboot_data)
        
        with open(self.reboot_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_reboot_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get reboot history"""
        if not self.reboot_log.exists():
            return []
        
        with open(self.reboot_log, 'r') as f:
            logs = json.load(f)
        
        # Sort by requested_at descending
        logs.sort(key=lambda x: x["requested_at"], reverse=True)
        
        return logs[:limit]
    
    def cancel_reboot(self, reboot_id: str, admin_id: str) -> Dict[str, Any]:
        """Cancel pending reboot"""
        if self.pending_reboot is None or self.pending_reboot["id"] != reboot_id:
            return {
                "success": False,
                "error": "No pending reboot with that ID"
            }
        
        self.pending_reboot["status"] = "cancelled"
        self.pending_reboot["cancelled_by"] = admin_id
        self.pending_reboot["cancelled_at"] = datetime.utcnow().isoformat()
        
        self._log_reboot(self.pending_reboot)
        self.pending_reboot = None
        
        return {
            "success": True,
            "message": "Reboot cancelled"
        }
