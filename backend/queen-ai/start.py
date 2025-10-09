#!/usr/bin/env python3
"""
OMK Hive - System Startup Script

Gracefully starts all components with proper initialization order.
Works for both localhost and cloud deployment.

Usage:
    python3 start.py                    # Start all components
    python3 start.py --component queen  # Start specific component
    python3 start.py --environment prod # Production mode
"""
import asyncio
import sys
import os
import signal
import time
from pathlib import Path
from typing import Optional, List
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

import structlog
from app.config.settings import settings

logger = structlog.get_logger(__name__)


class SystemLifecycleManager:
    """
    Manages system startup, health checks, and graceful shutdown
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.is_cloud = os.getenv("K_SERVICE") is not None  # Cloud Run detection
        self.is_gke = os.path.exists("/var/run/secrets/kubernetes.io")  # GKE detection
        
        self.components = {}
        self.shutdown_event = asyncio.Event()
        self.startup_time = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown_signal)
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)
    
    def _handle_shutdown_signal(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.warning(f"Received shutdown signal: {signal.Signals(signum).name}")
        self.shutdown_event.set()
    
    async def start(self, component: Optional[str] = None):
        """
        Start system components in proper order
        
        Startup Order:
        1. Configuration validation
        2. Database connections
        3. Redis connections
        4. LLM providers
        5. Bee manager
        6. Queen orchestrator
        7. API server
        """
        logger.info("="*70)
        logger.info("  OMK HIVE - SYSTEM STARTUP")
        logger.info("="*70)
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Deployment: {'Cloud' if self.is_cloud or self.is_gke else 'Local'}")
        logger.info(f"Debug Mode: {settings.DEBUG}")
        logger.info("="*70)
        
        self.startup_time = time.time()
        
        try:
            # Phase 1: Pre-flight checks
            await self._preflight_checks()
            
            # Phase 2: Initialize core infrastructure
            await self._initialize_infrastructure()
            
            # Phase 3: Initialize AI components
            await self._initialize_ai_components()
            
            # Phase 4: Start API server
            if component is None or component == "api":
                await self._start_api_server()
            
            # Phase 5: Post-startup validation
            await self._post_startup_validation()
            
            startup_duration = time.time() - self.startup_time
            logger.info("="*70)
            logger.info(f"✅ SYSTEM STARTUP COMPLETE ({startup_duration:.2f}s)")
            logger.info("="*70)
            
            # Keep running until shutdown signal
            await self.shutdown_event.wait()
            
            # Graceful shutdown
            await self.stop()
            
        except Exception as e:
            logger.error(f"System startup failed: {str(e)}", exc_info=True)
            await self.stop()
            sys.exit(1)
    
    async def _preflight_checks(self):
        """Pre-flight validation checks"""
        logger.info("🔍 Running pre-flight checks...")
        
        checks = []
        
        # Check 1: Environment variables
        required_env = ["DATABASE_URL", "REDIS_URL"]
        for env_var in required_env:
            value = getattr(settings, env_var, None)
            if not value:
                logger.warning(f"Missing environment variable: {env_var}")
            else:
                logger.info(f"✓ {env_var} configured")
                checks.append(True)
        
        # Check 2: LLM API keys
        if settings.DEFAULT_LLM_PROVIDER == "gemini" and not settings.GEMINI_API_KEY:
            logger.warning("⚠️  Gemini API key not configured (LLM features disabled)")
        elif settings.GEMINI_API_KEY:
            logger.info("✓ Gemini API key configured")
            checks.append(True)
        
        # Check 3: File permissions
        required_dirs = ["./logs", "./data"]
        for dir_path in required_dirs:
            Path(dir_path).mkdir(exist_ok=True, parents=True)
            logger.info(f"✓ Directory created/verified: {dir_path}")
        
        # Check 4: Port availability (localhost only)
        if not self.is_cloud and not self.is_gke:
            import socket
            port = 8000
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) == 0:
                    logger.error(f"❌ Port {port} already in use")
                    raise RuntimeError(f"Port {port} is not available")
                logger.info(f"✓ Port {port} available")
        
        logger.info(f"✅ Pre-flight checks complete ({len(checks)} passed)")
    
    async def _initialize_infrastructure(self):
        """Initialize database, Redis, and core infrastructure"""
        logger.info("🔧 Initializing infrastructure...")
        
        # Database
        try:
            from app.db.base import engine, init_db
            from sqlalchemy import text
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Create tables if needed
            init_db()
            
            logger.info("✅ Database connected and initialized")
            self.components["database"] = {"status": "running", "engine": engine}
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            if self.environment == "production":
                raise
            logger.warning("Continuing without database (development mode)")
        
        # Redis
        try:
            from app.core.redis_message_bus import RedisMessageBus
            from app.core.redis_hive_board import RedisHiveBoard
            
            message_bus = RedisMessageBus()
            await message_bus.initialize()
            
            hive_board = RedisHiveBoard()
            await hive_board.initialize()
            
            if message_bus.initialized and hive_board.initialized:
                logger.info("✅ Redis connected (MessageBus + HiveBoard)")
                self.components["redis"] = {
                    "status": "running",
                    "message_bus": message_bus,
                    "hive_board": hive_board
                }
            else:
                raise Exception("Redis initialization failed")
                
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {str(e)}")
            logger.warning("Falling back to in-memory message bus")
            
            # Fallback to in-memory
            from app.core.message_bus import MessageBus
            from app.core.hive_board import HiveInformationBoard
            
            message_bus = MessageBus()
            await message_bus.initialize()
            
            hive_board = HiveInformationBoard()
            await hive_board.initialize()
            
            logger.info("✅ In-memory MessageBus + HiveBoard initialized")
            self.components["message_bus"] = {"status": "running", "instance": message_bus}
            self.components["hive_board"] = {"status": "running", "instance": hive_board}
        
        # BigQuery (optional)
        if settings.BIGQUERY_ENABLED:
            try:
                from app.learning.bigquery_logger import bigquery_logger
                await bigquery_logger.initialize()
                
                if bigquery_logger.initialized:
                    logger.info("✅ BigQuery learning function initialized")
                    self.components["bigquery"] = {"status": "running", "logger": bigquery_logger}
                
            except Exception as e:
                logger.warning(f"BigQuery initialization failed: {str(e)}")
                logger.warning("Learning function disabled")
    
    async def _initialize_ai_components(self):
        """Initialize LLM, Bees, and Queen"""
        logger.info("🧠 Initializing AI components...")
        
        # LLM Abstraction
        try:
            from app.llm.abstraction import LLMAbstraction
            
            llm = LLMAbstraction()
            await llm.initialize()
            
            logger.info(f"✅ LLM initialized (provider: {settings.DEFAULT_LLM_PROVIDER})")
            self.components["llm"] = {"status": "running", "instance": llm}
            
        except Exception as e:
            logger.error(f"❌ LLM initialization failed: {str(e)}")
            if self.environment == "production":
                raise
            logger.warning("Continuing without LLM")
        
        # Bee Manager
        try:
            from app.bees.manager import BeeManager
            
            llm_instance = self.components.get("llm", {}).get("instance")
            bee_manager = BeeManager(llm_abstraction=llm_instance)
            await bee_manager.initialize()
            
            bee_count = len(bee_manager.bees)
            logger.info(f"✅ Bee Manager initialized ({bee_count} bees)")
            self.components["bee_manager"] = {"status": "running", "instance": bee_manager}
            
        except Exception as e:
            logger.error(f"❌ Bee Manager initialization failed: {str(e)}")
            if self.environment == "production":
                raise
        
        # Queen Orchestrator
        try:
            from app.core.orchestrator import QueenOrchestrator
            
            queen = QueenOrchestrator()
            await queen.initialize()
            
            logger.info("✅ Queen Orchestrator initialized")
            self.components["queen"] = {"status": "running", "instance": queen}
            
        except Exception as e:
            logger.error(f"❌ Queen initialization failed: {str(e)}")
            if self.environment == "production":
                raise
    
    async def _start_api_server(self):
        """Start FastAPI server"""
        logger.info("🌐 Starting API server...")
        
        # Note: In production, this is handled by uvicorn command
        # This is just for validation
        try:
            from app.main import app
            logger.info("✅ FastAPI application loaded")
            self.components["api"] = {"status": "ready"}
            
        except Exception as e:
            logger.error(f"❌ API server failed: {str(e)}")
            raise
    
    async def _post_startup_validation(self):
        """Post-startup health checks"""
        logger.info("🏥 Running post-startup validation...")
        
        # Check component health
        healthy_components = 0
        total_components = len(self.components)
        
        for name, component in self.components.items():
            if component.get("status") == "running" or component.get("status") == "ready":
                logger.info(f"✓ {name}: healthy")
                healthy_components += 1
            else:
                logger.warning(f"⚠ {name}: degraded")
        
        health_percentage = (healthy_components / total_components * 100) if total_components > 0 else 0
        logger.info(f"System Health: {health_percentage:.1f}% ({healthy_components}/{total_components} components)")
        
        if health_percentage < 50:
            logger.error("❌ System health below 50% - startup failed")
            raise RuntimeError("Insufficient system health")
    
    async def stop(self):
        """Graceful shutdown of all components"""
        logger.info("="*70)
        logger.info("  INITIATING GRACEFUL SHUTDOWN")
        logger.info("="*70)
        
        shutdown_start = time.time()
        
        # Shutdown in reverse order
        shutdown_order = ["api", "queen", "bee_manager", "llm", "bigquery", "redis", "message_bus", "hive_board", "database"]
        
        for component_name in shutdown_order:
            if component_name in self.components:
                try:
                    component = self.components[component_name]
                    instance = component.get("instance")
                    
                    if instance and hasattr(instance, "shutdown"):
                        await instance.shutdown()
                        logger.info(f"✓ {component_name} shutdown complete")
                    elif component_name == "database":
                        engine = component.get("engine")
                        if engine:
                            engine.dispose()
                            logger.info(f"✓ {component_name} shutdown complete")
                    
                except Exception as e:
                    logger.error(f"Error shutting down {component_name}: {str(e)}")
        
        shutdown_duration = time.time() - shutdown_start
        logger.info("="*70)
        logger.info(f"✅ SHUTDOWN COMPLETE ({shutdown_duration:.2f}s)")
        logger.info("="*70)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OMK Hive System Startup")
    parser.add_argument("--environment", "-e", default="development", choices=["development", "staging", "production"])
    parser.add_argument("--component", "-c", default=None, help="Start specific component only")
    parser.add_argument("--debug", "-d", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Update settings
    if args.debug:
        os.environ["DEBUG"] = "true"
    
    # Start system
    manager = SystemLifecycleManager(environment=args.environment)
    await manager.start(component=args.component)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutdown initiated by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        sys.exit(1)
