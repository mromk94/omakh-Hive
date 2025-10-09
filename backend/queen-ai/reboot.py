#!/usr/bin/env python3
"""
OMK Hive - System Reboot Script

Gracefully stops and restarts all components.

Usage:
    python3 reboot.py                    # Standard reboot
    python3 reboot.py --quick            # Quick reboot (skip validations)
    python3 reboot.py --environment prod # Reboot in production mode
"""
import asyncio
import sys
import time
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).parent))

import structlog
from stop import SystemShutdownManager
from start import SystemLifecycleManager

logger = structlog.get_logger(__name__)


class SystemRebootManager:
    """Manages system reboot"""
    
    def __init__(self, quick: bool = False, environment: str = "development"):
        self.quick = quick
        self.environment = environment
        self.reboot_delay = 2 if quick else 5  # seconds between stop and start
    
    async def reboot(self):
        """
        Reboot system
        
        Steps:
        1. Graceful shutdown
        2. Wait for cleanup
        3. Pre-startup checks
        4. Start system
        """
        logger.info("="*70)
        logger.info("  OMK HIVE - SYSTEM REBOOT")
        logger.info("="*70)
        logger.info(f"Mode: {'QUICK' if self.quick else 'STANDARD'}")
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Reboot delay: {self.reboot_delay}s")
        logger.info("="*70)
        
        reboot_start = time.time()
        
        try:
            # Phase 1: Shutdown
            logger.info("\n📴 PHASE 1: SHUTDOWN")
            shutdown_manager = SystemShutdownManager(force=self.quick)
            shutdown_manager.shutdown_timeout = 15 if self.quick else 30
            await shutdown_manager.shutdown()
            
            # Phase 2: Wait for cleanup
            logger.info(f"\n⏳ PHASE 2: WAITING {self.reboot_delay}s FOR CLEANUP")
            await asyncio.sleep(self.reboot_delay)
            
            # Phase 3: Pre-startup validation
            if not self.quick:
                logger.info("\n🔍 PHASE 3: PRE-STARTUP VALIDATION")
                await self._pre_startup_validation()
            
            # Phase 4: Startup
            logger.info("\n🚀 PHASE 4: STARTUP")
            startup_manager = SystemLifecycleManager(environment=self.environment)
            
            # Start in background (returns after initialization)
            asyncio.create_task(startup_manager.start())
            
            # Wait a bit to ensure startup began
            await asyncio.sleep(3)
            
            reboot_duration = time.time() - reboot_start
            logger.info("="*70)
            logger.info(f"✅ REBOOT COMPLETE ({reboot_duration:.2f}s)")
            logger.info("="*70)
            logger.info("\n💡 TIP: Check logs/queen.log for system status")
            logger.info("💡 TIP: Run 'python3 health_check.py' to verify health")
            
        except Exception as e:
            logger.error(f"❌ Reboot failed: {str(e)}", exc_info=True)
            logger.error("\n🔧 RECOVERY SUGGESTIONS:")
            logger.error("1. Check logs: tail -f logs/queen.log")
            logger.error("2. Manual start: python3 start.py --debug")
            logger.error("3. Check ports: lsof -i :8000")
            logger.error("4. Check processes: ps aux | grep queen")
            raise
    
    async def _pre_startup_validation(self):
        """Validate system is ready for startup"""
        logger.info("Running pre-startup validation...")
        
        checks = []
        
        # Check 1: No zombie processes
        import psutil
        zombie_count = 0
        for proc in psutil.process_iter(['name', 'status']):
            try:
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    zombie_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if zombie_count > 0:
            logger.warning(f"⚠️  {zombie_count} zombie processes detected")
        else:
            logger.info("✓ No zombie processes")
            checks.append(True)
        
        # Check 2: Port availability
        import socket
        port = 8000
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) == 0:
                logger.error(f"❌ Port {port} still in use")
                logger.error("   Waiting 5 more seconds...")
                await asyncio.sleep(5)
                
                # Retry
                if s.connect_ex(('localhost', port)) == 0:
                    raise RuntimeError(f"Port {port} still blocked after wait")
            else:
                logger.info(f"✓ Port {port} available")
                checks.append(True)
        
        # Check 3: File locks
        lock_files = ["./logs/queen.pid", "./data/db.lock"]
        for lock_file in lock_files:
            if Path(lock_file).exists():
                logger.warning(f"⚠️  Stale lock file: {lock_file}")
                Path(lock_file).unlink()
                logger.info(f"   Removed: {lock_file}")
        
        logger.info(f"✅ Pre-startup validation complete ({len(checks)} checks passed)")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OMK Hive System Reboot")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick reboot (skip validations)")
    parser.add_argument("--environment", "-e", default="development", choices=["development", "staging", "production"])
    parser.add_argument("--delay", "-d", type=int, help="Custom delay between stop/start (seconds)")
    
    args = parser.parse_args()
    
    manager = SystemRebootManager(quick=args.quick, environment=args.environment)
    
    if args.delay:
        manager.reboot_delay = args.delay
    
    await manager.reboot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Reboot cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Reboot failed: {str(e)}")
        print("\n🔧 Manual recovery required:")
        print("1. Stop: python3 stop.py --force")
        print("2. Start: python3 start.py --debug")
        sys.exit(1)
