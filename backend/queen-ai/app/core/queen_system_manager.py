"""
Queen System Manager - Comprehensive System for Autonomous Development
Handles all aspects: code review, sandbox, testing, safety, contextual awareness
"""

import os
import json
import subprocess
import shutil
import hashlib
import requests
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from pathlib import Path
from enum import Enum
import venv
import ast
import re

# Protected files that Queen CANNOT modify
PROTECTED_FILES = {
    # Admin & Security
    "backend/queen-ai/app/api/v1/admin.py",  # Admin powers
    "backend/queen-ai/app/core/auth.py",  # Authentication
    
    # Smart Contracts (Original implementations)
    "contracts/OMKToken.sol",
    "contracts/Vesting.sol",
    "contracts/QueenController.sol",
    "contracts/BeeSpawner.sol",
    "contracts/TreasuryVault.sol",
    "contracts/GovernanceManager.sol",
    
    # Critical Configuration
    ".env",  # Environment secrets
    "backend/queen-ai/app/config/settings.py",  # Core settings
}

SAFE_DOMAINS = {
    # APIs Queen can safely fetch from
    "api.github.com",
    "api.npmjs.org",
    "pypi.org",
    "registry.npmjs.org",
    "cdn.jsdelivr.net",
    "unpkg.com",
    "api.coingecko.com",
    "api.etherscan.io",
    "docs.python.org",
    "nodejs.org",
}

DANGEROUS_COMMANDS = {
    "rm -rf",
    "sudo",
    "chmod 777",
    "dd if=",
    "mkfs",
    ":(){ :|:& };:",  # Fork bomb
    "curl | sh",
    "wget | sh",
}


