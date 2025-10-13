"""
Codebase Navigator for Queen AI

Allows Claude/Queen to navigate and understand the entire codebase
by indexing files, functions, classes, and finding code by description.
"""

import os
import ast
import re
import structlog
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from datetime import datetime
import json

logger = structlog.get_logger(__name__)


class CodebaseNavigator:
    """
    Navigate and search the codebase intelligently
    
    Features:
    - Index all Python and TypeScript files
    - Find code by natural language description
    - Locate potential bug locations
    - Track file dependencies
    """
    
    def __init__(self, project_root: Optional[str] = None):
        # Auto-detect project root
        if project_root is None:
            current_file = Path(__file__).resolve()
            # Navigate up to find project root
            self.project_root = current_file.parent.parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.index_file = self.project_root / ".queen_system" / "codebase_index.json"
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.index: Dict[str, Any] = {
            "files": {},
            "functions": {},
            "classes": {},
            "keywords": {},
            "indexed_at": None
        }
        
        # Load existing index
        self._load_index()
    
    def _load_index(self):
        """Load existing index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
                logger.info(f"Loaded codebase index: {len(self.index.get('files', {}))} files")
            except Exception as e:
                logger.error(f"Failed to load index: {e}")
    
    def _save_index(self):
        """Save index to disk"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
            logger.info("Codebase index saved")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    async def index_project(self, force: bool = False) -> Dict[str, Any]:
        """
        Index entire project codebase
        
        Args:
            force: Force re-index even if recently indexed
        
        Returns:
            Index statistics
        """
        # Check if recently indexed
        if not force and self.index.get("indexed_at"):
            indexed_time = datetime.fromisoformat(self.index["indexed_at"])
            age_hours = (datetime.utcnow() - indexed_time).total_seconds() / 3600
            if age_hours < 24:
                logger.info(f"Using cached index (age: {age_hours:.1f} hours)")
                return {
                    "cached": True,
                    "age_hours": age_hours,
                    "files": len(self.index["files"])
                }
        
        logger.info(f"Indexing codebase at {self.project_root}")
        
        # Reset index
        self.index = {
            "files": {},
            "functions": {},
            "classes": {},
            "keywords": {},
            "indexed_at": datetime.utcnow().isoformat()
        }
        
        # Index directories
        backend_dir = self.project_root / "backend" / "queen-ai"
        frontend_dir = self.project_root / "omk-frontend"
        
        stats = {
            "python_files": 0,
            "typescript_files": 0,
            "functions": 0,
            "classes": 0,
            "total_lines": 0
        }
        
        # Index Python files (backend)
        if backend_dir.exists():
            for py_file in backend_dir.rglob("*.py"):
                if "venv" in str(py_file) or "__pycache__" in str(py_file):
                    continue
                await self._index_python_file(py_file, stats)
        
        # Index TypeScript files (frontend)
        if frontend_dir.exists():
            for ts_file in frontend_dir.rglob("*.tsx"):
                if "node_modules" in str(ts_file) or ".next" in str(ts_file):
                    continue
                await self._index_typescript_file(ts_file, stats)
            
            for ts_file in frontend_dir.rglob("*.ts"):
                if "node_modules" in str(ts_file) or ".next" in str(ts_file):
                    continue
                await self._index_typescript_file(ts_file, stats)
        
        # Save index
        self._save_index()
        
        logger.info(
            "Indexing complete",
            python_files=stats["python_files"],
            typescript_files=stats["typescript_files"],
            functions=stats["functions"],
            classes=stats["classes"]
        )
        
        return stats
    
    async def _index_python_file(self, file_path: Path, stats: Dict):
        """Index a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                logger.warning(f"Syntax error in {file_path}")
                return
            
            rel_path = str(file_path.relative_to(self.project_root))
            
            # Extract functions and classes
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args]
                    }
                    functions.append(func_info)
                    
                    # Add to global function index
                    self.index["functions"][f"{rel_path}::{node.name}"] = {
                        "file": rel_path,
                        "line": node.lineno,
                        "type": "function"
                    }
                    stats["functions"] += 1
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line": node.lineno,
                        "docstring": ast.get_docstring(node),
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    }
                    classes.append(class_info)
                    
                    # Add to global class index
                    self.index["classes"][f"{rel_path}::{node.name}"] = {
                        "file": rel_path,
                        "line": node.lineno,
                        "type": "class"
                    }
                    stats["classes"] += 1
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # Extract keywords from content
            keywords = self._extract_keywords(content)
            
            # Store file info
            self.index["files"][rel_path] = {
                "type": "python",
                "size": len(content),
                "lines": content.count('\n') + 1,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "keywords": keywords
            }
            
            # Add keywords to global keyword index
            for keyword in keywords:
                if keyword not in self.index["keywords"]:
                    self.index["keywords"][keyword] = []
                self.index["keywords"][keyword].append(rel_path)
            
            stats["python_files"] += 1
            stats["total_lines"] += content.count('\n') + 1
        
        except Exception as e:
            logger.error(f"Failed to index {file_path}: {e}")
    
    async def _index_typescript_file(self, file_path: Path, stats: Dict):
        """Index a TypeScript/TSX file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rel_path = str(file_path.relative_to(self.project_root))
            
            # Extract functions (basic regex matching)
            function_pattern = r'(?:async\s+)?(?:function\s+|const\s+|export\s+(?:default\s+)?function\s+)(\w+)\s*[=\(]'
            functions = []
            for match in re.finditer(function_pattern, content):
                func_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                functions.append({
                    "name": func_name,
                    "line": line_num
                })
                
                self.index["functions"][f"{rel_path}::{func_name}"] = {
                    "file": rel_path,
                    "line": line_num,
                    "type": "function"
                }
                stats["functions"] += 1
            
            # Extract components (React)
            component_pattern = r'(?:export\s+default\s+)?(?:function|const)\s+([A-Z]\w+)\s*[=\(]'
            classes = []
            for match in re.finditer(component_pattern, content):
                comp_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                classes.append({
                    "name": comp_name,
                    "line": line_num,
                    "type": "component"
                })
                
                self.index["classes"][f"{rel_path}::{comp_name}"] = {
                    "file": rel_path,
                    "line": line_num,
                    "type": "component"
                }
                stats["classes"] += 1
            
            # Extract imports
            import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
            imports = [match.group(1) for match in re.finditer(import_pattern, content)]
            
            # Extract keywords
            keywords = self._extract_keywords(content)
            
            # Store file info
            self.index["files"][rel_path] = {
                "type": "typescript",
                "size": len(content),
                "lines": content.count('\n') + 1,
                "functions": functions,
                "components": classes,
                "imports": imports,
                "keywords": keywords
            }
            
            # Add keywords to global keyword index
            for keyword in keywords:
                if keyword not in self.index["keywords"]:
                    self.index["keywords"][keyword] = []
                self.index["keywords"][keyword].append(rel_path)
            
            stats["typescript_files"] += 1
            stats["total_lines"] += content.count('\n') + 1
        
        except Exception as e:
            logger.error(f"Failed to index {file_path}: {e}")
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from code"""
        # Common technical keywords
        keywords = []
        
        keyword_patterns = [
            r'\bpassword\b',
            r'\bauth(?:entication|orization)?\b',
            r'\blogin\b',
            r'\buser\b',
            r'\bwallet\b',
            r'\btransaction\b',
            r'\btoken\b',
            r'\bsecurity\b',
            r'\bvalidation\b',
            r'\berror\b',
            r'\bapi\b',
            r'\bdatabase\b',
            r'\bquery\b'
        ]
        
        for pattern in keyword_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                keywords.append(pattern.strip(r'\b'))
        
        return list(set(keywords))
    
    async def find_by_description(self, description: str) -> List[Dict[str, Any]]:
        """
        Find files/functions matching a natural language description
        
        Example: "password validation logic" → finds auth.py, login.tsx, etc.
        """
        description_lower = description.lower()
        
        # Extract keywords from description
        words = re.findall(r'\w+', description_lower)
        
        # Search in keywords index
        matching_files = []
        seen_files = set()
        
        for word in words:
            if word in self.index["keywords"]:
                for file_path in self.index["keywords"][word]:
                    if file_path not in seen_files:
                        seen_files.add(file_path)
                        file_info = self.index["files"].get(file_path, {})
                        matching_files.append({
                            "file": file_path,
                            "relevance": self._calculate_relevance(file_path, words),
                            "type": file_info.get("type"),
                            "lines": file_info.get("lines"),
                            "functions": len(file_info.get("functions", [])),
                            "classes": len(file_info.get("classes", []))
                        })
        
        # Sort by relevance
        matching_files.sort(key=lambda x: x["relevance"], reverse=True)
        
        return matching_files[:20]  # Top 20 matches
    
    def _calculate_relevance(self, file_path: str, search_words: List[str]) -> float:
        """Calculate relevance score for a file"""
        file_info = self.index["files"].get(file_path, {})
        file_keywords = file_info.get("keywords", [])
        
        # Count keyword matches
        matches = sum(1 for word in search_words if word in file_keywords)
        
        # Bonus for file name matches
        file_name = file_path.lower()
        name_matches = sum(1 for word in search_words if word in file_name)
        
        return matches * 10 + name_matches * 5
    
    async def find_bug_location(self, bug_description: str) -> List[Dict[str, Any]]:
        """
        Suggest files that might contain a bug
        
        Example: "wrong password error even with correct password"
        → Suggests: auth.py, login.tsx, password_validator.py
        """
        # This is similar to find_by_description but prioritizes certain patterns
        results = await self.find_by_description(bug_description)
        
        # Prioritize files with "auth", "password", "login" etc.
        priority_keywords = ["auth", "password", "login", "validation", "verify"]
        
        for result in results:
            file_path = result["file"]
            for keyword in priority_keywords:
                if keyword in file_path.lower():
                    result["relevance"] += 20
        
        # Re-sort by updated relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        return results[:10]  # Top 10 likely locations
    
    async def get_file_content(self, file_path: str) -> Optional[str]:
        """Get content of a specific file"""
        try:
            full_path = self.project_root / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return None
    
    async def find_related_files(self, file_path: str) -> List[str]:
        """Find files that import or are imported by this file"""
        related = []
        
        file_info = self.index["files"].get(file_path)
        if not file_info:
            return related
        
        imports = file_info.get("imports", [])
        
        # Find files that match imports
        for other_path, other_info in self.index["files"].items():
            if other_path == file_path:
                continue
            
            # Check if this file imports our target file
            for imp in other_info.get("imports", []):
                if file_path.replace("/", ".").replace(".py", "") in imp:
                    related.append(other_path)
        
        return related
    
    async def get_function_signature(self, file_path: str, function_name: str) -> Optional[Dict]:
        """Get signature and docstring of a specific function"""
        file_info = self.index["files"].get(file_path)
        if not file_info:
            return None
        
        for func in file_info.get("functions", []):
            if func["name"] == function_name:
                return func
        
        return None
