"""
Codebase Context Builder - Provides rich context to Claude for better code generation
Scans actual project structure, packages, and examples
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class CodebaseContextBuilder:
    """
    Builds comprehensive context about the codebase for Claude
    Includes: file structure, installed packages, code examples, patterns
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            # Auto-detect project root
            current_file = Path(__file__).resolve()
            self.project_root = current_file.parent.parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.backend_dir = self.project_root / "backend" / "queen-ai"
        self.frontend_dir = self.project_root / "omk-frontend"
        
        logger.info("CodebaseContextBuilder initialized", root=str(self.project_root))
    
    def build_context(self, recommendation_type: str = "general") -> Dict[str, Any]:
        """
        Build complete context for Claude based on recommendation type
        
        Args:
            recommendation_type: Type of recommendation (redis, database, security, etc.)
        
        Returns:
            Dict with codebase context
        """
        logger.info(f"🔍 Building codebase context for: {recommendation_type}")
        
        context = {
            "project_structure": self._get_project_structure(),
            "installed_packages": self._get_installed_packages(),
            "import_patterns": self._get_import_patterns(),
            "async_patterns": self._get_async_patterns(),
            "code_examples": self._get_relevant_examples(recommendation_type),
            "validation_rules": self._get_validation_rules()
        }
        
        logger.info("✅ Context built successfully", 
                   packages=len(context["installed_packages"]),
                   examples=len(context["code_examples"]))
        
        return context
    
    def _get_project_structure(self) -> Dict[str, List[str]]:
        """Get actual project directory structure"""
        structure = {
            "backend_dirs": [],
            "frontend_dirs": [],
            "important_files": []
        }
        
        # Backend structure
        if self.backend_dir.exists():
            for path in self.backend_dir.rglob("*"):
                if path.is_dir() and not any(x in str(path) for x in [".venv", "__pycache__", ".git"]):
                    rel_path = str(path.relative_to(self.backend_dir))
                    if rel_path.count("/") <= 3:  # Only top 3 levels
                        structure["backend_dirs"].append(rel_path)
        
        # Frontend structure
        if self.frontend_dir.exists():
            for path in self.frontend_dir.rglob("*"):
                if path.is_dir() and not any(x in str(path) for x in ["node_modules", ".next", ".git"]):
                    rel_path = str(path.relative_to(self.frontend_dir))
                    if rel_path.count("/") <= 3:
                        structure["frontend_dirs"].append(rel_path)
        
        # Important files
        important_patterns = ["main.py", "settings.py", "*.config.js", "package.json", "requirements.txt"]
        for pattern in important_patterns:
            for path in self.project_root.rglob(pattern):
                if ".venv" not in str(path) and "node_modules" not in str(path):
                    structure["important_files"].append(str(path.relative_to(self.project_root)))
        
        return structure
    
    def _get_installed_packages(self) -> Dict[str, str]:
        """Get installed Python packages from requirements.txt"""
        packages = {}
        
        requirements_file = self.backend_dir / "requirements.txt"
        if requirements_file.exists():
            for line in requirements_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    # Parse package==version or package>=version
                    match = re.match(r'([a-zA-Z0-9\-_]+)([><=]+.*)?', line)
                    if match:
                        pkg_name = match.group(1)
                        version = match.group(2) or "latest"
                        packages[pkg_name] = version.strip()
        
        return packages
    
    def _get_import_patterns(self) -> Dict[str, List[str]]:
        """Extract common import patterns from existing code"""
        patterns = {
            "fastapi": [],
            "async": [],
            "database": [],
            "redis": [],
            "common": []
        }
        
        # Scan key files for imports
        key_files = [
            self.backend_dir / "main.py",
            self.backend_dir / "app" / "api" / "v1" / "queen_dev.py",
            self.backend_dir / "app" / "core" / "orchestrator.py"
        ]
        
        for file_path in key_files:
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    tree = ast.parse(content)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                import_line = f"import {alias.name}"
                                self._categorize_import(import_line, patterns)
                        
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                import_line = f"from {node.module} import {', '.join(a.name for a in node.names)}"
                                self._categorize_import(import_line, patterns)
                
                except Exception as e:
                    logger.debug(f"Error parsing {file_path}: {e}")
        
        return patterns
    
    def _categorize_import(self, import_line: str, patterns: Dict[str, List[str]]):
        """Categorize import into appropriate pattern list"""
        if "fastapi" in import_line.lower():
            patterns["fastapi"].append(import_line)
        elif "async" in import_line.lower() or "await" in import_line.lower():
            patterns["async"].append(import_line)
        elif "database" in import_line.lower() or "sqlalchemy" in import_line.lower():
            patterns["database"].append(import_line)
        elif "redis" in import_line.lower():
            patterns["redis"].append(import_line)
        else:
            patterns["common"].append(import_line)
    
    def _get_async_patterns(self) -> List[str]:
        """Get examples of async/await patterns from codebase"""
        patterns = []
        
        # Search for async function definitions
        search_dirs = [
            self.backend_dir / "app" / "api" / "v1",
            self.backend_dir / "app" / "core"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for py_file in search_dir.rglob("*.py"):
                    if "__pycache__" in str(py_file):
                        continue
                    
                    try:
                        content = py_file.read_text()
                        # Find async function definitions
                        async_funcs = re.findall(
                            r'async def \w+\([^)]*\).*?(?=\n(?:async def|\nclass|\nif __name__|$))',
                            content,
                            re.DOTALL
                        )
                        
                        if async_funcs and len(patterns) < 5:  # Limit to 5 examples
                            # Get first few lines of each function
                            for func in async_funcs[:2]:
                                lines = func.split('\n')[:8]  # First 8 lines
                                patterns.append('\n'.join(lines))
                    
                    except Exception as e:
                        logger.debug(f"Error reading {py_file}: {e}")
        
        return patterns[:5]  # Return max 5 examples
    
    def _get_relevant_examples(self, recommendation_type: str) -> List[Dict[str, str]]:
        """Get code examples relevant to the recommendation type"""
        examples = []
        
        # Map recommendation types to example files
        example_mapping = {
            "redis": ["app/core/redis_message_bus.py", "app/core/distributed_lock.py"],
            "database": ["app/database/connection.py", "app/db/models.py"],
            "cache": ["app/core/redis_message_bus.py"],
            "api": ["app/api/v1/queen_dev.py", "app/api/v1/admin.py"],
            "security": ["app/bees/enhanced_security_bee.py"],
            "websocket": ["app/api/v1/websocket.py"]
        }
        
        # Get relevant files for this recommendation type
        relevant_files = example_mapping.get(recommendation_type.lower(), [])
        
        for file_path in relevant_files:
            full_path = self.backend_dir / file_path
            if full_path.exists():
                try:
                    content = full_path.read_text()
                    # Extract key parts (first 30 lines or until first class/function)
                    lines = content.split('\n')
                    
                    # Find first class or significant function
                    code_snippet = []
                    in_code = False
                    for i, line in enumerate(lines):
                        if i > 50:  # Max 50 lines per example
                            break
                        
                        if 'class ' in line or 'async def ' in line or 'def ' in line:
                            in_code = True
                        
                        if in_code:
                            code_snippet.append(line)
                            
                            # Stop at next class/def or after 30 lines
                            if len(code_snippet) > 30:
                                break
                    
                    if code_snippet:
                        examples.append({
                            "file": file_path,
                            "code": '\n'.join(code_snippet)
                        })
                
                except Exception as e:
                    logger.debug(f"Error reading example {file_path}: {e}")
        
        return examples
    
    def _get_validation_rules(self) -> Dict[str, List[str]]:
        """Define validation rules for production-ready code"""
        return {
            "required": [
                "All imports must be from installed packages (see installed_packages)",
                "Use async/await for I/O operations (database, Redis, HTTP)",
                "All file paths must be relative to project root",
                "Use absolute imports (from app.X import Y, not from .X import Y)",
                "Include error handling (try/except) for external calls",
                "Use type hints for function parameters and returns",
                "Follow existing patterns (see code_examples)"
            ],
            "forbidden": [
                "Do not use blocking I/O in async functions",
                "Do not use bare except: (always specify exception type)",
                "Do not hardcode credentials or secrets",
                "Do not create files outside project structure",
                "Do not use synchronous Redis client (use redis.asyncio)",
                "Do not mix tabs and spaces (use 4 spaces)"
            ],
            "recommended": [
                "Use structlog for logging",
                "Follow FastAPI patterns for endpoints",
                "Use Pydantic for data validation",
                "Keep functions under 50 lines",
                "Add docstrings to all public functions",
                "Use meaningful variable names"
            ]
        }
    
    def format_for_claude(self, context: Dict[str, Any]) -> str:
        """Format context into a string for Claude's prompt"""
        
        formatted = "**CODEBASE CONTEXT:**\n\n"
        
        # Project structure
        formatted += "**Project Structure:**\n"
        formatted += f"Backend directories: {', '.join(context['project_structure']['backend_dirs'][:10])}\n"
        formatted += f"Frontend directories: {', '.join(context['project_structure']['frontend_dirs'][:10])}\n\n"
        
        # Installed packages
        formatted += "**Installed Packages:**\n"
        key_packages = ['fastapi', 'redis', 'sqlalchemy', 'pydantic', 'structlog', 'anthropic']
        for pkg in key_packages:
            if pkg in context['installed_packages']:
                formatted += f"- {pkg}{context['installed_packages'][pkg]}\n"
        formatted += "\n"
        
        # Import patterns
        formatted += "**Correct Import Patterns:**\n"
        if context['import_patterns'].get('redis'):
            formatted += "Redis (async): " + context['import_patterns']['redis'][0] + "\n"
        if context['import_patterns'].get('fastapi'):
            formatted += "FastAPI: " + context['import_patterns']['fastapi'][0] + "\n"
        formatted += "\n"
        
        # Async patterns
        if context['async_patterns']:
            formatted += "**Async/Await Pattern Example:**\n```python\n"
            formatted += context['async_patterns'][0][:300]  # First 300 chars
            formatted += "\n```\n\n"
        
        # Code examples
        if context['code_examples']:
            formatted += "**Working Code Example:**\n```python\n"
            formatted += context['code_examples'][0]['code'][:400]  # First 400 chars
            formatted += "\n```\n\n"
        
        # Validation rules
        formatted += "**VALIDATION RULES (MUST FOLLOW):**\n"
        for rule in context['validation_rules']['required'][:5]:
            formatted += f"✅ {rule}\n"
        for rule in context['validation_rules']['forbidden'][:3]:
            formatted += f"❌ {rule}\n"
        
        return formatted
