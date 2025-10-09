#!/usr/bin/env python3
"""
OMK Hive - System Shutdown Script

Gracefully stops all components with proper cleanup.

Usage:
    python3 stop.py              # Graceful shutdown
    python3 stop.py --force      # Force shutdown
    python3 stop.py --component queen  # Stop specific component
"""
import asyncio
import sys
import os
import signal
import time
from pathlib import Path
import argparse
import psutil

sys.path.insert(0, str(Path(__file__).parent))

import structlog

logger = structlog.get_logger(__name__)


class SystemShutdownManager:
    """Manages graceful system shutdown"""
    
    def __init__(self, force: bool = False):
        self.force = force
        self.shutdown_timeout = 30  # seconds
        self.processes = []
    
    async def shutdown(self, component: str = None):
        """
        Shutdown system components
        
        Args:
            component: Specific component to shutdown (None = all)
        """
        logger.info("="*70)
        logger.info("  OMK HIVE - SYSTEM SHUTDOWN")
        logger.info("="*70)
        logger.info(f"Mode: {'FORCE' if self.force else 'GRACEFUL'}")
        logger.info(f"Timeout: {self.shutdown_timeout}s")
        logger.info("="*70)
        
        shutdown_start = time.time()
        
        try:
            # Find running processes
            self._find_processes()
            
            if not self.processes:
                logger.info("No running OMK Hive processes found")
                return
            
            # Send shutdown signals
            await self._send_shutdown_signals()
            
            # Wait for graceful shutdown
            if not self.force:
                await self._wait_for_shutdown()
            
            # Force kill if necessary
            await self._force_kill_if_needed()
            
            # Cleanup
            await self._cleanup()
            
            shutdown_duration = time.time() - shutdown_start
            logger.info("="*70)
            logger.info(f"✅ SHUTDOWN COMPLETE ({shutdown_duration:.2f}s)")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}", exc_info=True)
            raise
    
    def _find_processes(self):
        """Find running OMK Hive processes"""
        logger.info("🔍 Searching for running processes...")
        
        current_pid = os.getpid()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if not cmdline:
                    continue
                
                cmdline_str = ' '.join(cmdline)
                
                # Look for OMK Hive processes
                if any(keyword in cmdline_str for keyword in ['uvicorn', 'start.py', 'main:app', 'queen']):
                    if proc.info['pid'] != current_pid:
                        self.processes.append(proc)
                        logger.info(f"Found: PID {proc.info['pid']} - {proc.info['name']}")
            
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.info(f"Found {len(self.processes)} running processes")
    
    async def _send_shutdown_signals(self):
        """Send SIGTERM to processes"""
        logger.info("📤 Sending shutdown signals...")
        
        for proc in self.processes:
            try:
                logger.info(f"Sending SIGTERM to PID {proc.pid}")
                proc.send_signal(signal.SIGTERM)
            except psutil.NoSuchProcess:
                logger.debug(f"Process {proc.pid} already terminated")
            except Exception as e:
                logger.error(f"Failed to signal PID {proc.pid}: {str(e)}")
    
    async def _wait_for_shutdown(self):
        """Wait for processes to shutdown gracefully"""
        logger.info(f"⏳ Waiting for graceful shutdown (max {self.shutdown_timeout}s)...")
        
        start_time = time.time()
        
        while self.processes and (time.time() - start_time) < self.shutdown_timeout:
            still_running = []
            
            for proc in self.processes:
                try:
                    if proc.is_running():
                        still_running.append(proc)
                except psutil.NoSuchProcess:
                    pass
            
            self.processes = still_running
            
            if self.processes:
                logger.debug(f"{len(self.processes)} processes still running...")
                await asyncio.sleep(1)
            else:
                logger.info("✅ All processes shutdown gracefully")
                return
        
        if self.processes:
            logger.warning(f"⚠️  {len(self.processes)} processes did not shutdown gracefully")
    
    async def _force_kill_if_needed(self):
        """Force kill remaining processes"""
        if not self.processes:
            return
        
        logger.warning(f"🔪 Force killing {len(self.processes)} remaining processes...")
        
        for proc in self.processes:
            try:
                logger.warning(f"Force killing PID {proc.pid}")
                proc.kill()
                proc.wait(timeout=5)
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                logger.error(f"Failed to kill PID {proc.pid}: {str(e)}")
    
    async def _cleanup(self):
        """Cleanup resources and temp files"""
        logger.info("🧹 Cleaning up...")
        
        # Close any open file handles
        cleanup_paths = [
            "./logs/queen.pid",
            "./data/temp/*",
        ]
        
        for path_pattern in cleanup_paths:
            from glob import glob
            for file_path in glob(path_pattern):
                try:
                    os.remove(file_path)
                    logger.debug(f"Removed: {file_path}")
                except Exception as e:
                    logger.debug(f"Cleanup failed for {file_path}: {str(e)}")
        
        logger.info("✅ Cleanup complete")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OMK Hive System Shutdown")
    parser.add_argument("--force", "-f", action="store_true", help="Force shutdown (no graceful period)")
    parser.add_argument("--component", "-c", default=None, help="Shutdown specific component")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Graceful shutdown timeout (seconds)")
    
    args = parser.parse_args()
    
    manager = SystemShutdownManager(force=args.force)
    manager.shutdown_timeout = args.timeout
    
    await manager.shutdown(component=args.component)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Shutdown interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Shutdown failed: {str(e)}")
        sys.exit(1)
