#!/usr/bin/env python3
"""
OMK Hive - Master Management Script

Unified interface for all system operations.

Usage:
    python3 manage.py start          # Start system
    python3 manage.py stop           # Stop system
    python3 manage.py restart        # Restart system
    python3 manage.py status         # Show status
    python3 manage.py health         # Health check
    python3 manage.py debug          # Debug mode
    python3 manage.py logs           # View logs
"""
import asyncio
import sys
import subprocess
from pathlib import Path
from typing import List
import argparse

sys.path.insert(0, str(Path(__file__).parent))

import structlog

logger = structlog.get_logger(__name__)


class SystemManager:
    """Master system management interface"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.python = sys.executable
    
    async def start(self, **kwargs):
        """Start the system"""
        print("🚀 Starting OMK Hive...")
        
        cmd = [self.python, "start.py"]
        
        if kwargs.get('environment'):
            cmd.extend(['--environment', kwargs['environment']])
        if kwargs.get('debug'):
            cmd.append('--debug')
        if kwargs.get('component'):
            cmd.extend(['--component', kwargs['component']])
        
        return self._run_command(cmd)
    
    async def stop(self, **kwargs):
        """Stop the system"""
        print("🛑 Stopping OMK Hive...")
        
        cmd = [self.python, "stop.py"]
        
        if kwargs.get('force'):
            cmd.append('--force')
        if kwargs.get('component'):
            cmd.extend(['--component', kwargs['component']])
        
        return self._run_command(cmd)
    
    async def restart(self, **kwargs):
        """Restart the system"""
        print("🔄 Restarting OMK Hive...")
        
        cmd = [self.python, "reboot.py"]
        
        if kwargs.get('quick'):
            cmd.append('--quick')
        if kwargs.get('environment'):
            cmd.extend(['--environment', kwargs['environment']])
        
        return self._run_command(cmd)
    
    async def status(self, **kwargs):
        """Show system status"""
        cmd = [self.python, "status.py"]
        
        if kwargs.get('refresh'):
            cmd.extend(['--refresh', str(kwargs['refresh'])])
        
        return self._run_command(cmd)
    
    async def health(self, **kwargs):
        """Run health check"""
        cmd = [self.python, "health_check.py"]
        
        if kwargs.get('component'):
            cmd.extend(['--component', kwargs['component']])
        if kwargs.get('watch'):
            cmd.append('--watch')
        
        return self._run_command(cmd)
    
    async def debug(self, **kwargs):
        """Run debugging tools"""
        cmd = [self.python, "debug.py"]
        
        if kwargs.get('logs'):
            cmd.append('--logs')
        if kwargs.get('profile'):
            cmd.append('--profile')
        if kwargs.get('inspect'):
            cmd.extend(['--inspect', kwargs['inspect']])
        if kwargs.get('all'):
            cmd.append('--all')
        
        return self._run_command(cmd)
    
    async def logs(self, **kwargs):
        """View logs"""
        log_file = kwargs.get('file', 'queen.log')
        log_path = self.base_dir / "logs" / log_file
        
        if not log_path.exists():
            print(f"❌ Log file not found: {log_path}")
            return 1
        
        lines = kwargs.get('lines', 50)
        
        # Use tail command
        cmd = ['tail', '-n', str(lines), str(log_path)]
        
        if kwargs.get('follow'):
            cmd.insert(1, '-f')
        
        return subprocess.call(cmd)
    
    async def test(self, **kwargs):
        """Run tests"""
        print("🧪 Running tests...")
        
        test_type = kwargs.get('type', 'pipeline')
        
        if test_type == 'pipeline':
            cmd = [self.python, "full_pipeline_test.py"]
        elif test_type == 'private_sale':
            cmd = [self.python, "test_private_sale.py"]
        elif test_type == 'integration':
            cmd = [self.python, "-m", "pytest", "integration_tests/", "-v"]
        else:
            print(f"❌ Unknown test type: {test_type}")
            return 1
        
        return self._run_command(cmd)
    
    async def db(self, **kwargs):
        """Database operations"""
        action = kwargs.get('action', 'status')
        
        if action == 'setup':
            cmd = [self.python, "setup_database.py"]
        elif action == 'migrate':
            cmd = ['alembic', 'upgrade', 'head']
        elif action == 'rollback':
            cmd = ['alembic', 'downgrade', '-1']
        elif action == 'status':
            cmd = ['alembic', 'current']
        else:
            print(f"❌ Unknown database action: {action}")
            print("   Available: setup, migrate, rollback, status")
            return 1
        
        return self._run_command(cmd)
    
    async def deploy(self, **kwargs):
        """Deployment operations"""
        target = kwargs.get('target', 'local')
        
        print(f"🚀 Deploying to {target}...")
        
        if target == 'local':
            # Local deployment
            await self.stop(force=True)
            await asyncio.sleep(2)
            await self.start(environment='development')
        
        elif target == 'gcp':
            # GCP deployment with Terraform
            print("📦 Deploying to Google Cloud Platform...")
            print("   Using Terraform...")
            
            terraform_dir = self.base_dir / "terraform"
            if not terraform_dir.exists():
                print(f"❌ Terraform directory not found: {terraform_dir}")
                return 1
            
            # Run terraform
            commands = [
                ['terraform', 'init'],
                ['terraform', 'plan'],
                ['terraform', 'apply', '-auto-approve'] if kwargs.get('auto_approve') else ['terraform', 'apply']
            ]
            
            for cmd in commands:
                print(f"\n$ {' '.join(cmd)}")
                result = subprocess.call(cmd, cwd=terraform_dir)
                if result != 0:
                    print(f"❌ Command failed: {' '.join(cmd)}")
                    return result
        
        elif target == 'docker':
            # Docker deployment
            print("🐳 Building Docker image...")
            cmd = ['docker', 'build', '-t', 'omk-queen-ai:latest', '.']
            return self._run_command(cmd)
        
        else:
            print(f"❌ Unknown deployment target: {target}")
            print("   Available: local, gcp, docker")
            return 1
        
        return 0
    
    def _run_command(self, cmd: List[str]) -> int:
        """Run command and return exit code"""
        try:
            return subprocess.call(cmd, cwd=self.base_dir)
        except KeyboardInterrupt:
            print("\n⚠️  Command interrupted")
            return 130
        except Exception as e:
            print(f"❌ Command failed: {str(e)}")
            return 1
    
    def print_help(self):
        """Print help message"""
        help_text = """
