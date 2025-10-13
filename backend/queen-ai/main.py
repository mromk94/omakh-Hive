"""
Queen AI - Main Application Entry Point
Integrates with all 16 PRIME2 Ethereum contracts + MySQL Database
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.csrf_protection import DoubleSubmitCSRFMiddleware
from dotenv import load_dotenv

from app.config.settings import settings
from app.config.logging_config import setup_logging, get_logger
from app.core.orchestrator import QueenOrchestrator

# Database imports
from app.database.connection import init_db
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Setup structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    logger.info("🚀 Starting Queen AI API Server")
    
    # Start with minimal state - initialize Queen in background
    app.state.queen = None
    app.state.initializing = True
    
    # Create background task for Queen initialization
    async def init_queen_background():
        """Initialize Queen in background to not block startup"""
        try:
            logger.info("🗄️  Initializing MySQL database...")
            if settings.ENVIRONMENT == "development":
                init_db()
                logger.info("✅ Database schema initialized")
            else:
                from app.database.connection import SessionLocal
                db = SessionLocal()
                try:
                    db.execute(text("SELECT 1"))
                    logger.info("✅ Database connection verified")
                finally:
                    db.close()
        except Exception as e:
            logger.warning(f"⚠️  Database connection failed: {e}")
        
        try:
            logger.info("🔧 Initializing Queen Orchestrator...")
            queen = QueenOrchestrator()
            await queen.initialize()
            
            app.state.queen = queen
            
            from app.api.v1.websocket import set_queen_instance
            set_queen_instance(queen)
            
            logger.info("✅ Queen AI fully operational")
        except Exception as e:
            logger.warning(f"⚠️  Queen initialization failed: {e}")
        finally:
            app.state.initializing = False
    
    # Start initialization in background
    asyncio.create_task(init_queen_background())
    
    logger.info("✅ API Server ready (Queen initializing in background)")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Queen AI")
    if app.state.queen:
        await app.state.queen.shutdown()


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
    
    # Add CSRF Protection (after CORS)
    app.add_middleware(DoubleSubmitCSRFMiddleware)
    logger.info("🛡️ CSRF protection enabled")

    # Include routers
    from app.api.v1 import auth, queen, queen_dev, admin, frontend, market, notifications, claude_analysis, contracts, websocket, autonomous_dev, proposal_auto_fix
    from app.api.v1.auth import router as auth_router
    
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(admin.router, prefix="/api/v1")
    app.include_router(frontend.router, prefix="/api/v1")
    app.include_router(market.router, prefix="/api/v1")
    app.include_router(notifications.router, prefix="/api/v1/admin")
    app.include_router(claude_analysis.router, prefix="/api/v1/admin")
    app.include_router(proposal_auto_fix.router, prefix="/api/v1/admin/proposals", tags=["Auto-Fix"])
    app.include_router(contracts.router, prefix="/api/v1")
    app.include_router(websocket.router, tags=["WebSocket"])
    app.include_router(queen.router, prefix="/api/v1")
    app.include_router(queen_dev.router, prefix="/api/v1/queen-dev")
    app.include_router(autonomous_dev.router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint - always returns 200 for Cloud Run"""
        if getattr(app.state, "initializing", False):
            status = "initializing"
        elif app.state.queen:
            status = "operational"
        else:
            status = "degraded"
        
        return {
            "service": "Queen AI Orchestrator",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "status": status,
            "queen_initialized": app.state.queen is not None
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
    import os
    
    # Use PORT environment variable (Google Cloud compatible)
    port = int(os.getenv("PORT", "8001"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,  # Only reload in debug mode
        log_level="info"
    )
