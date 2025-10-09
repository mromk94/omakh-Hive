#!/usr/bin/env python3
"""
OMK Hive - Advanced Debugging & Diagnostics Tool

Deep diagnostic tool for troubleshooting system issues.

Usage:
    python3 debug.py --logs              # Analyze recent logs
    python3 debug.py --trace bee_error   # Trace specific error
    python3 debug.py --profile           # Performance profiling
    python3 debug.py --inspect database  # Deep dive into component
"""
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent))

import structlog
from app.config.settings import settings

logger = structlog.get_logger(__name__)


class DebugAnalyzer:
    """Advanced debugging and diagnostics"""
    
    def __init__(self):
        self.log_dir = Path("./logs")
        self.findings = []
        self.recommendations = []
    
    async def analyze_logs(self, hours: int = 1):
        """Analyze recent logs for errors and patterns"""
        print(f"\n{'='*70}")
        print(f"  LOG ANALYSIS (Last {hours} hour(s))")
        print(f"{'='*70}\n")
        
        log_files = list(self.log_dir.glob("*.log"))
        
        if not log_files:
            print("❌ No log files found")
            return
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        errors = []
        warnings = []
        patterns = {}
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        # Parse structured logs
                        if 'ERROR' in line:
                            errors.append(line.strip())
                        elif 'WARNING' in line:
                            warnings.append(line.strip())
                        
                        # Look for patterns
                        if 'failed' in line.lower():
                            key = 'failures'
                            patterns[key] = patterns.get(key, 0) + 1
                        if 'timeout' in line.lower():
                            key = 'timeouts'
                            patterns[key] = patterns.get(key, 0) + 1
                        if 'connection' in line.lower() and 'refused' in line.lower():
                            key = 'connection_refused'
                            patterns[key] = patterns.get(key, 0) + 1
            
            except Exception as e:
                print(f"⚠️  Failed to read {log_file}: {str(e)}")
        
        # Report errors
        if errors:
            print(f"❌ ERRORS FOUND: {len(errors)}")
            for error in errors[-10:]:  # Last 10
                print(f"  • {error[:150]}...")
        else:
            print("✅ No errors found")
        
        # Report warnings
        if warnings:
            print(f"\n⚠️  WARNINGS FOUND: {len(warnings)}")
            for warning in warnings[-5:]:  # Last 5
                print(f"  • {warning[:150]}...")
        else:
            print("✅ No warnings found")
        
        # Report patterns
        if patterns:
            print(f"\n📊 PATTERNS DETECTED:")
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"  • {pattern}: {count} occurrences")
                
                # Generate recommendations
                if pattern == 'connection_refused' and count > 5:
                    self.recommendations.append(
                        "High number of connection refused errors - check database/Redis connectivity"
                    )
                elif pattern == 'timeouts' and count > 10:
                    self.recommendations.append(
                        "Frequent timeouts detected - consider increasing timeout values or checking network"
                    )
        
        print()
    
    async def trace_error(self, error_keyword: str):
        """Trace specific error through system"""
        print(f"\n{'='*70}")
        print(f"  ERROR TRACE: '{error_keyword}'")
        print(f"{'='*70}\n")
        
        found_traces = []
        
        # Search all logs
        for log_file in self.log_dir.glob("*.log"):
            try:
                with open(log_file, 'r') as f:
                    line_num = 0
                    for line in f:
                        line_num += 1
                        if error_keyword.lower() in line.lower():
                            found_traces.append({
                                'file': log_file.name,
                                'line': line_num,
                                'content': line.strip()
                            })
            except Exception as e:
                logger.debug(f"Failed to search {log_file}: {str(e)}")
        
        if found_traces:
            print(f"📍 Found {len(found_traces)} occurrences:\n")
            for trace in found_traces[:20]:  # Show first 20
                print(f"  {trace['file']}:{trace['line']}")
                print(f"  {trace['content'][:200]}")
                print()
        else:
            print(f"❌ No traces found for '{error_keyword}'")
    
    async def profile_performance(self):
        """Profile system performance"""
        print(f"\n{'='*70}")
        print(f"  PERFORMANCE PROFILING")
        print(f"{'='*70}\n")
        
        import psutil
        import time
        
        # CPU profiling
        print("📊 CPU Profiling (5 second sample)...")
        cpu_samples = []
        for i in range(5):
            cpu_samples.append(psutil.cpu_percent(interval=1))
            print(f"  Sample {i+1}: {cpu_samples[-1]}%")
        
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        print(f"  Average: {avg_cpu:.1f}%")
        
        if avg_cpu > 80:
            self.recommendations.append(f"High CPU usage detected ({avg_cpu:.1f}%) - investigate CPU-intensive processes")
        
        # Memory profiling
        print(f"\n💾 Memory Profiling...")
        memory = psutil.virtual_memory()
        print(f"  Total: {memory.total / 1024 / 1024 / 1024:.2f} GB")
        print(f"  Available: {memory.available / 1024 / 1024 / 1024:.2f} GB")
        print(f"  Used: {memory.percent}%")
        
        if memory.percent > 80:
            self.recommendations.append(f"High memory usage ({memory.percent}%) - check for memory leaks")
        
        # Process profiling
        print(f"\n🔍 Process Analysis...")
        current_process = psutil.Process()
        
        with current_process.oneshot():
            print(f"  PID: {current_process.pid}")
            print(f"  Memory: {current_process.memory_info().rss / 1024 / 1024:.2f} MB")
            print(f"  CPU: {current_process.cpu_percent()}%")
            print(f"  Threads: {current_process.num_threads()}")
            print(f"  Open Files: {len(current_process.open_files())}")
        
        # Database connection profiling
        try:
            from app.db.base import engine
            pool = engine.pool
            
            print(f"\n💧 Database Connection Pool:")
            print(f"  Size: {pool.size()}")
            print(f"  Checked out: {pool.checkedout()}")
            print(f"  Overflow: {pool.overflow()}")
            
            if pool.checkedout() == pool.size():
                self.recommendations.append("Connection pool exhausted - increase pool size or find connection leaks")
        
        except Exception as e:
            print(f"\n⚠️  Database profiling failed: {str(e)}")
        
        print()
    
    async def inspect_component(self, component: str):
        """Deep inspection of specific component"""
        print(f"\n{'='*70}")
        print(f"  COMPONENT INSPECTION: {component.upper()}")
        print(f"{'='*70}\n")
        
        if component == "database":
            await self._inspect_database()
        elif component == "redis":
            await self._inspect_redis()
        elif component == "llm":
            await self._inspect_llm()
        elif component == "bees":
            await self._inspect_bees()
        elif component == "queue":
            await self._inspect_queue()
        else:
            print(f"❌ Unknown component: {component}")
            print(f"   Available: database, redis, llm, bees, queue")
    
    async def _inspect_database(self):
        """Inspect database in detail"""
        try:
            from app.db.base import engine
            from sqlalchemy import text, inspect
            
            print("🔍 Database Inspection:\n")
            
            # Connection info
            print(f"URL: {str(engine.url).replace(engine.url.password or '', '****')}")
            print(f"Driver: {engine.driver}")
            print(f"Pool Size: {engine.pool.size()}")
            print()
            
            # Table analysis
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"📊 Tables ({len(tables)}):")
            with engine.connect() as conn:
                for table in tables:
                    # Row count
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    
                    # Table size (PostgreSQL specific)
                    try:
                        size_result = conn.execute(text(f"SELECT pg_size_pretty(pg_total_relation_size('{table}'))"))
                        size = size_result.scalar()
                    except:
                        size = "N/A"
                    
                    print(f"  • {table}: {count:,} rows, {size}")
            
            # Index analysis
            print(f"\n📇 Indexes:")
            for table in tables[:5]:  # First 5 tables
                indexes = inspector.get_indexes(table)
                if indexes:
                    print(f"  {table}:")
                    for idx in indexes:
                        print(f"    - {idx['name']}: {idx['column_names']}")
        
        except Exception as e:
            print(f"❌ Database inspection failed: {str(e)}")
    
    async def _inspect_redis(self):
        """Inspect Redis in detail"""
        try:
            from app.core.redis_message_bus import RedisMessageBus
            
            bus = RedisMessageBus()
            await bus.initialize()
            
            if not bus.initialized:
                print("❌ Redis not initialized")
                return
            
            print("🔍 Redis Inspection:\n")
            
            # Server info
            health = await bus.health_check()
            print(f"Status: {'Healthy' if health.get('healthy') else 'Unhealthy'}")
            print(f"Clients: {health.get('connected_clients', 'N/A')}")
            print(f"Memory: {health.get('used_memory_human', 'N/A')}")
            print(f"Uptime: {health.get('uptime_in_seconds', 0)}s")
            print()
            
            # Queue sizes
            print("📬 Message Queues:")
            from app.bees.manager import BeeManager
            manager = BeeManager()
            await manager.initialize()
            
            for bee_name in list(manager.bees.keys())[:10]:  # First 10
                queue_size = await bus.get_queue_size(bee_name)
                if queue_size['total'] > 0:
                    print(f"  • {bee_name}: {queue_size['total']} messages ({queue_size['priority']} priority)")
        
        except Exception as e:
            print(f"❌ Redis inspection failed: {str(e)}")
    
    async def _inspect_llm(self):
        """Inspect LLM configuration"""
        try:
            from app.llm.abstraction import LLMAbstraction
            
            llm = LLMAbstraction()
            await llm.initialize()
            
            print("🔍 LLM Inspection:\n")
            
            print(f"Default Provider: {llm.current_provider}")
            print(f"Available Providers: {list(llm.providers.keys())}")
            print()
            
            # Costs
            print("💰 Cost Tracking:")
            print(f"  Total: ${llm.costs['total']:.6f}")
            for provider, cost in llm.costs['by_provider'].items():
                print(f"  {provider}: ${cost:.6f}")
            print()
            
            # Test connectivity
            print("🔌 Connectivity Test:")
            for provider_name in llm.providers.keys():
                try:
                    await llm.switch_provider(provider_name)
                    response = await llm.generate("Say OK", max_tokens=5)
                    print(f"  ✅ {provider_name}: Working")
                except Exception as e:
                    print(f"  ❌ {provider_name}: {str(e)[:50]}")
        
        except Exception as e:
            print(f"❌ LLM inspection failed: {str(e)}")
    
    async def _inspect_bees(self):
        """Inspect bee status"""
        try:
            from app.bees.manager import BeeManager
            
            manager = BeeManager()
            await manager.initialize()
            
            print("🔍 Bee Inspection:\n")
            print(f"Total Bees: {len(manager.bees)}")
            print()
            
            print("🐝 Bee Status:")
            for bee_name, bee in manager.bees.items():
                llm_enabled = "🧠" if hasattr(bee, 'llm') and bee.llm else ""
                print(f"  • {bee_name} {llm_enabled}")
                print(f"    Type: {type(bee).__name__}")
                print(f"    ID: {bee.bee_id}")
        
        except Exception as e:
            print(f"❌ Bee inspection failed: {str(e)}")
    
    async def _inspect_queue(self):
        """Inspect message queue"""
        try:
            from app.core.message_bus import MessageBus
            
            bus = MessageBus()
            await bus.initialize()
            
            print("🔍 Message Queue Inspection:\n")
            
            # This would need implementation in MessageBus
            print("Queue statistics would appear here")
        
        except Exception as e:
            print(f"❌ Queue inspection failed: {str(e)}")
    
    def print_recommendations(self):
        """Print all recommendations"""
        if self.recommendations:
            print(f"\n{'='*70}")
            print(f"  💡 RECOMMENDATIONS")
            print(f"{'='*70}\n")
            
            for i, rec in enumerate(self.recommendations, 1):
                print(f"{i}. {rec}")
            print()


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="OMK Hive Advanced Debugging")
    parser.add_argument("--logs", action="store_true", help="Analyze recent logs")
    parser.add_argument("--hours", type=int, default=1, help="Hours of logs to analyze")
    parser.add_argument("--trace", type=str, help="Trace specific error keyword")
    parser.add_argument("--profile", action="store_true", help="Performance profiling")
    parser.add_argument("--inspect", type=str, help="Inspect component (database, redis, llm, bees, queue)")
    parser.add_argument("--all", action="store_true", help="Run all diagnostic tools")
    
    args = parser.parse_args()
    
    analyzer = DebugAnalyzer()
    
    if args.all or args.logs:
        await analyzer.analyze_logs(hours=args.hours)
    
    if args.trace:
        await analyzer.trace_error(args.trace)
    
    if args.all or args.profile:
        await analyzer.profile_performance()
    
    if args.inspect:
        await analyzer.inspect_component(args.inspect)
    
    if args.all:
        # Run all inspections
        for component in ["database", "redis", "llm", "bees"]:
            await analyzer.inspect_component(component)
    
    # Print recommendations
    analyzer.print_recommendations()
    
    if not any([args.logs, args.trace, args.profile, args.inspect, args.all]):
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