╔════════════════════════════════════════════════════════════════════════╗
║                     OMK HIVE - SYSTEM MANAGEMENT                       ║
╚════════════════════════════════════════════════════════════════════════╝

📋 BASIC COMMANDS:
  start          Start the system
  stop           Stop the system
  restart        Restart the system
  status         Show real-time status dashboard
  
🏥 MONITORING & DEBUGGING:
  health         Run comprehensive health check
  debug          Advanced debugging tools
  logs           View system logs
  
🧪 TESTING:
  test           Run tests (--type pipeline|private_sale|integration)
  
💾 DATABASE:
  db setup       Initialize database
  db migrate     Run migrations
  db rollback    Rollback last migration
  db status      Show migration status
  
🚀 DEPLOYMENT:
  deploy local   Deploy locally
  deploy gcp     Deploy to Google Cloud Platform
  deploy docker  Build Docker image
  
📚 EXAMPLES:
  # Start in production mode
  python3 manage.py start --environment production
  
  # Watch system status
  python3 manage.py status --refresh 5
  
  # Health check specific component
  python3 manage.py health --component database
  
  # View live logs
  python3 manage.py logs --follow
  
  # Run all debugging tools
  python3 manage.py debug --all
  
  # Deploy to GCP
  python3 manage.py deploy gcp --auto-approve

💡 For detailed help on any command:
  python3 manage.py <command> --help
        """
        print(help_text)


async def main():
    """Main entry point"""
    manager = SystemManager()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="OMK Hive System Management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the system')
    start_parser.add_argument('--environment', '-e', choices=['development', 'staging', 'production'], default='development')
    start_parser.add_argument('--debug', '-d', action='store_true')
    start_parser.add_argument('--component', '-c', help='Start specific component')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop the system')
    stop_parser.add_argument('--force', '-f', action='store_true')
    stop_parser.add_argument('--component', '-c', help='Stop specific component')
    
    # Restart command
    restart_parser = subparsers.add_parser('restart', help='Restart the system')
    restart_parser.add_argument('--quick', '-q', action='store_true')
    restart_parser.add_argument('--environment', '-e', choices=['development', 'staging', 'production'], default='development')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.add_argument('--refresh', '-r', type=int, default=2)
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Health check')
    health_parser.add_argument('--component', '-c')
    health_parser.add_argument('--watch', '-w', action='store_true')
    
    # Debug command
    debug_parser = subparsers.add_parser('debug', help='Debug tools')
    debug_parser.add_argument('--logs', action='store_true')
    debug_parser.add_argument('--profile', action='store_true')
    debug_parser.add_argument('--inspect', choices=['database', 'redis', 'llm', 'bees', 'queue'])
    debug_parser.add_argument('--all', action='store_true')
    
    # Logs command
    logs_parser = subparsers.add_parser('logs', help='View logs')
    logs_parser.add_argument('--file', '-f', default='queen.log')
    logs_parser.add_argument('--lines', '-n', type=int, default=50)
    logs_parser.add_argument('--follow', action='store_true')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--type', '-t', choices=['pipeline', 'private_sale', 'integration'], default='pipeline')
    
    # DB command
    db_parser = subparsers.add_parser('db', help='Database operations')
    db_parser.add_argument('action', choices=['setup', 'migrate', 'rollback', 'status'])
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Deploy system')
    deploy_parser.add_argument('target', choices=['local', 'gcp', 'docker'])
    deploy_parser.add_argument('--auto-approve', action='store_true')
    
    args = parser.parse_args()
    
    if not args.command:
        manager.print_help()
        return 0
    
    # Execute command
    command_func = getattr(manager, args.command, None)
    if command_func:
        kwargs = vars(args)
        kwargs.pop('command')
        exit_code = await command_func(**kwargs)
        return exit_code if exit_code is not None else 0
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Cancelled")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
