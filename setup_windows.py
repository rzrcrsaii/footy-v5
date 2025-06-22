#!/usr/bin/env python3
"""
Footy-Brain v5 Windows Setup Script
Simplified setup for Windows development environment.
"""

import os
import sys
import subprocess
import time
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Custom port configuration to avoid conflicts
PORTS = {
    'web_dashboard': 3001,
    'api_server': 8001,
    'postgres': 5433,
    'redis': 6380,
    'grafana': 3002
}

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message: str, status: str = "INFO") -> None:
    """Print colored status message."""
    color_map = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "STEP": Colors.PURPLE
    }
    color = color_map.get(status, Colors.WHITE)
    print(f"{color}[{status}]{Colors.END} {message}")

def run_command(command: str, cwd: Optional[str] = None, check: bool = True) -> Tuple[bool, str]:
    """Run shell command and return success status and output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def check_prerequisites() -> bool:
    """Check if all required tools are installed."""
    print_status("Checking prerequisites...", "STEP")
    
    required_tools = {
        'docker': 'Docker Desktop',
        'docker-compose': 'Docker Compose',
        'python': 'Python 3.11+',
        'node': 'Node.js 18+',
        'pnpm': 'pnpm 8+'
    }
    
    missing_tools = []
    
    for tool, name in required_tools.items():
        success, output = run_command(f"where {tool}", check=False)
        if success:
            print_status(f"✓ {name} found", "SUCCESS")
        else:
            print_status(f"✗ {name} not found", "ERROR")
            missing_tools.append(name)
    
    if missing_tools:
        print_status(f"Missing tools: {', '.join(missing_tools)}", "ERROR")
        print_status("Please install missing tools and run setup again.", "ERROR")
        return False
    
    return True

def create_env_file() -> bool:
    """Create .env file with custom port configuration."""
    print_status("Creating .env file with custom ports...", "STEP")
    
    env_content = f"""# Footy-Brain v5 Environment Configuration (Custom Ports)
DATABASE_URL=postgresql://footy:footy_secure_2024@localhost:{PORTS['postgres']}/footy
DB_PASSWORD=footy_secure_2024
REDIS_URL=redis://localhost:{PORTS['redis']}/0
CELERY_BROKER_URL=redis://localhost:{PORTS['redis']}/1
CELERY_RESULT_BACKEND=redis://localhost:{PORTS['redis']}/2
RAPIDAPI_KEY=your_rapidapi_key_here
JWT_SECRET=footy_jwt_secret_2024
API_HOST=0.0.0.0
API_PORT={PORTS['api_server']}
ENVIRONMENT=development
DEBUG=true
LIVE_WORKER_INTERVAL=10
LIVE_WORKER_CONCURRENCY=5
FRAME_WORKER_INTERVAL=60
CELERY_WORKER_CONCURRENCY=4
NEXT_PUBLIC_API_URL=http://localhost:{PORTS['api_server']}
NEXT_PUBLIC_WS_URL=ws://localhost:{PORTS['api_server']}
NEXTAUTH_SECRET=footy_nextauth_secret_2024
NEXTAUTH_URL=http://localhost:{PORTS['web_dashboard']}
GRAFANA_PASSWORD=admin
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print_status("✓ .env file created successfully", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"✗ Failed to create .env file: {e}", "ERROR")
        return False

