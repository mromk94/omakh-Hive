"""
Health and Readiness Endpoints

Supports Cloud Run and GKE auto-scaling by:
- /health - Liveness probe (is instance running?)
- /ready - Readiness probe (should receive traffic?)

During graceful shutdown, /ready returns 503 to stop new traffic
while /health still returns 200 to prevent container restart.
"""
from fastapi import APIRouter, Response, status
from typing import Dict, Any
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Liveness probe endpoint
    
    Returns 200 as long as the instance is running.
    Used by Cloud Run/GKE to detect if container is alive.
    
    If this returns non-200, container will be restarted.
    """
    return {
        "status": "healthy",
        "service": "omk-queen-ai"
    }


@router.get("/ready")
async def readiness_check(response: Response) -> Dict[str, Any]:
    """
    Readiness probe endpoint
    
    Returns:
    - 200: Instance is ready to receive traffic
    - 503: Instance is shutting down (stop sending new requests)
    
    Used by Cloud Run/GKE load balancer to determine
    if instance should receive new requests.
    """
    try:
        from app.core.stateless_architecture import stateless_manager
        
        # Check if instance is shutting down
        if stateless_manager.is_shutting_down():
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {
                "status": "shutting_down",
                "message": "Instance is gracefully shutting down"
            }
        
        # Check critical components
        health_status = await _check_components()
        
        if not health_status["healthy"]:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {
                "status": "degraded",
                "components": health_status["components"]
            }
        
        return {
            "status": "ready",
            "components": health_status["components"]
        }
    
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "error": str(e)
        }


async def _check_components() -> Dict[str, Any]:
    """Check critical component health"""
    components = {}
    healthy = True
    
    # Check database
    try:
        from app.db.base import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        components["database"] = "healthy"
    except Exception as e:
        components["database"] = f"unhealthy: {str(e)}"
        healthy = False
    
    # Check Redis
    try:
        from app.core.redis_message_bus import RedisMessageBus
        
        bus = RedisMessageBus()
        await bus.initialize()
        
        if bus.initialized:
            components["redis"] = "healthy"
        else:
            components["redis"] = "in-memory mode"
    except Exception as e:
        components["redis"] = f"unavailable: {str(e)}"
    
    return {
        "healthy": healthy,
        "components": components
    }


@router.get("/startup")
async def startup_probe() -> Dict[str, Any]:
    """
    Startup probe endpoint (GKE)
    
    Returns 200 once instance is fully initialized and ready.
    Used by GKE to wait for slow-starting containers.
    """
    try:
        # Check if startup is complete
        from app.core.stateless_architecture import stateless_manager
        
        return {
            "status": "started",
            "instance_id": stateless_manager.instance_id,
            "startup_time": stateless_manager.startup_time.isoformat()
        }
    
    except Exception as e:
        return {
            "status": "starting",
            "message": "Instance still initializing"
        }
