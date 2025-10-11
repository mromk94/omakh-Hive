"""
System Knowledge Base - Persistent Memory for Project Structure

Claude/Queen AI uses this to remember project details without repeatedly
reviewing the codebase structure.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json
import structlog

logger = structlog.get_logger(__name__)


class SystemKnowledge:
    """
    Persistent knowledge base for project structure and patterns
    
    Purpose:
    - Remember project structure (directories, ports, patterns)
    - Remember architectural decisions
    - Remember integration points
    - Learn from past implementations
    - Avoid repeated codebase reviews
    
    Updates automatically when:
    - Claude performs codebase review
    - New features are implemented
    - Patterns change
    - Admin provides corrections
    """
    
    def __init__(self, knowledge_file: Optional[Path] = None):
        self.knowledge_file = knowledge_file or Path("data/system_knowledge.json")
        self.knowledge: Dict[str, Any] = {}
        self._load_knowledge()
    
    def _load_knowledge(self):
        """Load knowledge base from disk"""
        try:
            if self.knowledge_file.exists():
                with open(self.knowledge_file, "r") as f:
                    self.knowledge = json.load(f)
                logger.info("System knowledge loaded", version=self.knowledge.get("version", "unknown"))
            else:
                # Initialize with OMK Hive defaults
                self._initialize_omk_knowledge()
                logger.info("System knowledge initialized with OMK Hive defaults")
        except Exception as e:
            logger.error("Failed to load system knowledge", error=str(e))
            self._initialize_omk_knowledge()
    
    def _initialize_omk_knowledge(self):
        """Initialize with OMK Hive project knowledge"""
        self.knowledge = {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "project_name": "OMK Hive",
            
            # Project Structure
            "structure": {
                "frontend": {
                    "directory": "omk-frontend",
                    "framework": "Next.js 14",
                    "port": 3001,
                    "package_manager": "npm",
                    "key_directories": {
                        "app": "omk-frontend/app",
                        "components": "omk-frontend/components",
                        "kingdom_admin": "omk-frontend/app/kingdom",
                        "kingdom_components": "omk-frontend/app/kingdom/components"
                    }
                },
                "backend": {
                    "directory": "backend/queen-ai",
                    "framework": "FastAPI",
                    "port": 8001,
                    "python_version": "3.13",
                    "key_directories": {
                        "api": "backend/queen-ai/app/api/v1",
                        "bees": "backend/queen-ai/app/bees",
                        "core": "backend/queen-ai/app/core",
                        "security": "backend/queen-ai/app/core/security",
                        "integrations": "backend/queen-ai/app/integrations",
                        "learning": "backend/queen-ai/app/learning"
                    }
                }
            },
            
            # Theme & Styling
            "theme": {
                "primary_color": "yellow-500",
                "background": "black/gray-900 gradient",
                "card_style": "bg-gray-900/50 border border-gray-700 rounded-xl",
                "text_primary": "white",
                "text_secondary": "gray-400",
                "accent_gradients": {
                    "yellow": "from-yellow-900/20 to-yellow-800/10 border-yellow-500/30",
                    "green": "from-green-900/20 to-green-800/10 border-green-500/30",
                    "blue": "from-blue-900/20 to-blue-800/10 border-blue-500/30",
                    "purple": "from-purple-900/20 to-purple-800/10 border-purple-500/30"
                },
                "icon_library": "lucide-react",
                "animation_library": "framer-motion"
            },
            
            # API Endpoints
            "endpoints": {
                "backend_url": "http://localhost:8001",
                "api_prefix": "/api/v1",
                "key_endpoints": {
                    "health": "/api/v1/health",
                    "queen_dev": "/api/v1/queen-dev",
                    "admin": "/api/v1/admin",
                    "admin_claude": "/api/v1/admin/claude",
                    "teacher_bee": "/api/v1/teacher-bee",
                    "frontend": "/api/v1/frontend"
                }
            },
            
            # Patterns & Conventions
            "patterns": {
                "kingdom_admin": {
                    "location": "omk-frontend/app/kingdom",
                    "tab_integration": {
                        "tabs_array": "In page.tsx, add to tabs array",
                        "component_loader": "Create function like ClaudeAnalysisTab()",
                        "component_location": "omk-frontend/app/kingdom/components/",
                        "import_pattern": "require('./components/ComponentName').default"
                    },
                    "navigation": {
                        "categories": ["main", "queen", "manage", "system"],
                        "structure": "Dropdown by category"
                    }
                },
                "backend_api": {
                    "router_pattern": "APIRouter with prefix and tags",
                    "security_integration": "get_security_bee() for validation",
                    "error_handling": "HTTPException with proper status codes",
                    "logging": "structlog for structured logging"
                },
                "component_style": {
                    "typescript": "Prefer functional components with hooks",
                    "imports": "Group: React → UI libs → local components",
                    "state": "useState for local, context for shared",
                    "styling": "Tailwind classes, match existing patterns"
                }
            },
            
            # Security System
            "security": {
                "components": [
                    "PromptProtectionGate",
                    "OutputFilter",
                    "SecurityContextManager",
                    "ImageContentScanner",
                    "EnhancedSecurityBee"
                ],
                "integration_points": 17,
                "coverage": "100% of LLM endpoints",
                "gates": {
                    "input_validation": "validate_llm_input",
                    "output_filtering": "filter_llm_output",
                    "image_scanning": "scan_image"
                }
            },
            
            # Bees (Specialized Agents)
            "bees": {
                "total": 22,
                "list": [
                    "MathsBee", "SecurityBee", "DataBee", "BlockchainBee", "TreasuryBee",
                    "LogicBee", "PatternBee", "TeacherBee", "LiquiditySentinelBee",
                    "StakeBotBee", "TokenizationBee", "MonitoringBee", "PrivateSaleBee",
                    "GovernanceBee", "VisualizationBee", "BridgeBee", "DataPipelineBee",
                    "OnboardingBee", "PurchaseBee", "UserExperienceBee",
                    "EnhancedSecurityBee", "BaseBee"
                ],
                "manager": "backend/queen-ai/app/bees/manager.py",
                "base_class": "backend/queen-ai/app/bees/base.py"
            },
            
            # Common Issues & Solutions
            "known_issues": {
                "wrong_port": {
                    "issue": "Using port 3000 instead of 3001",
                    "solution": "Always check omk-frontend/package.json for actual port",
                    "correct_value": 3001
                },
                "wrong_directory": {
                    "issue": "Using frontend/ instead of omk-frontend/",
                    "solution": "Always verify actual directory structure",
                    "correct_value": "omk-frontend/"
                },
                "parallel_systems": {
                    "issue": "Creating new dashboard instead of integrating",
                    "solution": "Always find and extend existing systems (Kingdom admin)",
                    "correct_approach": "Integrate into omk-frontend/app/kingdom/"
                },
                "hardcoded_data": {
                    "issue": "Returning static data instead of reading files",
                    "solution": "Always implement actual file I/O or database queries",
                    "correct_approach": "Read from JSON files or database"
                }
            },
            
            # Learning History
            "learning_history": {
                "implementations": [],
                "corrections": [],
                "patterns_discovered": []
            },
            
            # Metadata
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_reviewed": datetime.now().isoformat(),
                "review_count": 0,
                "implementation_count": 0
            }
        }
        self._save_knowledge()
    
    def _save_knowledge(self):
        """Save knowledge base to disk"""
        try:
            self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)
            self.knowledge["last_updated"] = datetime.now().isoformat()
            
            with open(self.knowledge_file, "w") as f:
                json.dump(self.knowledge, f, indent=2, default=str)
            
            logger.debug("System knowledge saved")
        except Exception as e:
            logger.error("Failed to save system knowledge", error=str(e))
    
    def get_project_structure(self) -> Dict[str, Any]:
        """Get complete project structure"""
        return self.knowledge.get("structure", {})
    
    def get_frontend_info(self) -> Dict[str, Any]:
        """Get frontend-specific information"""
        return self.knowledge.get("structure", {}).get("frontend", {})
    
    def get_backend_info(self) -> Dict[str, Any]:
        """Get backend-specific information"""
        return self.knowledge.get("structure", {}).get("backend", {})
    
    def get_theme(self) -> Dict[str, Any]:
        """Get theme and styling information"""
        return self.knowledge.get("theme", {})
    
    def get_patterns(self) -> Dict[str, Any]:
        """Get implementation patterns"""
        return self.knowledge.get("patterns", {})
    
    def get_known_issues(self) -> Dict[str, Any]:
        """Get known issues and their solutions"""
        return self.knowledge.get("known_issues", {})
    
    def add_implementation(self, implementation: Dict[str, Any]):
        """Record a new implementation"""
        if "learning_history" not in self.knowledge:
            self.knowledge["learning_history"] = {"implementations": [], "corrections": [], "patterns_discovered": []}
        
        self.knowledge["learning_history"]["implementations"].append({
            "timestamp": datetime.now().isoformat(),
            **implementation
        })
        
        self.knowledge["metadata"]["implementation_count"] = \
            self.knowledge["metadata"].get("implementation_count", 0) + 1
        
        self._save_knowledge()
        logger.info("Implementation recorded", title=implementation.get("title"))
    
    def add_correction(self, correction: Dict[str, Any]):
        """Record a correction/lesson learned"""
        if "learning_history" not in self.knowledge:
            self.knowledge["learning_history"] = {"implementations": [], "corrections": [], "patterns_discovered": []}
        
        self.knowledge["learning_history"]["corrections"].append({
            "timestamp": datetime.now().isoformat(),
            **correction
        })
        
        self._save_knowledge()
        logger.info("Correction recorded", issue=correction.get("issue"))
    
    def add_pattern(self, pattern: Dict[str, Any]):
        """Record a new pattern discovered"""
        if "learning_history" not in self.knowledge:
            self.knowledge["learning_history"] = {"implementations": [], "corrections": [], "patterns_discovered": []}
        
        self.knowledge["learning_history"]["patterns_discovered"].append({
            "timestamp": datetime.now().isoformat(),
            **pattern
        })
        
        self._save_knowledge()
        logger.info("Pattern recorded", name=pattern.get("name"))
    
    def update_structure(self, path: str, value: Any):
        """Update specific knowledge path"""
        keys = path.split(".")
        current = self.knowledge
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        self._save_knowledge()
    
    def get_context_for_claude(self) -> str:
        """Generate context string for Claude's system prompt"""
        structure = self.knowledge.get("structure", {})
        theme = self.knowledge.get("theme", {})
        patterns = self.knowledge.get("patterns", {})
        known_issues = self.knowledge.get("known_issues", {})
        
        context = f"""# PERSISTENT PROJECT KNOWLEDGE (Memorized)

You have persistent memory of the OMK Hive project structure. Use this knowledge
instead of repeatedly reviewing the codebase.

## Project Structure (MEMORIZED)
- Frontend: {structure.get('frontend', {}).get('directory', 'omk-frontend')}
  - Framework: {structure.get('frontend', {}).get('framework', 'Next.js 14')}
  - Port: {structure.get('frontend', {}).get('port', 3001)} (ALWAYS USE THIS PORT!)
  - Admin Dashboard: omk-frontend/app/kingdom/
  - Components: omk-frontend/app/kingdom/components/

- Backend: {structure.get('backend', {}).get('directory', 'backend/queen-ai')}
  - Framework: {structure.get('backend', {}).get('framework', 'FastAPI')}
  - Port: {structure.get('backend', {}).get('port', 8001)}
  - API Routes: backend/queen-ai/app/api/v1/
  - Security: backend/queen-ai/app/core/security/

## Theme (MEMORIZED)
- Primary: {theme.get('primary_color', 'yellow-500')} (yellow/black theme)
- Icons: {theme.get('icon_library', 'lucide-react')}
- Animations: {theme.get('animation_library', 'framer-motion')}
- Card Style: {theme.get('card_style', 'bg-gray-900/50 border border-gray-700 rounded-xl')}

## Integration Patterns (MEMORIZED)
Kingdom Admin Tab Integration:
1. Add to tabs array in omk-frontend/app/kingdom/page.tsx
2. Create component in omk-frontend/app/kingdom/components/
3. Create loader function: ClaudeAnalysisTab()
4. Use: require('./components/ComponentName').default

Backend API Pattern:
1. Create router in backend/queen-ai/app/api/v1/
2. Register in backend/queen-ai/app/api/v1/router.py
3. Use get_security_bee() for validation
4. Use structlog for logging

## Known Issues (NEVER REPEAT):
{self._format_known_issues(known_issues)}

## Last Updated
{self.knowledge.get('last_updated', 'Unknown')}

You KNOW this information. Don't review it again unless explicitly asked to update your knowledge.
"""
        return context
    
    def _format_known_issues(self, known_issues: Dict[str, Any]) -> str:
        """Format known issues for context"""
        lines = []
        for issue_key, issue_data in known_issues.items():
            lines.append(f"- {issue_data.get('issue', issue_key)}")
            lines.append(f"  ✓ Solution: {issue_data.get('solution', 'N/A')}")
        return "\n".join(lines) if lines else "None"
    
    def mark_reviewed(self):
        """Mark knowledge as reviewed (increments review count)"""
        self.knowledge["metadata"]["review_count"] = \
            self.knowledge["metadata"].get("review_count", 0) + 1
        self.knowledge["metadata"]["last_reviewed"] = datetime.now().isoformat()
        self._save_knowledge()


# Global instance
system_knowledge = SystemKnowledge()
