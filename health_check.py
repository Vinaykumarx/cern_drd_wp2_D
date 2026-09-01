#!/usr/bin/env python3
from core.bootstrap import require_bootstrap; require_bootstrap()
"""
🏥 PROJECT HEALTH CHECK
Monitor all systems and report status in real-time
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

class HealthMonitor:
    def __init__(self):
        self.root = Path(__file__).parent
        self.results = {}
        
    def check_port(self, port: int) -> bool:
        """Check if a port is listening"""
        try:
            result = subprocess.run(
                f"lsof -ti :{port}",
                shell=True,
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def check_file(self, path: str, required=True) -> bool:
        """Check if a file exists"""
        exists = (self.root / path).exists()
        return exists if required else True
    
    def check_import(self, module: str) -> bool:
        """Check if a Python module can be imported"""
        try:
            __import__(module)
            return True
        except ImportError:
            return False
    
    def get_process_info(self, port: int) -> dict:
        """Get process info for a port"""
        try:
            result = subprocess.run(
                f"lsof -i :{port} | tail -1",
                shell=True,
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.stdout:
                parts = result.stdout.split()
                if len(parts) >= 9:
                    return {
                        "process": parts[0],
                        "pid": parts[1],
                        "memory": parts[9]
                    }
        except:
            pass
        return None
    
    def test_endpoint(self, url: str) -> bool:
        """Test if an HTTP endpoint responds"""
        try:
            result = subprocess.run(
                f"curl -s -m 2 {url} > /dev/null 2>&1",
                shell=True,
                timeout=3
            )
            return result.returncode == 0
        except:
            return False
    
    def run_checks(self):
        """Run all health checks"""
        print("\n" + "="*60)
        print("🏥 PROJECT HEALTH CHECK")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
        
        # Backend checks
        print("📦 BACKEND (RAG Pipeline)")
        print("-" * 60)
        backend_port = 8000
        backend_running = self.check_port(backend_port)
        print(f"  Port 8000 Listening: {'✅ YES' if backend_running else '❌ NO'}")
        
        if backend_running:
            proc = self.get_process_info(backend_port)
            if proc:
                print(f"  Process: {proc['process']} (PID: {proc['pid']})")
                print(f"  Memory: {proc['memory']}")
            
            endpoint_ok = self.test_endpoint("http://localhost:8000/docs")
            print(f"  API Endpoint: {'✅ RESPONSIVE' if endpoint_ok else '⚠️ SLOW'}")
        else:
            print(f"  Status: ❌ NOT RUNNING")
            print(f"  Action: Start with: uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        
        # Dashboard checks
        print("\n📊 DASHBOARD (Project Management)")
        print("-" * 60)
        dashboard_port = 8888
        dashboard_running = self.check_port(dashboard_port)
        print(f"  Port 8888 Listening: {'✅ YES' if dashboard_running else '❌ NO'}")
        
        if dashboard_running:
            proc = self.get_process_info(dashboard_port)
            if proc:
                print(f"  Process: {proc['process']} (PID: {proc['pid']})")
                print(f"  Memory: {proc['memory']}")
            
            endpoint_ok = self.test_endpoint("http://localhost:8888/")
            print(f"  Web Interface: {'✅ RESPONSIVE' if endpoint_ok else '⚠️ SLOW'}")
        else:
            print(f"  Status: ❌ NOT RUNNING")
            print(f"  Action: Start with: uvicorn project_dashboard:app --host 0.0.0.0 --port 8888")
        
        # File checks
        print("\n📁 FILES & PERSISTENCE")
        print("-" * 60)
        files_to_check = [
            ("project_agent.py", "Project Agent"),
            ("project_dashboard.py", "Dashboard"),
            ("project_cli.py", "CLI Tool"),
            ("project_manager.py", "Manager"),
            ("project_tasks.json", "Task Database"),
            ("backend/main.py", "Backend"),
        ]
        
        for file_path, name in files_to_check:
            exists = self.check_file(file_path)
            print(f"  {name}: {'✅' if exists else '❌'} {file_path}")
        
        # Dependencies
        print("\n🔧 DEPENDENCIES")
        print("-" * 60)
        deps = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "lancedb",
            "torch",
            "streamlit"
        ]
        
        for dep in deps:
            ok = self.check_import(dep)
            print(f"  {dep}: {'✅' if ok else '❌'}")
        
        # Summary
        print("\n" + "="*60)
        print("📋 SUMMARY")
        print("="*60)
        
        backend_status = "✅ ONLINE" if backend_running else "❌ OFFLINE"
        dashboard_status = "✅ ONLINE" if dashboard_running else "❌ OFFLINE"
        
        print(f"\nBackend:  {backend_status}")
        print(f"Dashboard: {dashboard_status}")
        
        if backend_running and dashboard_running:
            print("\n✨ ALL SYSTEMS OPERATIONAL ✨")
            print("\nAccess:")
            print("  Dashboard: http://localhost:8888")
            print("  Backend API: http://localhost:8000/docs")
            return 0
        else:
            print("\n⚠️  SOME SYSTEMS NOT RUNNING")
            if not backend_running:
                print("\nTo start backend:")
                print("  cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration")
                print("  uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload")
            if not dashboard_running:
                print("\nTo start dashboard:")
                print("  cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration")
                print("  uvicorn project_dashboard:app --host 0.0.0.0 --port 8888 --reload")
            return 1
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    monitor = HealthMonitor()
    sys.exit(monitor.run_checks())
