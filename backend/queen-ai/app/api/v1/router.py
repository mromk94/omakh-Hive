from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router

# Create the main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health_router, prefix="/health", tags=["health"])

# This is the main router that will be imported by the application
router = APIRouter()
router.include_router(api_router, prefix="/api/v1")
