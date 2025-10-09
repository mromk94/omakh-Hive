#!/usr/bin/env python3
"""
OMK Hive - Comprehensive Health Check

Performs deep system health analysis across all components.

Usage:
    python3 health_check.py              # Full health check
    python3 health_check.py --component database  # Check specific component
    python3 health_check.py --watch      # Continuous monitoring
"""
import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
import argparse
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import structlog
from app.config.settings import settings

logger = structlog.get_logger(__name__)


class HealthCheckResult:
    """Health check result container"""
    
    def __init__(self, component: str):
        self.component = component
        self.status = "unknown"
        self.checks = []
        self.errors = []
        self.warnings = []
        self.metrics = {}
        self.timestamp = datetime.utcnow()
    
    def add_check(self, name: str, passed: bool, details: str = ""):
        """Add check result"""
        self.checks.append({
            "name": name,
            "passed": passed,
            "details": details
        })
    
    def add_error(self, error: str):
        """Add error"""
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        """Add warning"""
        self.warnings.append(warning)
    
    def set_metric(self, key: str, value: Any):
        """Set metric"""
        self.metrics[key] = value
    
    def calculate_status(self):
        """Calculate overall status"""
        total_checks = len(self.checks)
        if total_checks == 0:
            self.status = "unknown"
            return
        
        passed_checks = sum(1 for c in self.checks if c["passed"])
        pass_rate = passed_checks / total_checks
        
        if pass_rate == 1.0:
            self.status = "healthy"
        elif pass_rate >= 0.7:
            self.status = "degraded"
        else:
            self.status = "unhealthy"
    
    def print_report(self):
        """Print formatted report"""
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
            "unknown": "❓"
        }
        
        print(f"\n{'='*70}")
        print(f"  {status_emoji.get(self.status, '?')} {self.component.upper()} - {self.status.upper()}")
        print(f"{'='*70}")
        
        # Checks
        if self.checks:
            print(f"\n📋 Checks ({sum(1 for c in self.checks if c['passed'])}/{len(self.checks)} passed):")
            for check in self.checks:
                emoji = "✓" if check["passed"] else "✗"
                print(f"  {emoji} {check['name']}")
                if check["details"]:
                    print(f"    {check['details']}")
        
        # Metrics
        if self.metrics:
            print(f"\n📊 Metrics:")
            for key, value in self.metrics.items():
                print(f"  • {key}: {value}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        # Errors
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"  • {error}")


