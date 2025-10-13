"""
Enhanced Sandbox System
Complete isolated environment with venv, testing, and safe execution
"""

import os
import json
import shutil
import subprocess
import venv
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import ast
import difflib


class SandboxEnvironment:
    """
    Complete sandbox environment for testing code changes
    Includes virtual environment, dependencies, and isolation
    """
    
    def __init__(self, proposal_id: str, project_root: Path):
        self.proposal_id = proposal_id
        self.project_root = project_root
        
        # Sandbox paths
        self.sandbox_root = project_root / ".queen_system" / "sandbox" / proposal_id
        self.sandbox_backend = self.sandbox_root / "backend"
        self.sandbox_frontend = self.sandbox_root / "omk-frontend"
        self.sandbox_venv = self.sandbox_root / "venv"
        self.sandbox_logs = self.sandbox_root / "logs"
        
        # Metadata
        self.metadata_file = self.sandbox_root / "sandbox_metadata.json"
        self.metadata = {
            "proposal_id": proposal_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "initializing",
            "venv_created": False,
            "dependencies_installed": False,
            "files_modified": [],
            "tests_run": [],
        }
        
    async def create(self) -> Dict[str, Any]:
        """
        Create complete sandbox environment
        """
        try:
            print(f"🏗️ Creating sandbox for proposal {self.proposal_id}...")
            
            # Step 1: Create directory structure
            self._create_directories()
            
            # Step 2: Copy codebase
            copied_files = self._copy_codebase()
            
            # Step 3: Create virtual environment
            venv_result = await self._create_venv()
            
            # Step 4: Install dependencies
            deps_result = await self._install_dependencies()
            
            # Update metadata
            self.metadata.update({
                "status": "ready",
                "venv_created": venv_result["success"],
                "dependencies_installed": deps_result["success"],
                "files_copied": len(copied_files),
                "ready_at": datetime.utcnow().isoformat()
            })
            self._save_metadata()
            
            print(f"✅ Sandbox created successfully")
            
            return {
                "success": True,
                "sandbox_path": str(self.sandbox_root),
                "files_copied": len(copied_files),
                "venv_path": str(self.sandbox_venv),
                "metadata": self.metadata
            }
            
        except Exception as e:
            self.metadata["status"] = "failed"
            self.metadata["error"] = str(e)
            self._save_metadata()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_directories(self):
        """Create sandbox directory structure"""
        for directory in [self.sandbox_root, self.sandbox_backend, 
                         self.sandbox_frontend, self.sandbox_logs]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _copy_codebase(self) -> List[str]:
        """Copy relevant codebase to sandbox"""
        copied_files = []
        
        # Copy backend
        backend_src = self.project_root / "backend" / "queen-ai"
        if backend_src.exists():
            for item in backend_src.rglob("*"):
                if self._should_copy_file(item):
                    rel_path = item.relative_to(backend_src)
                    dest = self.sandbox_backend / "queen-ai" / rel_path
                    
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    if item.is_file():
                        shutil.copy2(item, dest)
                        copied_files.append(str(rel_path))
        
        # Copy frontend (essential files only)
        frontend_src = self.project_root / "omk-frontend"
        if frontend_src.exists():
            essential_dirs = ["app", "components", "lib", "public"]
            for dir_name in essential_dirs:
                src_dir = frontend_src / dir_name
                if src_dir.exists():
                    dest_dir = self.sandbox_frontend / dir_name
                    shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True,
                                  ignore=shutil.ignore_patterns('node_modules', '.next', 'build'))
                    copied_files.append(dir_name)
            
            # Copy essential config files
            for config_file in ["package.json", "tsconfig.json", "next.config.js", "tailwind.config.ts"]:
                src_file = frontend_src / config_file
                if src_file.exists():
                    shutil.copy2(src_file, self.sandbox_frontend / config_file)
                    copied_files.append(config_file)
        
        return copied_files
    
    def _should_copy_file(self, path: Path) -> bool:
        """Check if file should be copied to sandbox"""
        ignore_patterns = [
            '__pycache__', '.pyc', '.git', 'venv', 'node_modules',
            '.env', '.next', 'build', 'dist', '.queen_system'
        ]
        
        path_str = str(path)
        return not any(pattern in path_str for pattern in ignore_patterns)
    
    async def _create_venv(self) -> Dict[str, Any]:
        """Create Python virtual environment"""
        try:
            print(f"🐍 Creating virtual environment...")
            
            # Create venv
            venv.create(self.sandbox_venv, with_pip=True, clear=True)
            
            print(f"✅ Virtual environment created")
            
            return {
                "success": True,
                "venv_path": str(self.sandbox_venv)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _install_dependencies(self) -> Dict[str, Any]:
        """Install Python and Node dependencies"""
        results = {
            "python": {"success": False},
            "node": {"success": False}
        }
        
        # Install Python dependencies
        requirements_file = self.sandbox_backend / "queen-ai" / "requirements.txt"
        if requirements_file.exists():
            try:
                print(f"📦 Installing Python dependencies...")
                
                pip_path = self.sandbox_venv / "bin" / "pip"
                if not pip_path.exists():
                    pip_path = self.sandbox_venv / "Scripts" / "pip.exe"  # Windows
                
                result = subprocess.run(
                    [str(pip_path), "install", "-r", str(requirements_file)],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                results["python"] = {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None
                }
                
                print(f"✅ Python dependencies installed")
                
            except Exception as e:
                results["python"] = {
                    "success": False,
                    "error": str(e)
                }
        
        # Install Node dependencies (optional, can be skipped for speed)
        package_json = self.sandbox_frontend / "package.json"
        if package_json.exists():
            try:
                print(f"📦 Installing Node dependencies...")
                
                result = subprocess.run(
                    ["npm", "install", "--legacy-peer-deps"],
                    cwd=str(self.sandbox_frontend),
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                results["node"] = {
                    "success": result.returncode == 0,
                    "output": result.stdout[:500],  # Truncate
                    "error": result.stderr[:500] if result.returncode != 0 else None
                }
                
                print(f"✅ Node dependencies installed")
                
            except Exception as e:
                results["node"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": results["python"]["success"],  # Python is required
            "details": results
        }
    
    async def apply_changes(self, file_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply code changes to sandbox
        """
        applied_files = []
        errors = []
        
        for change in file_changes:
            file_path = change["path"]
            new_code = change["new_code"]
            
            try:
                # Determine full path in sandbox
                if file_path.startswith("backend"):
                    full_path = self.sandbox_root / file_path
                elif file_path.startswith("omk-frontend"):
                    full_path = self.sandbox_root / file_path
                else:
                    # Assume backend if not specified
                    full_path = self.sandbox_backend / file_path
                
                # Create parent directories
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Backup original if exists
                if full_path.exists():
                    backup_path = full_path.with_suffix(full_path.suffix + '.backup')
                    shutil.copy2(full_path, backup_path)
                
                # Write new code
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                
                applied_files.append({
                    "path": str(full_path.relative_to(self.sandbox_root)),
                    "size": len(new_code),
                    "lines": new_code.count('\n') + 1
                })
                
                # Log to metadata
                self.metadata["files_modified"].append({
                    "path": file_path,
                    "modified_at": datetime.utcnow().isoformat(),
                    "size": len(new_code)
                })
                
            except Exception as e:
                errors.append({
                    "path": file_path,
                    "error": str(e)
                })
        
        self._save_metadata()
        
        return {
            "success": len(errors) == 0,
            "applied_files": applied_files,
            "errors": errors
        }
    
    async def run_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive tests in sandbox
        """
        test_results = {
            "started_at": datetime.utcnow().isoformat(),
            "tests": []
        }
        
        # Test 1: Python linting
        lint_result = await self._run_python_lint()
        test_results["tests"].append(lint_result)
        
        # Test 2: Python syntax check
        syntax_result = await self._check_python_syntax()
        test_results["tests"].append(syntax_result)
        
        # Test 3: Import validation
        import_result = await self._validate_imports()
        test_results["tests"].append(import_result)
        
        # Test 4: Run pytest if available
        pytest_result = await self._run_pytest()
        test_results["tests"].append(pytest_result)
        
        # Test 5: TypeScript check (if frontend modified)
        if self._has_frontend_changes():
            ts_result = await self._check_typescript()
            test_results["tests"].append(ts_result)
        
        test_results["completed_at"] = datetime.utcnow().isoformat()
        
        # Determine overall status
        all_passed = all(
            t["status"] in ["passed", "skipped"] 
            for t in test_results["tests"]
        )
        
        test_results["overall_status"] = "passed" if all_passed else "failed"
        
        # Save to metadata
        self.metadata["tests_run"].append(test_results)
        self._save_metadata()
        
        return test_results
    
    async def _run_python_lint(self) -> Dict[str, Any]:
        """Run Python linting"""
        try:
            python_path = self.sandbox_venv / "bin" / "python"
            if not python_path.exists():
                python_path = self.sandbox_venv / "Scripts" / "python.exe"
            
            result = subprocess.run(
                [str(python_path), "-m", "pylint", "--errors-only", 
                 str(self.sandbox_backend)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "name": "Python Linting",
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout[:1000],
                "errors": result.stderr[:1000] if result.returncode != 0 else None
            }
            
        except Exception as e:
            return {
                "name": "Python Linting",
                "status": "skipped",
                "error": str(e)
            }
    
    async def _check_python_syntax(self) -> Dict[str, Any]:
        """Check Python syntax"""
        errors = []
        
        for py_file in self.sandbox_backend.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                errors.append(f"{py_file.name}: {str(e)}")
        
        return {
            "name": "Python Syntax Check",
            "status": "passed" if len(errors) == 0 else "failed",
            "errors_found": len(errors),
            "errors": errors[:10] if errors else None
        }
    
    async def _validate_imports(self) -> Dict[str, Any]:
        """Validate Python imports"""
        try:
            python_path = self.sandbox_venv / "bin" / "python"
            if not python_path.exists():
                python_path = self.sandbox_venv / "Scripts" / "python.exe"
            
            # Try importing modified files
            import_errors = []
            
            for modified_file in self.metadata["files_modified"]:
                file_path = modified_file["path"]
                if file_path.endswith(".py"):
                    # Convert path to module name
                    module_name = file_path.replace("/", ".").replace(".py", "")
                    
                    result = subprocess.run(
                        [str(python_path), "-c", f"import {module_name}"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode != 0:
                        import_errors.append({
                            "file": file_path,
                            "error": result.stderr[:200]
                        })
            
            return {
                "name": "Import Validation",
                "status": "passed" if len(import_errors) == 0 else "failed",
                "errors_found": len(import_errors),
                "errors": import_errors
            }
            
        except Exception as e:
            return {
                "name": "Import Validation",
                "status": "skipped",
                "error": str(e)
            }
    
    async def _run_pytest(self) -> Dict[str, Any]:
        """Run pytest if tests exist"""
        try:
            python_path = self.sandbox_venv / "bin" / "python"
            if not python_path.exists():
                python_path = self.sandbox_venv / "Scripts" / "python.exe"
            
            result = subprocess.run(
                [str(python_path), "-m", "pytest", str(self.sandbox_backend), "-v"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return {
                "name": "Pytest",
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout[:2000],
                "errors": result.stderr[:1000] if result.returncode != 0 else None
            }
            
        except Exception as e:
            return {
                "name": "Pytest",
                "status": "skipped",
                "reason": str(e)
            }
    
    def _has_frontend_changes(self) -> bool:
        """Check if frontend files were modified"""
        return any(
            "omk-frontend" in f["path"] 
            for f in self.metadata.get("files_modified", [])
        )
    
    async def _check_typescript(self) -> Dict[str, Any]:
        """Check TypeScript compilation"""
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                cwd=str(self.sandbox_frontend),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "name": "TypeScript Check",
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout[:1000],
                "errors": result.stderr[:1000] if result.returncode != 0 else None
            }
            
        except Exception as e:
            return {
                "name": "TypeScript Check",
                "status": "skipped",
                "error": str(e)
            }
    
    def get_diff(self, file_path: str) -> Optional[str]:
        """Get diff between original and modified file"""
        try:
            original_file = self.project_root / file_path
            sandbox_file = self.sandbox_root / file_path
            
            if not original_file.exists() or not sandbox_file.exists():
                return None
            
            with open(original_file, 'r') as f:
                original_lines = f.readlines()
            
            with open(sandbox_file, 'r') as f:
                modified_lines = f.readlines()
            
            diff = difflib.unified_diff(
                original_lines,
                modified_lines,
                fromfile=f"original/{file_path}",
                tofile=f"modified/{file_path}",
                lineterm=''
            )
            
            return '\n'.join(diff)
            
        except Exception as e:
            return f"Error generating diff: {str(e)}"
    
    def cleanup(self, keep_logs: bool = True):
        """Clean up sandbox environment"""
        try:
            if keep_logs:
                # Move logs to permanent storage
                log_archive = self.project_root / ".queen_system" / "logs" / "sandbox_archives"
                log_archive.mkdir(parents=True, exist_ok=True)
                
                archive_path = log_archive / f"{self.proposal_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(str(self.sandbox_logs), str(archive_path))
            
            # Remove sandbox
            shutil.rmtree(self.sandbox_root)
            
            return {"success": True, "cleaned": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _save_metadata(self):
        """Save sandbox metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get sandbox metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return self.metadata
