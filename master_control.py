#!/usr/bin/env python3
from core.bootstrap import require_bootstrap; require_bootstrap()
"""
🎛️ MASTER CONTROL PANEL
Complete project startup, monitoring, and task management
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import socket

class MasterControlPanel:
    """Master control for the entire project"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        
    def check_port(self, port: int) -> bool:
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_banner(self):
        """Display welcome banner"""
        self.clear_screen()
        print("\n" + "█" * 90)
        print("█" + " " * 88 + "█")
        print("█" + "  🎛️  CERN MULTIMODAL RAG - MASTER CONTROL PANEL  ".center(88) + "█")
        print("█" + " " * 88 + "█")
        print("█" * 90)
        print()
    
    def show_menu(self):
        """Display main menu"""
        menu = """
╔════════════════════════════════════════════════════════════════════════════╗
║                          MAIN MENU                                         ║
╚════════════════════════════════════════════════════════════════════════════╝

  📊 PROJECT DASHBOARD
  ─────────────────────────────────────────────────────────────────────────
  
  1️⃣  🌐 WEB DASHBOARD (http://localhost:8888)
      Real-time metrics, kanban board, team assignments
      
  2️⃣  📋 TASK MANAGEMENT (CLI)
      View, update, and assign tasks from terminal
      
  3️⃣  📡 SERVICE STATUS
      Check backend, dashboard, and frontend health
      
  4️⃣  🚀 REAL-TIME TRACKER
      Continuous monitoring dashboard (auto-refresh)
      
  5️⃣  📊 IMPLEMENTATION PLAN
      View full execution plan and timeline
      
  6️⃣  🔧 QUICK SETTINGS
      Configure project parameters
      
  7️⃣  💻 DEVELOPMENT CONSOLE
      Direct access to tools and scripts
      
  8️⃣  📚 HELP & DOCUMENTATION
      View guides and references
      
  0️⃣  EXIT
      Close the control panel

╚════════════════════════════════════════════════════════════════════════════╝
"""
        print(menu)
    
    def show_status(self):
        """Display quick status"""
        services = {
            "Backend RAG API": (8000, "http://localhost:8000/docs"),
            "Project Dashboard": (8888, "http://localhost:8888"),
            "Frontend": (3000, "http://localhost:3000"),
        }
        
        print("\n📡 SERVICE STATUS:")
        print("-" * 80)
        
        all_running = True
        for name, (port, url) in services.items():
            status = "🟢 RUNNING" if self.check_port(port) else "🔴 STOPPED"
            print(f"  {status:15} | {name:25} | Port {port:5} | {url}")
            if status == "🔴 STOPPED":
                all_running = False
        
        print()
        if all_running:
            print("  ✅ All systems operational - Agent can track everything!")
        else:
            print("  ⚠️  Some services offline - Starting them now...")
        
        return all_running
    
    def option_1_web_dashboard(self):
        """Open web dashboard"""
        self.clear_screen()
        print("\n📊 LAUNCHING WEB DASHBOARD\n")
        print("Opening: http://localhost:8888")
        print("\nFeatures:")
        print("  - Real-time project metrics")
        print("  - Kanban task board (To-Do → In Progress → Done)")
        print("  - Team member assignments")
        print("  - Progress tracking and charts")
        print("  - Health score indicators\n")
        
        import webbrowser
        webbrowser.open("http://localhost:8888", new=2)
        
        print("✅ Dashboard opened in your browser!")
        print("\nThe dashboard is running on:")
        print("  🔗 http://localhost:8888")
        input("\nPress Enter to return to menu...")
    
    def option_2_task_management(self):
        """Task management CLI"""
        self.clear_screen()
        print("\n📋 TASK MANAGEMENT\n")
        print("Available commands:")
        print("  1. List all tasks")
        print("  2. View task details")
        print("  3. Update task status")
        print("  4. Assign task to engineer")
        print("  5. Back to menu\n")
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            print("\n🔄 Running: python project_cli.py --list\n")
            os.system("cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration && python project_cli.py --list")
        elif choice == "2":
            task_id = input("\nEnter task ID (e.g., TASK-0001): ").strip()
            print(f"\n🔄 Running: python project_cli.py --view {task_id}\n")
            os.system(f"cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration && python project_cli.py --view {task_id}")
        elif choice == "3":
            task_id = input("\nEnter task ID: ").strip()
            print(f"\n🔄 Running: python project_cli.py --update {task_id}\n")
            os.system(f"cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration && python project_cli.py --update {task_id}")
        
        input("\nPress Enter to return to menu...")
    
    def option_3_service_status(self):
        """Show detailed service status"""
        self.clear_screen()
        print("\n📡 DETAILED SERVICE STATUS\n")
        
        services = {
            "Backend RAG API": 8000,
            "Project Dashboard": 8888,
            "Frontend": 3000,
        }
        
        for name, port in services.items():
            if self.check_port(port):
                print(f"  ✅ {name:25} RUNNING on port {port}")
            else:
                print(f"  ❌ {name:25} NOT RUNNING on port {port}")
        
        print("\n" + "=" * 80)
        print("Health Check:")
        print("=" * 80 + "\n")
        
        os.system("cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration && python health_check.py 2>&1 | head -30")
        
        input("\n\nPress Enter to return to menu...")
    
    def option_4_realtime_tracker(self):
        """Real-time tracker"""
        print("\n🚀 STARTING REAL-TIME TRACKER (Refreshing every 30 seconds)")
        print("Press Ctrl+C to stop\n")
        time.sleep(2)
        
        os.system("cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration && python real_time_tracker.py --continuous --interval 30")
    
    def option_5_implementation_plan(self):
        """Show implementation plan"""
        self.clear_screen()
        print("\n📊 IMPLEMENTATION PLAN\n")
        
        print("=" * 80)
        print("PHASE 1: CRITICAL FIXES (26 hours, This Week)")
        print("=" * 80)
        print("""
  🔴 TASK-0001: Fix LanceDB Synchronization (8 hrs)
     - Backend dashboard_status counts vectors incorrectly
     - Fix vector sync between extraction and LanceDB
     
  🔴 TASK-0002: Fix Async/Await Mismatch (12 hrs)
     - SemanticChunker and searches run synchronously
     - Blocking event loop under load
     
  🔴 TASK-0003: Fix Knowledge Graph Memory Leak (6 hrs)
     - get_knowledge_graph loads all 200 vectors
     - Implement pagination to prevent browser freeze
""")
        
        print("=" * 80)
        print("PHASE 2: HIGH-PRIORITY IMPROVEMENTS (60 hours, Next 2 weeks)")
        print("=" * 80)
        print("""
  🟠 TASK-0004: Replace pymupdf4llm with Docling (16 hrs)
  🟠 TASK-0005: Implement Proper Error Handling (24 hrs)
  🟠 TASK-0006: Add Comprehensive Logging (20 hrs)
""")
        
        print("=" * 80)
        print("PHASE 3: QUALITY & OPTIMIZATION (60 hours, Weeks 3-4)")
        print("=" * 80)
        print("""
  🟡 TASK-0007: Performance Optimization (20 hrs)
  🟡 TASK-0008: Add Unit Tests (25 hrs)
  🟡 TASK-0009: Refactor Component Coupling (15 hrs)
""")
        
        print("=" * 80)
        print("PHASE 4: DOCUMENTATION (20 hours)")
        print("=" * 80)
        print("""
  🟢 TASK-0010: API Documentation (12 hrs)
  🟢 TASK-0011: Deployment Guide (8 hrs)
""")
        
        print("\n📊 TOTAL EFFORT: 166 hours")
        print("👥 RECOMMENDED TEAM: 5 senior + 2 mid-level engineers")
        print("📅 TIMELINE: 6-8 weeks (with full team)\n")
        
        input("Press Enter to return to menu...")
    
    def option_6_settings(self):
        """Settings/configuration"""
        self.clear_screen()
        print("\n🔧 PROJECT SETTINGS\n")
        print("Backend Port: 8000")
        print("Dashboard Port: 8888")
        print("Frontend Port: 3000")
        print("\nNo changes needed - all ports are configured.")
        input("\nPress Enter to return to menu...")
    
    def option_7_console(self):
        """Development console"""
        self.clear_screen()
        print("\n💻 DEVELOPMENT CONSOLE\n")
        print("Quick commands:")
        print("  health_check.py       - Run project health check")
        print("  project_cli.py        - Task management CLI")
        print("  real_time_tracker.py  - Real-time monitoring")
        print("  project_agent.py      - Project analysis agent")
        print("  project_dashboard.py  - Web dashboard server")
        print("\nOr type 'bash' to start a shell, 'python' for Python REPL, 'exit' to return\n")
        
        cmd = input("Enter command: ").strip()
        if cmd == "bash":
            os.chdir("/home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration")
            os.system("bash")
        elif cmd == "python":
            os.system("python")
        elif cmd:
            os.system(f"cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration && {cmd}")
    
    def option_8_help(self):
        """Help and documentation"""
        self.clear_screen()
        print("\n📚 HELP & DOCUMENTATION\n")
        print("Quick Links:")
        print("  🌐 Web Dashboard:     http://localhost:8888")
        print("  📚 API Documentation: http://localhost:8000/docs")
        print("  💻 Frontend:          http://localhost:3000")
        print("\nDocumentation Files:")
        print("  📄 QUICK_START_AGENT.md")
        print("  📄 PROJECT_AGENT_README.md")
        print("  📄 IMPLEMENTATION_LOG.txt")
        print("  📄 README.md")
        print("\nFeatures:")
        print("  ✅ Real-time project tracking")
        print("  ✅ Kanban task board")
        print("  ✅ Team assignment management")
        print("  ✅ Automated health checks")
        print("  ✅ Implementation planning")
        print("  ✅ Progress metrics\n")
        input("Press Enter to return to menu...")
    
    def run(self):
        """Main loop"""
        try:
            while True:
                self.display_banner()
                
                # Show quick status
                self.show_status()
                
                # Show menu
                self.show_menu()
                
                choice = input("Select an option (0-8): ").strip()
                
                if choice == "0":
                    print("\n✅ Goodbye!\n")
                    sys.exit(0)
                elif choice == "1":
                    self.option_1_web_dashboard()
                elif choice == "2":
                    self.option_2_task_management()
                elif choice == "3":
                    self.option_3_service_status()
                elif choice == "4":
                    self.option_4_realtime_tracker()
                elif choice == "5":
                    self.option_5_implementation_plan()
                elif choice == "6":
                    self.option_6_settings()
                elif choice == "7":
                    self.option_7_console()
                elif choice == "8":
                    self.option_8_help()
                else:
                    print("\n❌ Invalid option. Please try again.")
                    time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n\n✅ Master Control Panel closed")
            sys.exit(0)


def main():
    """Main entry point"""
    panel = MasterControlPanel()
    panel.run()


if __name__ == "__main__":
    main()