class SystemHealthChecker:
    """Comprehensive system health checker"""
    
    def __init__(self):
        self.results: List[HealthCheckResult] = []
    
    async def check_all(self, component: str = None):
        """Run all health checks"""
        logger.info("="*70)
        logger.info("  OMK HIVE - SYSTEM HEALTH CHECK")
        logger.info("="*70)
        logger.info(f"Timestamp: {datetime.utcnow().isoformat()}")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info("="*70)
        
        check_start = time.time()
        
        # Run checks
        checks = [
            self.check_database,
            self.check_redis,
            self.check_llm,
            self.check_bees,
            self.check_api,
            self.check_system_resources,
            self.check_security,
        ]
        
        if component:
            # Filter to specific component
            checks = [c for c in checks if component.lower() in c.__name__.lower()]
        
        for check in checks:
            try:
                result = await check()
                result.calculate_status()
                self.results.append(result)
                result.print_report()
            except Exception as e:
                logger.error(f"Health check failed: {check.__name__}: {str(e)}")
        
        # Overall summary
        check_duration = time.time() - check_start
        self._print_summary(check_duration)
    
    async def check_database(self) -> HealthCheckResult:
        """Check database health"""
        result = HealthCheckResult("Database")
        
        try:
            from app.db.base import engine
            from sqlalchemy import text
            
            # Connection test
            start = time.time()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            latency = (time.time() - start) * 1000
            
            result.add_check("Connection", True, f"Latency: {latency:.2f}ms")
            result.set_metric("latency_ms", f"{latency:.2f}")
            
            # Pool status
            pool = engine.pool
            result.set_metric("pool_size", pool.size())
            result.set_metric("pool_checked_out", pool.checkedout())
            result.set_metric("pool_overflow", pool.overflow())
            
            if pool.checkedout() == pool.size():
                result.add_warning("Connection pool exhausted")
            
            # Table count
            with engine.connect() as conn:
                tables_result = conn.execute(text("""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                table_count = tables_result.scalar()
                result.add_check("Tables", table_count > 0, f"{table_count} tables")
                result.set_metric("table_count", table_count)
            
        except Exception as e:
            result.add_check("Connection", False, str(e))
            result.add_error(f"Database unavailable: {str(e)}")
        
        return result
    
    async def check_redis(self) -> HealthCheckResult:
        """Check Redis health"""
        result = HealthCheckResult("Redis")
        
        try:
            from app.core.redis_message_bus import RedisMessageBus
            
            bus = RedisMessageBus()
            await bus.initialize()
            
            if bus.initialized:
                result.add_check("Connection", True)
                
                # Get Redis info
                health = await bus.health_check()
                if health.get("healthy"):
                    result.add_check("Health", True)
                    result.set_metric("connected_clients", health.get("connected_clients", "N/A"))
                    result.set_metric("used_memory", health.get("used_memory_human", "N/A"))
                    result.set_metric("uptime", f"{health.get('uptime_in_seconds', 0)}s")
                else:
                    result.add_check("Health", False, health.get("error"))
            else:
                result.add_check("Connection", False, "Not initialized")
                result.add_warning("Falling back to in-memory")
            
        except Exception as e:
            result.add_check("Connection", False, str(e))
            result.add_error(f"Redis unavailable: {str(e)}")
        
        return result
    
    async def check_llm(self) -> HealthCheckResult:
        """Check LLM provider health"""
        result = HealthCheckResult("LLM")
        
        try:
            from app.llm.abstraction import LLMAbstraction
            
            llm = LLMAbstraction()
            await llm.initialize()
            
            # Provider availability
            result.add_check("Initialization", len(llm.providers) > 0, f"{len(llm.providers)} providers")
            result.set_metric("providers", list(llm.providers.keys()))
            result.set_metric("default_provider", llm.current_provider)
            
            # Test generation (small prompt)
            if llm.providers:
                try:
                    start = time.time()
                    response = await llm.generate("Say 'OK'", max_tokens=10, temperature=0)
                    latency = (time.time() - start) * 1000
                    
                    result.add_check("Generation", len(response) > 0, f"Latency: {latency:.0f}ms")
                    result.set_metric("generation_latency_ms", f"{latency:.0f}")
                except Exception as e:
                    result.add_check("Generation", False, str(e))
                    result.add_warning(f"Generation failed: {str(e)}")
            
            # Cost tracking
            costs = llm.costs
            result.set_metric("total_cost", f"${costs['total']:.6f}")
            
        except Exception as e:
            result.add_check("Initialization", False, str(e))
            result.add_error(f"LLM unavailable: {str(e)}")
        
        return result
    
    async def check_bees(self) -> HealthCheckResult:
        """Check bee health"""
        result = HealthCheckResult("Bees")
        
        try:
            from app.bees.manager import BeeManager
            
            manager = BeeManager()
            await manager.initialize()
            
            bee_count = len(manager.bees)
            result.add_check("Initialization", bee_count > 0, f"{bee_count} bees loaded")
            result.set_metric("bee_count", bee_count)
            
            # Test each bee
            working_bees = 0
            for bee_name, bee in manager.bees.items():
                try:
                    # Simple health check
                    if hasattr(bee, 'process'):
                        test_result = await bee.process({})
                        if test_result:
                            working_bees += 1
                except Exception:
                    result.add_warning(f"Bee '{bee_name}' health check failed")
            
            result.add_check("Bee Availability", working_bees > 0, f"{working_bees}/{bee_count} responsive")
            result.set_metric("working_bees", f"{working_bees}/{bee_count}")
            
        except Exception as e:
            result.add_check("Initialization", False, str(e))
            result.add_error(f"Bee manager unavailable: {str(e)}")
        
        return result
    
    async def check_api(self) -> HealthCheckResult:
        """Check API health"""
        result = HealthCheckResult("API")
        
        try:
            import httpx
            
            # Test local API
            base_url = "http://localhost:8000"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Health endpoint
                try:
                    response = await client.get(f"{base_url}/health")
                    result.add_check("Health Endpoint", response.status_code == 200)
                except Exception as e:
                    result.add_check("Health Endpoint", False, str(e))
                    result.add_warning("API server may not be running")
            
        except ImportError:
            result.add_warning("httpx not installed - skipping API check")
        except Exception as e:
            result.add_error(f"API check failed: {str(e)}")
        
        return result
    
    async def check_system_resources(self) -> HealthCheckResult:
        """Check system resources"""
        result = HealthCheckResult("System Resources")
        
        try:
            import psutil
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            result.add_check("CPU Usage", cpu_percent < 90, f"{cpu_percent}%")
            result.set_metric("cpu_percent", f"{cpu_percent}%")
            
            if cpu_percent > 80:
                result.add_warning(f"High CPU usage: {cpu_percent}%")
            
            # Memory
            memory = psutil.virtual_memory()
            result.add_check("Memory Usage", memory.percent < 90, f"{memory.percent}%")
            result.set_metric("memory_percent", f"{memory.percent}%")
            result.set_metric("memory_available", f"{memory.available / 1024 / 1024 / 1024:.2f}GB")
            
            if memory.percent > 80:
                result.add_warning(f"High memory usage: {memory.percent}%")
            
            # Disk
            disk = psutil.disk_usage('/')
            result.add_check("Disk Usage", disk.percent < 90, f"{disk.percent}%")
            result.set_metric("disk_percent", f"{disk.percent}%")
            result.set_metric("disk_free", f"{disk.free / 1024 / 1024 / 1024:.2f}GB")
            
            if disk.percent > 80:
                result.add_warning(f"Low disk space: {disk.percent}% used")
            
        except Exception as e:
            result.add_error(f"Resource check failed: {str(e)}")
        
        return result
    
    async def check_security(self) -> HealthCheckResult:
        """Check security configuration"""
        result = HealthCheckResult("Security")
        
        # Check debug mode
        if settings.DEBUG and settings.ENVIRONMENT == "production":
            result.add_check("Debug Mode", False, "Debug enabled in production!")
            result.add_error("DEBUG=True in production environment")
        else:
            result.add_check("Debug Mode", True)
        
        # Check API keys
        has_admin_key = bool(settings.ADMIN_API_KEYS)
        result.add_check("Admin API Keys", has_admin_key)
        
        if not has_admin_key:
            result.add_warning("No admin API keys configured")
        
        # Check secret key
        if settings.SECRET_KEY == "development-secret-key-change-in-production":
            result.add_check("Secret Key", False, "Using default secret key")
            result.add_error("Change SECRET_KEY in production!")
        else:
            result.add_check("Secret Key", True)
        
        return result
    
    def _print_summary(self, duration: float):
        """Print overall summary"""
        print(f"\n{'='*70}")
        print(f"  HEALTH CHECK SUMMARY")
        print(f"{'='*70}")
        
        total_components = len(self.results)
        healthy = sum(1 for r in self.results if r.status == "healthy")
        degraded = sum(1 for r in self.results if r.status == "degraded")
        unhealthy = sum(1 for r in self.results if r.status == "unhealthy")
        
        print(f"\nComponents Checked: {total_components}")
        print(f"  ✅ Healthy: {healthy}")
        print(f"  ⚠️  Degraded: {degraded}")
        print(f"  ❌ Unhealthy: {unhealthy}")
        
        overall_health = (healthy / total_components * 100) if total_components > 0 else 0
        print(f"\nOverall System Health: {overall_health:.1f}%")
        print(f"Check Duration: {duration:.2f}s")
        
        if overall_health == 100:
            print("\n🎉 System is fully operational!")
        elif overall_health >= 70:
            print("\n⚠️  System is operational but degraded")
        else:
            print("\n❌ System health is critical!")
        
        print(f"{'='*70}\n")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OMK Hive Health Check")
    parser.add_argument("--component", "-c", help="Check specific component only")
    parser.add_argument("--watch", "-w", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", "-i", type=int, default=30, help="Watch interval (seconds)")
    
    args = parser.parse_args()
    
    checker = SystemHealthChecker()
    
    if args.watch:
        print(f"👀 Starting continuous monitoring (interval: {args.interval}s)")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                await checker.check_all(component=args.component)
                await asyncio.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
    else:
        await checker.check_all(component=args.component)


if __name__ == "__main__":
    asyncio.run(main())
