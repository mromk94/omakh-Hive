"""
Queen AI - Main Application Entry Point
Integrates with all 16 PRIME2 Ethereum contracts
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.config.settings import settings
from app.config.logging_config import setup_logging, get_logger
from app.core.orchestrator import QueenOrchestrator

# Load environment variables
load_dotenv()

# Setup structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    logger.info("🚀 Starting Queen AI Orchestrator")
    
    # Initialize Queen Orchestrator
    queen = QueenOrchestrator()
    await queen.initialize()
    
    # Store in app state
    app.state.queen = queen
    
    logger.info("✅ Queen AI ready and operational")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Queen AI")
    await queen.shutdown()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="OMK Hive - Queen AI",
        description="Central AI orchestration system for OMK Hive ecosystem",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    from app.api.v1 import router as api_router
    app.include_router(api_router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        health = {"status": "starting"}
        
        if hasattr(app.state, "queen"):
            health = await app.state.queen.get_system_health()
        
        return {
            "service": "Queen AI Orchestrator",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            **health
        }

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "OMK Hive - Queen AI",
            "version": "1.0.0",
            "status": "operational",
            "docs": "/docs",
            "health": "/health",
            "contracts": {
                "bee_spawner": settings.BEE_SPAWNER_ADDRESS,
                "omk_bridge": settings.OMK_BRIDGE_ADDRESS,
                "treasury_vault": settings.TREASURY_VAULT_ADDRESS,
            }
        }

    return app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Changed from 8000 to 8001
        reload=True,
        log_level="info"
    )
