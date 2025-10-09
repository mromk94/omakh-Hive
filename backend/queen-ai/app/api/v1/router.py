from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.queen import router as queen_router
from app.api.v1.frontend import router as frontend_router

# Create the main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(queen_router, prefix="/queen", tags=["queen"])
api_router.include_router(frontend_router, tags=["frontend"])

# This is the main router that will be imported by the application
router = APIRouter()
router.include_router(api_router)