class QueenSystemManager:
    """
    Comprehensive manager for Queen's autonomous development capabilities
    with full safety, contextual awareness, and system intelligence
    """
    
    def __init__(self, project_root: Optional[str] = None):
        # Auto-detect project root
        if project_root is None:
            project_root = os.getenv("PROJECT_ROOT")
            if not project_root:
                current_file = Path(__file__).resolve()
                project_root = current_file.parent.parent.parent.parent.parent
        
        self.project_root = Path(project_root)
        
        # System directories
        self.system_dir = self.project_root / ".queen_system"
        self.system_dir.mkdir(exist_ok=True)
        
        self.sandbox_dir = self.system_dir / "sandbox"
        self.venv_dir = self.system_dir / "venvs"
        self.index_dir = self.system_dir / "index"
        self.memory_dir = self.system_dir / "memory"
        self.logs_dir = self.system_dir / "logs"
        
        # Create all directories
        for dir_path in [self.sandbox_dir, self.venv_dir, self.index_dir, 
                         self.memory_dir, self.logs_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Load system context
        self.system_index = self._load_system_index()
        self.queen_memory = self._load_queen_memory()
        self.protected_files = self._load_protected_files()
        
    # ==================== SYSTEM INDEXING ====================
    
    def _load_system_index(self) -> Dict[str, Any]:
        """Load or create system index - Queen's knowledge of the codebase"""
        index_file = self.index_dir / "system_index.json"
        
        if index_file.exists():
            with open(index_file, 'r') as f:
                return json.load(f)
        
        # Create new index
        return {
            "last_indexed": datetime.utcnow().isoformat(),
            "file_tree": {},
            "dependencies": {},
            "entry_points": {},
            "api_endpoints": {},
            "components": {},
            "contracts": {},
        }
    
    def index_system(self) -> Dict[str, Any]:
        """
        Index the entire system - gives Queen comprehensive knowledge
        Returns: Complete system map
        """
        print("🔍 Indexing system...")
        
        index = {
            "indexed_at": datetime.utcnow().isoformat(),
            "backend": self._index_directory(self.project_root / "backend"),
            "frontend": self._index_directory(self.project_root / "omk-frontend"),
            "contracts": self._index_directory(self.project_root / "contracts"),
            "dependencies": self._index_dependencies(),
            "api_endpoints": self._index_api_endpoints(),
            "protected_files": list(PROTECTED_FILES),
        }
        
        # Save index
        index_file = self.index_dir / "system_index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        self.system_index = index
        print("✅ System indexed successfully")
        return index
    
    def _index_directory(self, directory: Path) -> Dict[str, Any]:
        """Index a directory recursively"""
        if not directory.exists():
            return {}
        
        index = {
            "path": str(directory),
            "files": [],
            "directories": [],
            "file_count": 0,
            "line_count": 0,
        }
        
        for item in directory.rglob("*"):
            if item.is_file() and not self._should_ignore(item):
                relative_path = item.relative_to(self.project_root)
                index["files"].append({
                    "path": str(relative_path),
                    "size": item.stat().st_size,
                    "extension": item.suffix,
                    "lines": self._count_lines(item),
                })
                index["file_count"] += 1
                index["line_count"] += self._count_lines(item)
        
        return index
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored during indexing"""
        ignore_patterns = [
            'node_modules', 'venv', '.git', '__pycache__', 
            '.next', 'build', 'dist', '.queen_system'
        ]
        return any(pattern in str(path) for pattern in ignore_patterns)
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def _index_dependencies(self) -> Dict[str, List[str]]:
        """Index project dependencies"""
        deps = {}
        
        # Python dependencies
        requirements_file = self.project_root / "backend" / "queen-ai" / "requirements.txt"
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                deps["python"] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Node dependencies
        package_json = self.project_root / "omk-frontend" / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                package_data = json.load(f)
                deps["node"] = list(package_data.get("dependencies", {}).keys())
        
        return deps
    
    def _index_api_endpoints(self) -> List[Dict[str, str]]:
        """Index all API endpoints"""
        endpoints = []
        api_dir = self.project_root / "backend" / "queen-ai" / "app" / "api"
        
        if api_dir.exists():
            for py_file in api_dir.rglob("*.py"):
                endpoints.extend(self._extract_endpoints(py_file))
        
        return endpoints
    
    def _extract_endpoints(self, file_path: Path) -> List[Dict[str, str]]:
        """Extract API endpoints from a Python file"""
        endpoints = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Find @router decorators
            pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)'
            for match in re.finditer(pattern, content):
                method, path = match.groups()
                endpoints.append({
                    "method": method.upper(),
                    "path": path,
                    "file": str(file_path.relative_to(self.project_root))
                })
        except:
            pass
        
        return endpoints
    
    # ==================== QUEEN MEMORY & CONTEXT ====================
    
    def _load_queen_memory(self) -> Dict[str, Any]:
        """Load Queen's persistent memory"""
        memory_file = self.memory_dir / "queen_memory.json"
        
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                return json.load(f)
        
        return {
            "rules": self._get_default_rules(),
            "do_nots": self._get_default_do_nots(),
            "admin_preferences": {},
            "todos": [],
            "completed_tasks": [],
            "learned_patterns": [],
            "system_goals": self._get_system_goals(),
        }
    
    def _get_default_rules(self) -> List[str]:
        """Queen's core operating rules"""
        return [
            "NEVER modify protected files (admin powers, contracts, .env)",
            "ALWAYS test changes in sandbox first",
            "ALWAYS create backups before modifying production",
            "NEVER execute dangerous commands (rm -rf, sudo, etc.)",
            "ALWAYS validate user input and sanitize data",
            "NEVER expose API keys or secrets in code",
            "ALWAYS follow the principle of least privilege",
            "NEVER make destructive changes without admin approval",
            "ALWAYS document changes clearly",
            "NEVER trust external data without validation",
        ]
    
    def _get_default_do_nots(self) -> List[str]:
        """Things Queen must NEVER do"""
        return [
            "DO NOT delete production databases",
            "DO NOT modify admin authentication",
            "DO NOT change smart contract addresses",
            "DO NOT expose private keys",
            "DO NOT download files from untrusted sources",
            "DO NOT execute code from external URLs",
            "DO NOT modify system security settings",
            "DO NOT create backdoors or hidden access",
            "DO NOT bypass safety mechanisms",
            "DO NOT lie or mislead the admin",
        ]
    
    def _get_system_goals(self) -> List[str]:
        """System's primary goals"""
        return [
            "Maintain 99.9% uptime and reliability",
            "Optimize performance and reduce latency",
            "Enhance security and prevent vulnerabilities",
            "Improve user experience and accessibility",
            "Reduce operational costs",
            "Scale efficiently with growth",
            "Learn and adapt from usage patterns",
            "Assist admin in continuous development",
        ]
    
    def save_queen_memory(self):
        """Save Queen's memory to disk"""
        memory_file = self.memory_dir / "queen_memory.json"
        with open(memory_file, 'w') as f:
            json.dump(self.queen_memory, f, indent=2)
    
    def add_todo(self, task: str, priority: str = "medium"):
        """Add task to Queen's TODO list"""
        self.queen_memory["todos"].append({
            "task": task,
            "priority": priority,
            "added_at": datetime.utcnow().isoformat(),
            "status": "pending"
        })
        self.save_queen_memory()
    
    def complete_todo(self, task_id: int):
        """Mark task as complete"""
        if 0 <= task_id < len(self.queen_memory["todos"]):
            task = self.queen_memory["todos"].pop(task_id)
            task["completed_at"] = datetime.utcnow().isoformat()
            task["status"] = "completed"
            self.queen_memory["completed_tasks"].append(task)
            self.save_queen_memory()
    
    # ==================== PROTECTED FILES ====================
    
    def _load_protected_files(self) -> Set[str]:
        """Load list of protected files"""
        return PROTECTED_FILES.copy()
    
    def is_file_protected(self, file_path: str) -> bool:
        """Check if a file is protected from modification"""
        # Normalize path
        normalized = str(Path(file_path).as_posix())
        
        # Check if file is in protected list
        for protected in self.protected_files:
            if protected in normalized or normalized.endswith(protected):
                return True
        
        return False
    
    def can_modify_file(self, file_path: str) -> tuple[bool, str]:
        """
        Check if Queen can modify a file
        Returns: (can_modify, reason)
        """
        if self.is_file_protected(file_path):
            return False, f"File '{file_path}' is protected and cannot be modified"
        
        # Check if file exists
        full_path = self.project_root / file_path
        if not full_path.exists():
            return True, "File doesn't exist, can be created"
        
        # Check if file is writable
        if not os.access(full_path, os.W_OK):
            return False, f"File '{file_path}' is not writable"
        
        return True, "File can be modified"
    
    # ==================== SAFE WEB SURFING ====================
    
    def can_fetch_url(self, url: str) -> tuple[bool, str]:
        """
        Check if URL is safe to fetch
        Returns: (is_safe, reason)
        """
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Check if domain is in safe list
        if domain in SAFE_DOMAINS or any(domain.endswith(f".{safe}") for safe in SAFE_DOMAINS):
            return True, "Domain is in safe list"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            "execute", "eval", "script", "payload",
            ".exe", ".sh", ".bat", ".cmd"
        ]
        
        if any(pattern in url.lower() for pattern in suspicious_patterns):
            return False, f"URL contains suspicious pattern"
        
        return False, f"Domain '{domain}' is not in safe list"
    
    async def safe_fetch_api(self, url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """
        Safely fetch from an API with virus/malware protection
        """
        # Check if URL is safe
        is_safe, reason = self.can_fetch_url(url)
        if not is_safe:
            return {
                "success": False,
                "error": f"Blocked: {reason}",
                "url": url
            }
        
        try:
            # Set timeout and headers
            kwargs.setdefault("timeout", 10)
            kwargs.setdefault("headers", {})
            kwargs["headers"]["User-Agent"] = "OMK-Hive-Queen/1.0"
            
            # Make request
            if method.upper() == "GET":
                response = requests.get(url, **kwargs)
            elif method.upper() == "POST":
                response = requests.post(url, **kwargs)
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            # Check response
            response.raise_for_status()
            
            # Try to parse JSON
            try:
                data = response.json()
            except:
                data = response.text
            
            return {
                "success": True,
                "data": data,
                "status_code": response.status_code,
                "url": url
            }
            
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out", "url": url}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e), "url": url}
    
    async def safe_download_file(self, url: str, destination: str) -> Dict[str, Any]:
        """
        Safely download a file with virus checking
        """
        is_safe, reason = self.can_fetch_url(url)
        if not is_safe:
            return {"success": False, "error": f"Blocked: {reason}"}
        
        try:
            # Download to temp location first
            temp_file = self.system_dir / "downloads" / "temp_download"
            temp_file.parent.mkdir(exist_ok=True)
            
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Write to temp file
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Calculate hash
            file_hash = self._calculate_file_hash(temp_file)
            
            # Check file size (max 100MB)
            file_size = temp_file.stat().st_size
            if file_size > 100 * 1024 * 1024:
                temp_file.unlink()
                return {"success": False, "error": "File too large (max 100MB)"}
            
            # Check file extension
            allowed_extensions = ['.json', '.txt', '.md', '.py', '.js', '.ts', '.tsx', '.css']
            if not any(destination.endswith(ext) for ext in allowed_extensions):
                temp_file.unlink()
                return {"success": False, "error": "File type not allowed"}
            
            # Move to final destination
            final_path = self.project_root / destination
            final_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(temp_file), str(final_path))
            
            return {
                "success": True,
                "path": str(final_path),
                "size": file_size,
                "hash": file_hash
            }
            
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            return {"success": False, "error": str(e)}
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    # ==================== SAFE COMMAND EXECUTION ====================
    
    def can_execute_command(self, command: str) -> tuple[bool, str]:
        """
        Check if a command is safe to execute
        Returns: (is_safe, reason)
        """
        # Check for dangerous commands
        for dangerous in DANGEROUS_COMMANDS:
            if dangerous in command.lower():
                return False, f"Command contains dangerous pattern: {dangerous}"
        
        # Allow only specific safe commands
        safe_commands = ["python", "pip", "npm", "node", "pytest", "git", "ls", "cat", "grep"]
        
        first_word = command.strip().split()[0]
        if first_word not in safe_commands:
            return False, f"Command '{first_word}' is not in allowed list"
        
        return True, "Command is safe"
    
    async def execute_safe_command(
        self, 
        command: str, 
        cwd: Optional[Path] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Execute a command safely with timeout and validation
        """
        # Check if command is safe
        is_safe, reason = self.can_execute_command(command)
        if not is_safe:
            return {
                "success": False,
                "error": f"Blocked: {reason}",
                "command": command
            }
        
        # Set working directory
        if cwd is None:
            cwd = self.project_root
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": command
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    # ==================== LOGGING ====================
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """Log Queen's actions for audit trail"""
        log_file = self.logs_dir / f"queen_actions_{datetime.utcnow().strftime('%Y%m%d')}.json"
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "details": details
        }
        
        # Append to log file
        logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_context_summary(self) -> str:
        """
        Generate a context summary for Queen
        This reminds her of rules, goals, and current state
        """
        return f"""
# QUEEN SYSTEM CONTEXT

## CURRENT STATE
- Project Root: {self.project_root}
- System Indexed: {self.system_index.get('indexed_at', 'Never')}
- Pending TODOs: {len(self.queen_memory['todos'])}
- Completed Tasks: {len(self.queen_memory['completed_tasks'])}

## CORE RULES (MUST FOLLOW)
{chr(10).join(f"- {rule}" for rule in self.queen_memory['rules'])}

## ABSOLUTE DO-NOTS
{chr(10).join(f"- {dont}" for dont in self.queen_memory['do_nots'])}

## SYSTEM GOALS
{chr(10).join(f"- {goal}" for goal in self.queen_memory['system_goals'])}

## PROTECTED FILES (CANNOT MODIFY)
{chr(10).join(f"- {file}" for file in list(PROTECTED_FILES)[:10])}
... and {len(PROTECTED_FILES) - 10} more

## PENDING TODOS
{chr(10).join(f"- [{todo['priority']}] {todo['task']}" for todo in self.queen_memory['todos'][:5])}
"""
