from fastapi import APIRouter
from app.api.v1.endpoints import health
from app.api.v1.endpoints import teacher_bee
from app.api.v1 import queen
from app.api.v1 import frontend
from app.api.v1 import admin
from app.api.v1 import queen_dev
from app.api.v1 import admin_claude
from app.api.v1 import market
from app.api.v1 import proposal_auto_fix

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(queen.router, prefix="/queen", tags=["queen"])
api_router.include_router(queen_dev.router, prefix="/queen-dev", tags=["queen-development"])
api_router.include_router(frontend.router, tags=["frontend"])
api_router.include_router(teacher_bee.router, prefix="/teacher-bee", tags=["teacher-bee"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(admin_claude.router, tags=["admin-claude"])
api_router.include_router(market.router, tags=["market"])
api_router.include_router(proposal_auto_fix.router, prefix="/admin/proposals", tags=["admin-proposals"])

# This is the main router that will be imported by the application
router = APIRouter()
router.include_router(api_router)
