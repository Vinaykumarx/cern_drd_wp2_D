#!/usr/bin/env python3
"""
🎯 REAL-TIME PROJECT TRACKER
Monitors all running services, tasks, and project health in real-time
"""

import os
import json
import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import socket
import requests

class RealTimeTracker:
    """Tracks project status in real-time"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tasks_file = self.project_root / "project_tasks.json"
        self.backend_port = 8000
        self.dashboard_port = 8888
        self.frontend_port = 3000
        
    def check_port_open(self, port: int) -> bool:
        """Check if a port is open and listening"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "all_running": True
        }
        
        services = {
            "Backend RAG API": (self.backend_port, "http://localhost:8000/docs"),
            "Project Dashboard": (self.dashboard_port, "http://localhost:8888"),
            "Frontend": (self.frontend_port, "http://localhost:3000"),
        }
        
        for service_name, (port, url) in services.items():
            is_open = self.check_port_open(port)
            status["services"][service_name] = {
                "port": port,
                "running": is_open,
                "url": url,
                "status": "🟢 RUNNING" if is_open else "🔴 STOPPED"
            }
            if not is_open:
                status["all_running"] = False
        
        return status
    
    def load_tasks(self) -> List[Dict]:
        """Load task data"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file) as f:
                    data = json.load(f)
                    # Handle both list and dict formats
                    if isinstance(data, dict):
                        # If it's a dict, extract task list
                        if "tasks" in data:
                            return data.get("tasks", [])
                        else:
                            # It's a dict of tasks by ID
                            return list(data.values())
                    elif isinstance(data, list):
                        return data
        except Exception:
            pass
        return []
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get task summary statistics"""
        tasks = self.load_tasks()
        summary = {
            "total": len(tasks),
            "not_started": 0,
            "in_progress": 0,
            "completed": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
        }
        
        for task in tasks:
            # Parse status
            status = task.get("status", "Backlog")
            if "Backlog" in status or "not-started" in status:
                summary["not_started"] += 1
            elif "Progress" in status or "In Progress" in status or "🔄" in status:
                summary["in_progress"] += 1
            elif "Done" in status or "✅" in status or "completed" in status:
                summary["completed"] += 1
            
            # Parse priority
            priority = task.get("priority", "Medium")
            if "Critical" in priority or "🔴" in priority:
                summary["critical"] += 1
            elif "High" in priority or "🟠" in priority:
                summary["high"] += 1
            elif "Medium" in priority or "🟡" in priority:
                summary["medium"] += 1
            elif "Low" in priority or "🟢" in priority:
                summary["low"] += 1
        
        return summary
    
    def display_real_time_dashboard(self):
        """Display real-time dashboard in terminal"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("\n" + "="*80)
        print("🎯 REAL-TIME PROJECT TRACKER")
        print("="*80)
        
        # Services Status
        service_status = self.get_service_status()
        print("\n📡 SERVICES STATUS:")
        print("-" * 80)
        
        for service_name, info in service_status["services"].items():
            status_icon = info["status"]
            port = info["port"]
            url = info["url"]
            print(f"  {status_icon:20} | Port {port:5} | {service_name:25} | {url}")
        
        # Task Summary
        task_summary = self.get_task_summary()
        print("\n📋 TASK SUMMARY:")
        print("-" * 80)
        print(f"  Total Tasks: {task_summary['total']}")
        print(f"    ✅ Completed:    {task_summary['completed']}")
        print(f"    🔄 In Progress:  {task_summary['in_progress']}")
        print(f"    ⏳ Not Started:  {task_summary['not_started']}")
        print()
        print(f"  By Priority:")
        print(f"    🔴 Critical:  {task_summary['critical']} tasks")
        print(f"    🟠 High:      {task_summary['high']} tasks")
        print(f"    🟡 Medium:    {task_summary['medium']} tasks")
        print(f"    🟢 Low:       {task_summary['low']} tasks")
        
        # Overall Status
        print("\n🎯 OVERALL STATUS:")
        print("-" * 80)
        if service_status["all_running"]:
            print("  ✅ ALL SYSTEMS OPERATIONAL - Agent can track everything")
        else:
            print("  ⚠️  Some services not running")
        
        progress = (task_summary['completed'] / task_summary['total'] * 100) if task_summary['total'] > 0 else 0
        print(f"  📈 Project Progress: {progress:.1f}% ({task_summary['completed']}/{task_summary['total']} tasks)")
        
        # Quick Links
        print("\n🚀 QUICK LINKS:")
        print("-" * 80)
        print("  🌐 Dashboard:        http://localhost:8888")
        print("  📚 API Docs:         http://localhost:8000/docs")
        print("  💻 Frontend:         http://localhost:3000")
        print("  📊 Live Metrics:     http://localhost:8888/metrics")
        print("  👥 Team View:        http://localhost:8888/team")
        print("  📋 Task Board:       http://localhost:8888/tasks")
        
        # How to Use
        print("\n💡 NEXT STEPS:")
        print("-" * 80)
        print("  1. Open: http://localhost:8888 (Project Dashboard)")
        print("  2. View tasks and assign to team")
        print("  3. Track progress on kanban board")
        print("  4. Update task status as work completes")
        print("  5. Review metrics and health scores")
        
        print("\n📝 To manage tasks, run:")
        print("  python project_cli.py --list          # See all tasks")
        print("  python project_cli.py --update <id>   # Update task status")
        print("  python project_cli.py --assign <id>   # Assign to team member")
        
        print("\n" + "="*80)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
    
    def run_continuous_monitoring(self, interval: int = 30):
        """Run continuous monitoring"""
        try:
            while True:
                self.display_real_time_dashboard()
                print(f"Refreshing in {interval} seconds... (Press Ctrl+C to stop)")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n✅ Monitoring stopped")
            sys.exit(0)
    
    def get_json_status(self) -> str:
        """Get status as JSON"""
        service_status = self.get_service_status()
        task_summary = self.get_task_summary()
        
        data = {
            "timestamp": service_status["timestamp"],
            "services": service_status["services"],
            "tasks": task_summary,
            "all_running": service_status["all_running"]
        }
        return json.dumps(data, indent=2)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-time Project Tracker")
    parser.add_argument("--once", action="store_true", help="Show status once and exit")
    parser.add_argument("--continuous", action="store_true", help="Continuous monitoring (default)")
    parser.add_argument("--interval", type=int, default=30, help="Refresh interval in seconds")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--api", action="store_true", help="Start as API server")
    
    args = parser.parse_args()
    
    tracker = RealTimeTracker()
    
    if args.json:
        print(tracker.get_json_status())
    elif args.api:
        # Start as API server
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        import uvicorn
        
        app = FastAPI(title="Real-Time Tracker API")
        
        @app.get("/status")
        def get_status():
            service_status = tracker.get_service_status()
            task_summary = tracker.get_task_summary()
            return {
                "services": service_status["services"],
                "tasks": task_summary,
                "all_running": service_status["all_running"]
            }
        
        @app.get("/health")
        def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @app.get("/metrics")
        def get_metrics():
            service_status = tracker.get_service_status()
            task_summary = tracker.get_task_summary()
            return {
                "services_running": sum(1 for s in service_status["services"].values() if s["running"]),
                "services_total": len(service_status["services"]),
                "tasks_completed": task_summary["completed"],
                "tasks_total": task_summary["total"],
                "progress_percent": (task_summary["completed"] / task_summary["total"] * 100) if task_summary["total"] > 0 else 0
            }
        
        print("🚀 Starting Real-Time Tracker API on http://localhost:8999")
        uvicorn.run(app, host="0.0.0.0", port=8999)
    elif args.once:
        tracker.display_real_time_dashboard()
    else:
        tracker.run_continuous_monitoring(interval=args.interval)


if __name__ == "__main__":
    main()
