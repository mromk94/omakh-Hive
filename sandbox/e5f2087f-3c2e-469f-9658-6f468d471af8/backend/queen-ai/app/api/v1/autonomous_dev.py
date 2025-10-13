"""
Autonomous Development API

Endpoints for Queen's autonomous bug fixing and code improvement capabilities
"""

from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

from app.core.autonomous_fixer import AutonomousFixer
from app.core.bug_analyzer import BugAnalyzer
from app.tools.codebase_navigator import CodebaseNavigator
from app.api.v1.admin import verify_admin
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/autonomous", tags=["Autonomous Development"])

# Initialize systems
autonomous_fixer = AutonomousFixer()
bug_analyzer = BugAnalyzer()
codebase_nav = CodebaseNavigator()


# ==================== REQUEST MODELS ====================

class BugReportRequest(BaseModel):
    bug_description: str
    user_context: Optional[Dict[str, Any]] = None
    num_approaches: int = 3
    auto_apply_if_safe: bool = False


class ApproveFixRequest(BaseModel):
    notes: Optional[str] = None


class RejectFixRequest(BaseModel):
    reason: str


class CodeSearchRequest(BaseModel):
    query: str
    limit: int = 20


# ==================== ENDPOINTS ====================

@router.post("/fix-bug")
async def autonomous_bug_fix(
    request: BugReportRequest,
    background_tasks: BackgroundTasks,
    admin: bool = Depends(verify_admin)
):
    """
    🤖 Autonomous bug fixing
    
    Queen will:
    1. Analyze the bug
    2. Generate 3 fix approaches
    3. Test each in sandbox
    4. Present best fix for approval
    """
    try:
        logger.info(f"Autonomous fix requested: {request.bug_description[:100]}")
        
        # Run fix in background for long-running operation
        fix_task = autonomous_fixer.fix_bug(
            bug_description=request.bug_description,
            admin_id="admin",  # TODO: Get from auth
            user_context=request.user_context,
            num_approaches=request.num_approaches,
            auto_apply_if_safe=request.auto_apply_if_safe
        )
        
        # Wait for result (or use background tasks for async)
        result = await fix_task
        
        return {
            "success": True,
            "message": "Autonomous fix complete" if result.get("success") else "Fix failed",
            **result
        }
    
    except Exception as e:
        logger.error(f"Autonomous fix endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fixes/{fix_id}")
async def get_fix_status(
    fix_id: str,
    admin: bool = Depends(verify_admin)
):
    """
    Get status of an autonomous fix
    """
    fix_info = autonomous_fixer.active_fixes.get(fix_id)
    
    if not fix_info:
        raise HTTPException(status_code=404, detail="Fix not found")
    
    return {
        "success": True,
        "fix": fix_info
    }


@router.get("/fixes")
async def list_active_fixes(
    status: Optional[str] = None,
    admin: bool = Depends(verify_admin)
):
    """
    List all active autonomous fixes
    """
    fixes = list(autonomous_fixer.active_fixes.values())
    
    if status:
        fixes = [f for f in fixes if f.get("status") == status]
    
    return {
        "success": True,
        "count": len(fixes),
        "fixes": fixes
    }


@router.post("/fixes/{fix_id}/approve")
async def approve_fix(
    fix_id: str,
    request: ApproveFixRequest,
    admin: bool = Depends(verify_admin)
):
    """
    ✅ Approve and apply an autonomous fix
    """
    try:
        result = await autonomous_fixer.approve_and_apply(
            fix_id=fix_id,
            approved_by="admin",  # TODO: Get from auth
            notes=request.notes
        )
        
        return {
            "success": result.get("success"),
            "message": "Fix applied successfully" if result.get("success") else "Application failed",
            **result
        }
    
    except Exception as e:
        logger.error(f"Fix approval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fixes/{fix_id}/reject")
async def reject_fix(
    fix_id: str,
    request: RejectFixRequest,
    admin: bool = Depends(verify_admin)
):
    """
    ❌ Reject an autonomous fix
    """
    try:
        result = await autonomous_fixer.reject_fix(
            fix_id=fix_id,
            rejected_by="admin",  # TODO: Get from auth
            reason=request.reason
        )
        
        return {
            "success": True,
            "message": "Fix rejected",
            **result
        }
    
    except Exception as e:
        logger.error(f"Fix rejection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== BUG ANALYSIS ====================

@router.post("/analyze-bug")
async def analyze_bug_report(
    request: BugReportRequest,
    admin: bool = Depends(verify_admin)
):
    """
    🔍 Analyze a bug without fixing it (inspection only)
    """
    try:
        analysis = await bug_analyzer.analyze_bug(
            bug_description=request.bug_description,
            user_context=request.user_context
        )
        
        return {
            "success": True,
            "analysis": analysis
        }
    
    except Exception as e:
        logger.error(f"Bug analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CODEBASE NAVIGATION ====================

@router.post("/index-codebase")
async def index_codebase(
    force: bool = False,
    admin: bool = Depends(verify_admin)
):
    """
    📚 Index the entire codebase for fast searching
    """
    try:
        stats = await codebase_nav.index_project(force=force)
        
        return {
            "success": True,
            "message": "Codebase indexed successfully",
            "stats": stats
        }
    
    except Exception as e:
        logger.error(f"Codebase indexing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search-code")
async def search_codebase(
    request: CodeSearchRequest,
    admin: bool = Depends(verify_admin)
):
    """
    🔎 Search codebase by natural language description
    
    Example: "password validation logic"
    """
    try:
        results = await codebase_nav.find_by_description(request.query)
        
        return {
            "success": True,
            "query": request.query,
            "count": len(results),
            "results": results[:request.limit]
        }
    
    except Exception as e:
        logger.error(f"Code search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_path:path}")
async def get_file_content(
    file_path: str,
    admin: bool = Depends(verify_admin)
):
    """
    📄 Get content of a specific file
    """
    try:
        content = await codebase_nav.get_file_content(file_path)
        
        if content is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "file_path": file_path,
            "content": content,
            "lines": content.count('\n') + 1
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File read error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SYSTEM STATUS ====================

@router.get("/status")
async def get_autonomous_system_status(
    admin: bool = Depends(verify_admin)
):
    """
    📊 Get status of autonomous development system
    """
    try:
        return {
            "success": True,
            "status": {
                "active_fixes": len(autonomous_fixer.active_fixes),
                "fixes_by_status": {
                    "awaiting_approval": len([f for f in autonomous_fixer.active_fixes.values() if f.get("status") == "awaiting_approval"]),
                    "applied": len([f for f in autonomous_fixer.active_fixes.values() if f.get("status") == "applied"]),
                    "rejected": len([f for f in autonomous_fixer.active_fixes.values() if f.get("status") == "rejected"])
                },
                "codebase_indexed": codebase_nav.index.get("indexed_at") is not None,
                "indexed_files": len(codebase_nav.index.get("files", {})),
                "capabilities": {
                    "bug_analysis": True,
                    "autonomous_fixing": True,
                    "sandbox_testing": True,
                    "codebase_navigation": True
                }
            }
        }
    
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
