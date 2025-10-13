from fastapi import APIRouter

# Create a router for health check endpoints
router = APIRouter()

@router.get("/")
async def health_check():
    """Health check endpoint for the API."""
    return {
        "status": "healthy",
        "service": "queen-ai",
        "version": "0.1.0"
    }
