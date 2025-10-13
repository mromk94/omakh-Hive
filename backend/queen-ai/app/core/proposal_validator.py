"""
Proposal Validator - Validates code proposals before sandbox deployment
Prevents broken proposals from wasting testing resources
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import structlog

logger = structlog.get_logger(__name__)


class ProposalValidator:
    """
    Validates code proposals before they're deployed to sandbox
    Checks: file paths, syntax, imports, dependencies
    """
    
    def __init__(self, project_root: Optional[Path] = None, installed_packages: Optional[Dict[str, str]] = None):
        if project_root is None:
            current_file = Path(__file__).resolve()
            self.project_root = current_file.parent.parent.parent.parent.parent
        else:
            self.project_root = Path(project_root)
        
        self.backend_dir = self.project_root / "backend" / "queen-ai"
        self.frontend_dir = self.project_root / "omk-frontend"
        self.installed_packages = installed_packages or self._load_packages()
        
        logger.info("ProposalValidator initialized", 
                   root=str(self.project_root),
                   packages=len(self.installed_packages))
    
    def _load_packages(self) -> Dict[str, str]:
        """Load installed packages from requirements.txt"""
        packages = {}
        requirements_file = self.backend_dir / "requirements.txt"
        
        if requirements_file.exists():
            for line in requirements_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    match = re.match(r'([a-zA-Z0-9\-_]+)', line)
                    if match:
                        packages[match.group(1).lower()] = "installed"
        
        # Add standard library packages
        stdlib = ['asyncio', 'json', 'os', 'sys', 're', 'datetime', 'typing', 'pathlib']
        for pkg in stdlib:
            packages[pkg] = "stdlib"
        
        return packages
    
    def validate_proposal(self, proposal_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a complete proposal
        
        Args:
            proposal_data: Proposal data with files_to_modify
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        logger.info("🔍 Validating proposal", title=proposal_data.get('title'))
        
        errors = []
        warnings = []
        
        files_to_modify = proposal_data.get('files_to_modify', [])
        
        if not files_to_modify:
            errors.append("No files to modify - proposal is empty")
            return False, errors, warnings
        
        for i, file_data in enumerate(files_to_modify):
            file_errors, file_warnings = self._validate_file(file_data, i)
            errors.extend(file_errors)
            warnings.extend(file_warnings)
        
        is_valid = len(errors) == 0
        
        if is_valid:
            logger.info("✅ Proposal validation passed", 
                       files=len(files_to_modify),
                       warnings=len(warnings))
        else:
            logger.warning("❌ Proposal validation failed", 
                          errors=len(errors),
                          warnings=len(warnings))
        
        return is_valid, errors, warnings
    
    def _validate_file(self, file_data: Dict[str, Any], index: int) -> Tuple[List[str], List[str]]:
        """Validate a single file in the proposal"""
        errors = []
        warnings = []
        
        path = file_data.get('path', '')
        code = file_data.get('code', '')
        
        # Validation 1: Path must exist
        if not path or path == "unknown":
            errors.append(f"File {index}: Invalid path '{path}'")
            return errors, warnings
        
        # Validation 2: Path must be valid format
        if not self._is_valid_path(path):
            errors.append(f"File {index} ({path}): Path format invalid")
        
        # Validation 3: Code must not be empty
        if not code or not code.strip():
            errors.append(f"File {index} ({path}): Code is empty")
            return errors, warnings
        
        # Validation 4: For Python files, check syntax
        if path.endswith('.py'):
            syntax_errors = self._check_python_syntax(code, path)
            errors.extend(syntax_errors)
            
            # Validation 5: Check imports
            if not syntax_errors:  # Only if syntax is valid
                import_errors, import_warnings = self._check_imports(code, path)
                errors.extend(import_errors)
                warnings.extend(import_warnings)
            
            # Validation 6: Check async/await consistency
            async_warnings = self._check_async_patterns(code, path)
            warnings.extend(async_warnings)
        
        # Validation 7: For TypeScript files, basic checks
        elif path.endswith(('.ts', '.tsx')):
            if 'import' in code and not re.search(r'import .+ from ["\'].+["\']', code):
                warnings.append(f"File {path}: Check import syntax")
        
        return errors, warnings
    
    def _is_valid_path(self, path: str) -> bool:
        """Check if path format is valid"""
        # Must be relative path
        if path.startswith('/'):
            return False
        
        # Must not have .. (no directory traversal)
        if '..' in path:
            return False
        
        # Must have valid extension
        valid_extensions = ['.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.yaml', '.yml', '.txt', '.md']
        if not any(path.endswith(ext) for ext in valid_extensions):
            return False
        
        return True
    
    def _check_python_syntax(self, code: str, path: str) -> List[str]:
        """Check Python code for syntax errors"""
        errors = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"File {path}: Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"File {path}: Parse error: {str(e)}")
        
        return errors
    
    def _check_imports(self, code: str, path: str) -> Tuple[List[str], List[str]]:
        """Check if all imports are available"""
        errors = []
        warnings = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        package = alias.name.split('.')[0]
                        if not self._is_package_available(package):
                            errors.append(
                                f"File {path}: Import '{alias.name}' - package '{package}' not installed"
                            )
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        package = node.module.split('.')[0]
                        
                        # Special case: check for common mistakes
                        if package == 'redis' and node.module == 'redis':
                            # Check if importing asyncio version
                            imported_names = [a.name for a in node.names]
                            if 'Redis' in imported_names or 'ConnectionPool' in imported_names:
                                warnings.append(
                                    f"File {path}: Consider using 'from redis.asyncio import' for async support"
                                )
                        
                        if not self._is_package_available(package):
                            errors.append(
                                f"File {path}: Import from '{node.module}' - package '{package}' not installed"
                            )
        
        except Exception as e:
            # If we can't parse, it was already caught in syntax check
            pass
        
        return errors, warnings
    
    def _is_package_available(self, package: str) -> bool:
        """Check if a package is available (installed or stdlib)"""
        package_lower = package.lower()
        
        # Check installed packages
        if package_lower in self.installed_packages:
            return True
        
        # Check if it's an app import
        if package == 'app':
            return True
        
        # Common packages that might not be in requirements.txt
        common_packages = [
            'fastapi', 'pydantic', 'sqlalchemy', 'redis', 'structlog',
            'uvicorn', 'anthropic', 'openai', 'google', 'web3'
        ]
        
        return package_lower in common_packages
    
    def _check_async_patterns(self, code: str, path: str) -> List[str]:
        """Check for common async/await issues"""
        warnings = []
        
        try:
            tree = ast.parse(code)
            
            # Find async functions
            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef):
                    # Check if function has any await calls
                    has_await = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.Await):
                            has_await = True
                            break
                    
                    if not has_await:
                        warnings.append(
                            f"File {path}: Async function '{node.name}' has no await calls - consider making it sync"
                        )
                
                # Check for blocking calls in async context
                elif isinstance(node, ast.FunctionDef):
                    # Look for blocking operations
                    func_code = ast.unparse(node) if hasattr(ast, 'unparse') else ''
                    if 'sleep(' in func_code and 'time.sleep' in func_code:
                        warnings.append(
                            f"File {path}: Using time.sleep() - use asyncio.sleep() in async code"
                        )
        
        except Exception:
            pass
        
        return warnings
    
    def validate_and_fix(self, proposal_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Validate proposal and attempt auto-fixes for common issues
        
        Returns:
            Tuple of (is_valid, fixed_proposal_data, messages)
        """
        is_valid, errors, warnings = self.validate_proposal(proposal_data)
        
        if is_valid:
            return True, proposal_data, warnings
        
        # Attempt auto-fixes
        fixed_data = proposal_data.copy()
        messages = []
        
        # Fix 1: Remove files with empty code
        original_files = fixed_data.get('files_to_modify', [])
        fixed_files = [
            f for f in original_files 
            if f.get('code') and f.get('code').strip()
        ]
        
        if len(fixed_files) < len(original_files):
            messages.append(f"Auto-fixed: Removed {len(original_files) - len(fixed_files)} empty files")
            fixed_data['files_to_modify'] = fixed_files
        
        # Fix 2: Correct common import mistakes
        for file_data in fixed_data.get('files_to_modify', []):
            if file_data.get('path', '').endswith('.py'):
                original_code = file_data['code']
                fixed_code = self._fix_common_imports(original_code)
                
                if fixed_code != original_code:
                    file_data['code'] = fixed_code
                    messages.append(f"Auto-fixed: Corrected imports in {file_data['path']}")
        
        # Re-validate after fixes
        is_valid, errors, warnings = self.validate_proposal(fixed_data)
        
        all_messages = messages + warnings
        if errors:
            all_messages.extend([f"ERROR: {e}" for e in errors])
        
        return is_valid, fixed_data, all_messages
    
    def _fix_common_imports(self, code: str) -> str:
        """Fix common import mistakes"""
        fixed = code
        
        # Fix 1: redis -> redis.asyncio for async context
        if 'from redis import' in fixed and ('Redis' in fixed or 'ConnectionPool' in fixed):
            fixed = fixed.replace('from redis import', 'from redis.asyncio import')
        
        # Fix 2: Add missing asyncio import if using await
        if 'await ' in fixed and 'import asyncio' not in fixed:
            # Add at top after other imports
            lines = fixed.split('\n')
            import_index = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_index = i + 1
            
            if import_index > 0:
                lines.insert(import_index, 'import asyncio')
                fixed = '\n'.join(lines)
        
        return fixed
