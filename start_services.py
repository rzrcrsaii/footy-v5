#!/usr/bin/env python3
"""
Footy-Brain Services Launcher
Tüm servisleri başlatır ve logları izler.
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import psutil

# ANSI renk kodları
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class ServiceManager:
    def __init__(self):
        self.services: Dict[str, Dict] = {}
        self.running = True
        self.project_root = Path(__file__).parent
        
    def log(self, service_name: str, message: str, level: str = "INFO"):
        """Renkli log mesajı yazdır."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Renk seçimi
        if level == "ERROR":
            color = Colors.RED
        elif level == "WARN":
            color = Colors.YELLOW
        elif level == "SUCCESS":
            color = Colors.GREEN
        elif service_name == "DASHBOARD":
            color = Colors.CYAN
        elif service_name == "API":
            color = Colors.BLUE
        else:
            color = Colors.WHITE
            
        print(f"{color}[{timestamp}] {service_name:>10} | {message}{Colors.RESET}")
    
    def start_service(self, name: str, command: List[str], cwd: str, port: int):
        """Bir servisi başlat."""
        try:
            self.log(name, f"Starting service on port {port}...", "INFO")

            # Windows için environment ayarları
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            # Process'i başlat
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env,
                shell=True  # Windows için shell=True
            )
            
            # Service bilgilerini kaydet
            self.services[name] = {
                'process': process,
                'port': port,
                'command': ' '.join(command),
                'cwd': cwd,
                'start_time': datetime.now()
            }
            
            # Log okuma thread'i başlat
            log_thread = threading.Thread(
                target=self._read_logs,
                args=(name, process),
                daemon=True
            )
            log_thread.start()
            
            self.log(name, f"Service started (PID: {process.pid})", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(name, f"Failed to start: {e}", "ERROR")
            return False
    
    def _read_logs(self, service_name: str, process: subprocess.Popen):
        """Process loglarını oku ve yazdır."""
        try:
            for line in iter(process.stdout.readline, ''):
                if not self.running:
                    break
                    
                line = line.strip()
                if line:
                    # Log seviyesini belirle
                    if "ERROR" in line.upper() or "FAILED" in line.upper():
                        level = "ERROR"
                    elif "WARN" in line.upper():
                        level = "WARN"
                    elif "✓" in line or "SUCCESS" in line.upper() or "Ready" in line:
                        level = "SUCCESS"
                    else:
                        level = "INFO"
                    
                    # Uzun logları kısalt
                    if len(line) > 120:
                        line = line[:117] + "..."
                    
                    self.log(service_name, line, level)
                    
        except Exception as e:
            if self.running:
                self.log(service_name, f"Log reading error: {e}", "ERROR")
    
    def check_port(self, port: int) -> bool:
        """Port'un kullanımda olup olmadığını kontrol et."""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        except:
            return False
    
    def wait_for_service(self, name: str, port: int, timeout: int = 30):
        """Servisin hazır olmasını bekle."""
        self.log(name, f"Waiting for service on port {port}...", "INFO")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_port(port):
                self.log(name, f"Service is ready on port {port}", "SUCCESS")
                return True
            time.sleep(1)
        
        self.log(name, f"Service not ready after {timeout}s", "WARN")
        return False
    
    def stop_all_services(self):
        """Tüm servisleri durdur."""
        self.running = False
        self.log("SYSTEM", "Stopping all services...", "WARN")
        
        for name, service in self.services.items():
            try:
                process = service['process']
                if process.poll() is None:  # Hala çalışıyor
                    self.log(name, "Stopping service...", "WARN")
                    process.terminate()
                    
                    # 5 saniye bekle, sonra kill
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.log(name, "Force killing service...", "ERROR")
                        process.kill()
                    
                    self.log(name, "Service stopped", "SUCCESS")
            except Exception as e:
                self.log(name, f"Error stopping: {e}", "ERROR")
    
    def show_status(self):
        """Servislerin durumunu göster."""
        print(f"\n{Colors.BOLD}=== SERVICE STATUS ==={Colors.RESET}")
        
        for name, service in self.services.items():
            process = service['process']
            uptime = datetime.now() - service['start_time']
            
            if process.poll() is None:
                status = f"{Colors.GREEN}RUNNING{Colors.RESET}"
            else:
                status = f"{Colors.RED}STOPPED{Colors.RESET}"
            
            print(f"{name:>10} | {status} | Port: {service['port']} | Uptime: {str(uptime).split('.')[0]}")
        
        print(f"\n{Colors.BOLD}=== ENDPOINTS ==={Colors.RESET}")
        print(f"Dashboard:  {Colors.CYAN}http://localhost:3000{Colors.RESET}")
        print(f"API Docs:   {Colors.BLUE}http://localhost:8001/docs{Colors.RESET}")
        print(f"Health:     {Colors.BLUE}http://localhost:8001/health{Colors.RESET}")
        print(f"WebSocket:  {Colors.MAGENTA}ws://localhost:8001/ws/live/general{Colors.RESET}")
        print()

def signal_handler(signum, frame):
    """Ctrl+C yakalandığında servisleri durdur."""
    print(f"\n{Colors.YELLOW}Received signal {signum}, shutting down...{Colors.RESET}")
    manager.stop_all_services()
    sys.exit(0)

def main():
    global manager
    manager = ServiceManager()
    
    # Signal handler'ları ayarla
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("╔══════════════════════════════════════╗")
    print("║        FOOTY-BRAIN LAUNCHER          ║")
    print("║     Starting All Services...         ║")
    print("╚══════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    try:
        # 1. API Server'ı başlat
        api_success = manager.start_service(
            name="API",
            command=["python", "simple_main.py"],
            cwd=str(manager.project_root / "apps" / "api-server"),
            port=8001
        )
        
        if api_success:
            manager.wait_for_service("API", 8001, timeout=15)
        
        # 2. Dashboard'u başlat
        dashboard_success = manager.start_service(
            name="DASHBOARD",
            command=["cmd", "/c", "pnpm dev"],
            cwd=str(manager.project_root / "apps" / "web-dashboard"),
            port=3000
        )
        
        if dashboard_success:
            manager.wait_for_service("DASHBOARD", 3000, timeout=20)
        
        # Durum göster
        time.sleep(2)
        manager.show_status()
        
        # Ana döngü - logları izle
        manager.log("SYSTEM", "All services started! Press Ctrl+C to stop.", "SUCCESS")
        manager.log("SYSTEM", "Monitoring logs...", "INFO")
        
        while manager.running:
            time.sleep(1)
            
            # Servislerin durumunu kontrol et
            for name, service in manager.services.items():
                if service['process'].poll() is not None:
                    manager.log(name, "Service crashed! Restarting...", "ERROR")
                    # TODO: Restart logic eklenebilir
    
    except KeyboardInterrupt:
        pass
    except Exception as e:
        manager.log("SYSTEM", f"Unexpected error: {e}", "ERROR")
    finally:
        manager.stop_all_services()

if __name__ == "__main__":
    main()