def update_docker_compose() -> bool:
    """Update docker-compose.yml with custom ports."""
    print_status("Updating docker-compose.yml with custom ports...", "STEP")
    
    try:
        # Read original docker-compose.yml
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        
        # Create backup
        shutil.copy('docker-compose.yml', 'docker-compose.yml.backup')
        
        # Replace ports
        replacements = {
            '"5432:5432"': f'"{PORTS["postgres"]}:5432"',
            '"6379:6379"': f'"{PORTS["redis"]}:6379"',
            '"8000:8000"': f'"{PORTS["api_server"]}:8000"',
            '"3000:3000"': f'"{PORTS["web_dashboard"]}:3000"',
            '"3001:3000"': f'"{PORTS["grafana"]}:3000"'
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Write updated content
        with open('docker-compose.yml', 'w') as f:
            f.write(content)
        
        print_status("✓ docker-compose.yml updated successfully", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"✗ Failed to update docker-compose.yml: {e}", "ERROR")
        return False

def start_infrastructure() -> bool:
    """Start PostgreSQL and Redis containers."""
    print_status("Starting infrastructure services...", "STEP")
    
    # Stop any existing containers
    run_command("docker-compose down", check=False)
    
    # Start PostgreSQL and Redis
    success, output = run_command("docker-compose up -d pg redis")
    if not success:
        print_status(f"✗ Failed to start infrastructure: {output}", "ERROR")
        return False
    
    # Wait for services to be ready
    print_status("Waiting for services to be ready...", "INFO")
    time.sleep(15)
    
    print_status("✓ Infrastructure services started", "SUCCESS")
    return True

def install_frontend_deps() -> bool:
    """Install frontend dependencies."""
    print_status("Installing frontend dependencies...", "STEP")
    
    success, output = run_command("pnpm install", cwd="apps/web-dashboard")
    if not success:
        print_status(f"✗ pnpm install failed: {output}", "ERROR")
        return False
    
    print_status("✓ Frontend dependencies installed", "SUCCESS")
    return True

def create_startup_scripts() -> bool:
    """Create Windows batch scripts for starting services."""
    print_status("Creating startup scripts...", "STEP")
    
    # API Server startup script
    api_script = f"""@echo off
echo Starting Footy-Brain API Server on port {PORTS['api_server']}...
cd apps\\api-server
python main.py
pause
"""
    
    # Web Dashboard startup script
    web_script = f"""@echo off
echo Starting Footy-Brain Web Dashboard on port {PORTS['web_dashboard']}...
cd apps\\web-dashboard
pnpm dev
pause
"""
    
    try:
        with open('start_api.bat', 'w') as f:
            f.write(api_script)
        
        with open('start_web.bat', 'w') as f:
            f.write(web_script)
        
        print_status("✓ Startup scripts created", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"✗ Failed to create startup scripts: {e}", "ERROR")
        return False

def verify_infrastructure() -> Dict[str, bool]:
    """Verify infrastructure services are running."""
    print_status("Verifying infrastructure services...", "STEP")
    
    services = {
        f"PostgreSQL (:{PORTS['postgres']})": "docker ps --filter name=footy-brain-db --filter status=running",
        f"Redis (:{PORTS['redis']})": "docker ps --filter name=footy-brain-redis --filter status=running"
    }
    
    results = {}
    for service, command in services.items():
        success, output = run_command(command, check=False)
        # Check if container is in the output
        is_running = success and "footy-brain" in output
        results[service] = is_running
        status = "SUCCESS" if is_running else "ERROR"
        symbol = "✓" if is_running else "✗"
        print_status(f"{symbol} {service}", status)
    
    return results

def print_final_summary(service_results: Dict[str, bool]) -> None:
    """Print final setup summary with instructions."""
    print("\n" + "="*80)
    print_status("🎉 FOOTY-BRAIN V5 SETUP COMPLETE!", "SUCCESS")
    print("="*80)
    
    print(f"\n{Colors.BOLD}📊 Infrastructure Status:{Colors.END}")
    for service, status in service_results.items():
        symbol = "✅" if status else "❌"
        print(f"  {symbol} {service}")
    
    print(f"\n{Colors.BOLD}🚀 Next Steps:{Colors.END}")
    print("  1. Open TWO separate Command Prompt windows")
    print("  2. In first window, run:  start_api.bat")
    print("  3. In second window, run: start_web.bat")
    print("  4. Wait for both services to start")
    
    print(f"\n{Colors.BOLD}🌐 Service URLs (Custom Ports):{Colors.END}")
    urls = [
        f"🎯 Web Dashboard:    http://localhost:{PORTS['web_dashboard']}",
        f"🔧 API Server:       http://localhost:{PORTS['api_server']}",
        f"📚 API Docs:         http://localhost:{PORTS['api_server']}/docs",
        f"💾 PostgreSQL:       localhost:{PORTS['postgres']} (footy/footy_secure_2024)",
        f"🔴 Redis:            localhost:{PORTS['redis']}",
    ]
    
    for url in urls:
        print(f"  {url}")
    
    print(f"\n{Colors.BOLD}⚠️  Important Notes:{Colors.END}")
    notes = [
        "• Add your RapidAPI key to .env file for live data",
        "• Services are running on custom ports to avoid conflicts",
        "• Use 'docker-compose down' to stop infrastructure services",
        "• Press Ctrl+C in each window to stop the services"
    ]
    
    for note in notes:
        print(f"  {note}")
    
    print(f"\n{Colors.BOLD}🔧 Manual Commands (if batch files don't work):{Colors.END}")
    print(f"  # Start API Server")
    print(f"  cd apps\\api-server && python main.py")
    print(f"  ")
    print(f"  # Start Web Dashboard")
    print(f"  cd apps\\web-dashboard && pnpm dev")
    
    print("\n" + "="*80)

def main() -> None:
    """Main setup function."""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("🏈⚡ FOOTY-BRAIN V5 WINDOWS SETUP")
    print("Real-time Football Data Platform")
    print("="*50)
    print(f"{Colors.END}")
    
    try:
        # Step 1: Check prerequisites
        if not check_prerequisites():
            sys.exit(1)
        
        # Step 2: Create environment file
        if not create_env_file():
            sys.exit(1)
        
        # Step 3: Update docker-compose.yml
        if not update_docker_compose():
            sys.exit(1)
        
        # Step 4: Install frontend dependencies
        if not install_frontend_deps():
            sys.exit(1)
        
        # Step 5: Start infrastructure
        if not start_infrastructure():
            sys.exit(1)
        
        # Step 6: Create startup scripts
        if not create_startup_scripts():
            sys.exit(1)
        
        # Step 7: Verify infrastructure
        service_results = verify_infrastructure()
        
        # Step 8: Print final summary
        print_final_summary(service_results)
        
    except KeyboardInterrupt:
        print_status("\n🛑 Setup interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"💥 Unexpected error: {e}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()
