#!/usr/bin/env python3
"""
OMK Hive - Real-time Status Dashboard

Live system status monitoring in terminal.

Usage:
    python3 status.py              # Real-time dashboard
    python3 status.py --refresh 5  # Update every 5 seconds
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
import argparse

sys.path.insert(0, str(Path(__file__).parent))

import structlog

logger = structlog.get_logger(__name__)


class StatusDashboard:
    """Real-time system status dashboard"""
    
    def __init__(self, refresh_interval: int = 2):
        self.refresh_interval = refresh_interval
        self.running = True
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    async def display(self):
        """Display real-time status"""
        while self.running:
            self.clear_screen()
            
            # Header
            print("="*80)
            print("  OMK HIVE - SYSTEM STATUS DASHBOARD")
            print("="*80)
            print(f"  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Refresh: {self.refresh_interval}s | Press Ctrl+C to exit")
            print("="*80)
            print()
            
            # System Resources
            await self._display_system_resources()
            
            # Components Status
            await self._display_component_status()
            
            # Recent Activity
            await self._display_recent_activity()
            
            # Metrics
            await self._display_metrics()
            
            # Footer
            print("\n" + "="*80)
            
            # Wait for next refresh
            try:
                await asyncio.sleep(self.refresh_interval)
            except asyncio.CancelledError:
                self.running = False
                break
    
    async def _display_system_resources(self):
        """Display system resources"""
        try:
            import psutil
            
            print("📊 SYSTEM RESOURCES")
            print("-" * 80)
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_bar = self._create_bar(cpu_percent, 50)
            cpu_color = self._get_color(cpu_percent)
            print(f"  CPU:    {cpu_bar} {cpu_color}{cpu_percent:5.1f}%\033[0m")
            
            # Memory
            memory = psutil.virtual_memory()
            mem_bar = self._create_bar(memory.percent, 50)
            mem_color = self._get_color(memory.percent)
            print(f"  Memory: {mem_bar} {mem_color}{memory.percent:5.1f}%\033[0m ({memory.available / 1024**3:.1f}GB free)")
            
            # Disk
            disk = psutil.disk_usage('/')
            disk_bar = self._create_bar(disk.percent, 50)
            disk_color = self._get_color(disk.percent)
            print(f"  Disk:   {disk_bar} {disk_color}{disk.percent:5.1f}%\033[0m ({disk.free / 1024**3:.1f}GB free)")
            
            print()
        
        except Exception as e:
            print(f"  ⚠️  Resource monitoring unavailable: {str(e)}\n")
    
    async def _display_component_status(self):
        """Display component status"""
        print("🔧 COMPONENT STATUS")
        print("-" * 80)
        
        components = {
            "Database": await self._check_database(),
            "Redis": await self._check_redis(),
            "LLM": await self._check_llm(),
            "Bees": await self._check_bees(),
            "API": await self._check_api(),
        }
        
        for name, status in components.items():
            emoji = "✅" if status["healthy"] else "❌"
            details = status.get("details", "")
            print(f"  {emoji} {name:12} {details}")
        
        print()
    
    async def _display_recent_activity(self):
        """Display recent activity from logs"""
        print("📝 RECENT ACTIVITY (Last 5 events)")
        print("-" * 80)
        
        try:
            log_file = Path("./logs/queen.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    recent = lines[-5:] if len(lines) >= 5 else lines
                    
                    for line in recent:
                        # Truncate long lines
                        truncated = line.strip()[:75]
                        print(f"  • {truncated}")
            else:
                print("  No recent activity logged")
        except Exception as e:
            print(f"  ⚠️  Log unavailable: {str(e)}")
        
        print()
    
    async def _display_metrics(self):
        """Display key metrics"""
        print("📈 KEY METRICS")
        print("-" * 80)
        
        try:
            # Get metrics from various sources
            metrics = {}
            
            # LLM costs
            try:
                from app.llm.abstraction import LLMAbstraction
                llm = LLMAbstraction()
                await llm.initialize()
                metrics["LLM Total Cost"] = f"${llm.costs['total']:.6f}"
            except:
                pass
            
            # Database connections
            try:
                from app.db.base import engine
                pool = engine.pool
                metrics["DB Connections"] = f"{pool.checkedout()}/{pool.size()}"
            except:
                pass
            
            # Display metrics
            if metrics:
                for key, value in metrics.items():
                    print(f"  {key:20} {value}")
            else:
                print("  No metrics available")
        
        except Exception as e:
            print(f"  ⚠️  Metrics unavailable: {str(e)}")
        
        print()
    
    def _create_bar(self, percentage: float, width: int = 50) -> str:
        """Create progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def _get_color(self, percentage: float) -> str:
        """Get color code based on percentage"""
        if percentage < 70:
            return "\033[92m"  # Green
        elif percentage < 85:
            return "\033[93m"  # Yellow
        else:
            return "\033[91m"  # Red
    
    async def _check_database(self) -> dict:
        """Check database status"""
        try:
            from app.db.base import engine
            from sqlalchemy import text
            
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            pool = engine.pool
            return {
                "healthy": True,
                "details": f"Connected ({pool.checkedout()}/{pool.size()} connections)"
            }
        except Exception as e:
            return {"healthy": False, "details": f"Error: {str(e)[:30]}"}
    
    async def _check_redis(self) -> dict:
        """Check Redis status"""
        try:
            from app.core.redis_message_bus import RedisMessageBus
            
            bus = RedisMessageBus()
            await bus.initialize()
            
            if bus.initialized:
                return {"healthy": True, "details": "Connected"}
            else:
                return {"healthy": False, "details": "Not initialized"}
        except Exception as e:
            return {"healthy": False, "details": "In-memory mode"}
    
    async def _check_llm(self) -> dict:
        """Check LLM status"""
        try:
            from app.llm.abstraction import LLMAbstraction
            from app.config.settings import settings
            
            llm = LLMAbstraction()
            await llm.initialize()
            
            if llm.providers:
                return {
                    "healthy": True,
                    "details": f"{settings.DEFAULT_LLM_PROVIDER} ({len(llm.providers)} available)"
                }
            else:
                return {"healthy": False, "details": "No providers"}
        except Exception as e:
            return {"healthy": False, "details": "Not configured"}
    
    async def _check_bees(self) -> dict:
        """Check bees status"""
        try:
            from app.bees.manager import BeeManager
            
            manager = BeeManager()
            await manager.initialize()
            
            return {
                "healthy": len(manager.bees) > 0,
                "details": f"{len(manager.bees)} bees active"
            }
        except Exception as e:
            return {"healthy": False, "details": "Error"}
    
    async def _check_api(self) -> dict:
        """Check API status"""
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get("http://localhost:8000/health")
                
                if response.status_code == 200:
                    return {"healthy": True, "details": "Running on :8000"}
                else:
                    return {"healthy": False, "details": f"Status {response.status_code}"}
        except:
            return {"healthy": False, "details": "Not running"}


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OMK Hive Status Dashboard")
    parser.add_argument("--refresh", "-r", type=int, default=2, help="Refresh interval (seconds)")
    
    args = parser.parse_args()
    
    dashboard = StatusDashboard(refresh_interval=args.refresh)
    
    try:
        await dashboard.display()
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped")


if __name__ == "__main__":
    asyncio.run(main())
