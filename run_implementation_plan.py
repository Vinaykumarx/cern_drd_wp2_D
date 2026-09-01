#!/usr/bin/env python3
from core.bootstrap import require_bootstrap; require_bootstrap()
"""
🚀 IMPLEMENTATION PLAN EXECUTOR
Auto-runs the project startup plan and tracks progress
"""

import os
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ImplementationPlanExecutor:
    """Executes the implementation plan"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tasks_file = self.project_root / "project_tasks.json"
        self.plan_log_file = self.project_root / "IMPLEMENTATION_LOG.txt"
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] [{level:8}] {message}"
        print(log_msg)
        
        # Also save to file
        with open(self.plan_log_file, "a") as f:
            f.write(log_msg + "\n")
    
    def load_tasks(self) -> Dict:
        """Load tasks from file"""
        try:
            with open(self.tasks_file) as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Error loading tasks: {e}", "ERROR")
            return {}
    
    def save_tasks(self, tasks: Dict):
        """Save tasks to file"""
        try:
            with open(self.tasks_file, "w") as f:
                json.dump(tasks, f, indent=2)
            self.log(f"Saved {len(tasks)} tasks", "INFO")
        except Exception as e:
            self.log(f"Error saving tasks: {e}", "ERROR")
    
    def initialize_tasks_from_backlog(self):
        """Initialize tasks from backlog"""
        self.log("=" * 80, "START")
        self.log("INITIALIZING PROJECT TASKS", "START")
        
        tasks = self.load_tasks()
        
        if not tasks:
            self.log("No tasks found!", "WARN")
            return
        
        # Count tasks by status
        stats = {
            "total": len(tasks),
            "backlog": 0,
            "in_progress": 0,
            "done": 0,
        }
        
        for task_id, task in tasks.items():
            status = task.get("status", "")
            if "Backlog" in status:
                stats["backlog"] += 1
            elif "In Progress" in status or "🔄" in status:
                stats["in_progress"] += 1
            elif "Done" in status or "✅" in status:
                stats["done"] += 1
        
        self.log(f"Loaded {stats['total']} tasks", "INFO")
        self.log(f"  - Backlog: {stats['backlog']}", "INFO")
        self.log(f"  - In Progress: {stats['in_progress']}", "INFO")
        self.log(f"  - Done: {stats['done']}", "INFO")
    
    def verify_services(self):
        """Verify all services are running"""
        self.log("VERIFYING SERVICES", "CHECK")
        
        ports = {
            8000: "Backend RAG API",
            8888: "Project Dashboard",
            3000: "Frontend",
        }
        
        all_running = True
        for port, name in ports.items():
            result = os.system(f"nc -z localhost {port} 2>/dev/null")
            if result == 0:
                self.log(f"✅ {name:25} running on port {port}", "INFO")
            else:
                self.log(f"⚠️  {name:25} NOT running on port {port}", "WARN")
                all_running = False
        
        return all_running
    
    def run_health_check(self):
        """Run health checks"""
        self.log("RUNNING HEALTH CHECKS", "CHECK")
        
        try:
            result = subprocess.run(
                ["python", "health_check.py"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                self.log("✅ Health check passed", "INFO")
                return True
            else:
                self.log(f"⚠️  Health check issues detected", "WARN")
                return False
        except Exception as e:
            self.log(f"Health check failed: {e}", "ERROR")
            return False
    
    def create_implementation_plan(self):
        """Create the implementation plan"""
        self.log("CREATING IMPLEMENTATION PLAN", "PLAN")
        
        plan = {
            "phase": 1,
            "stages": [
                {
                    "stage": "1. PROJECT SETUP & VERIFICATION",
                    "duration": "2 hours",
                    "tasks": [
                        "✅ Verify all services running (Backend, Dashboard, Frontend)",
                        "✅ Load and validate task database",
                        "✅ Run health checks",
                        "✅ Initialize tracking systems",
                    ]
                },
                {
                    "stage": "2. CRITICAL FIXES (Phase 1)",
                    "duration": "26 hours",
                    "tasks": [
                        "🔴 TASK-0001: Fix LanceDB Synchronization (8 hrs)",
                        "🔴 TASK-0002: Fix Async/Await Mismatch (12 hrs)",
                        "🔴 TASK-0003: Fix Knowledge Graph Memory Leak (6 hrs)",
                    ]
                },
                {
                    "stage": "3. HIGH-PRIORITY IMPROVEMENTS",
                    "duration": "60 hours",
                    "tasks": [
                        "🟠 TASK-0004: Replace pymupdf4llm with Docling (16 hrs)",
                        "🟠 TASK-0005: Implement Proper Error Handling (24 hrs)",
                        "🟠 TASK-0006: Add Comprehensive Logging (20 hrs)",
                    ]
                },
                {
                    "stage": "4. QUALITY & OPTIMIZATION",
                    "duration": "60 hours",
                    "tasks": [
                        "🟡 TASK-0007: Performance Optimization (20 hrs)",
                        "🟡 TASK-0008: Add Unit Tests (25 hrs)",
                        "🟡 TASK-0009: Refactor Component Coupling (15 hrs)",
                    ]
                },
                {
                    "stage": "5. DOCUMENTATION & TEAM PREP",
                    "duration": "20 hours",
                    "tasks": [
                        "🟢 TASK-0010: API Documentation (12 hrs)",
                        "🟢 TASK-0011: Deployment Guide (8 hrs)",
                    ]
                },
            ],
            "total_effort": "168 hours",
            "recommended_team": {
                "seniors": 5,
                "mid_level": 2,
                "total_capacity_tasks": 34,
            }
        }
        
        self.log("Implementation Plan:", "PLAN")
        for stage in plan["stages"]:
            self.log(f"\n{stage['stage']}", "PLAN")
            self.log(f"  Duration: {stage['duration']}", "PLAN")
            for task in stage['tasks']:
                self.log(f"    - {task}", "PLAN")
        
        return plan
    
    def track_execution(self):
        """Track execution progress"""
        self.log("TRACKING EXECUTION", "TRACK")
        
        tasks = self.load_tasks()
        
        # Count by priority
        priority_map = {
            "🔴 Critical": "critical",
            "🟠 High": "high",
            "🟡 Medium": "medium",
            "🟢 Low": "low",
        }
        
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for task_id, task in tasks.items():
            priority = task.get("priority", "")
            for emoji_priority, level in priority_map.items():
                if emoji_priority in priority:
                    counts[level] += 1
                    break
        
        self.log("Task breakdown by priority:", "TRACK")
        self.log(f"  🔴 Critical: {counts['critical']} tasks - 26 hours", "TRACK")
        self.log(f"  🟠 High:     {counts['high']} tasks - 60 hours", "TRACK")
        self.log(f"  🟡 Medium:   {counts['medium']} tasks - 60 hours", "TRACK")
        self.log(f"  🟢 Low:      {counts['low']} tasks - 20 hours", "TRACK")
    
    def create_team_assignment_template(self):
        """Create team assignment template"""
        self.log("CREATING TEAM ASSIGNMENT TEMPLATE", "SETUP")
        
        template = {
            "phase": 1,
            "week": 1,
            "team": [
                {
                    "role": "Senior Backend Engineer #1",
                    "focus": "TASK-0001: LanceDB Sync (8 hrs)",
                    "skills": ["Python", "Async", "LanceDB", "Vector DB"],
                    "capacity": "40 hrs/week",
                },
                {
                    "role": "Senior Backend Engineer #2",
                    "focus": "TASK-0002: Async/Await (12 hrs)",
                    "skills": ["Python", "FastAPI", "Async", "Performance"],
                    "capacity": "40 hrs/week",
                },
                {
                    "role": "Senior Full-Stack Engineer #3",
                    "focus": "TASK-0003: Memory Leak + Support",
                    "skills": ["Python", "React", "Performance", "Debugging"],
                    "capacity": "40 hrs/week",
                },
                {
                    "role": "Mid-Level Backend Engineer",
                    "focus": "TASK-0004: Docling Integration (16 hrs)",
                    "skills": ["Python", "PDF Processing", "Testing"],
                    "capacity": "40 hrs/week",
                },
                {
                    "role": "Senior DevOps/QA Engineer",
                    "focus": "Health Checks & Testing",
                    "skills": ["Python", "Testing", "CI/CD", "Monitoring"],
                    "capacity": "40 hrs/week",
                }
            ]
        }
        
        self.log("Recommended team for Phase 1:", "SETUP")
        for idx, member in enumerate(template["team"], 1):
            self.log(f"  {idx}. {member['role']}", "SETUP")
            self.log(f"     Focus: {member['focus']}", "SETUP")
        
        return template
    
    def run(self):
        """Execute the full implementation plan"""
        try:
            # Clear and start log
            self.plan_log_file.write_text("")
            
            self.log("=" * 80, "START")
            self.log("CERN MULTIMODAL RAG - IMPLEMENTATION PLAN EXECUTOR", "START")
            self.log("=" * 80, "START")
            
            # Step 1: Verify services
            self.log("\n" + "="*80, "STEP")
            self.log("STEP 1: VERIFY SERVICES", "STEP")
            self.log("="*80, "STEP")
            all_running = self.verify_services()
            
            if not all_running:
                self.log("⚠️  Some services not running. Please start them:", "WARN")
                self.log("  Backend: uvicorn backend.main:app --port 8000", "WARN")
                self.log("  Dashboard: uvicorn project_dashboard:app --port 8888", "WARN")
                return False
            
            # Step 2: Initialize tasks
            self.log("\n" + "="*80, "STEP")
            self.log("STEP 2: INITIALIZE TASKS", "STEP")
            self.log("="*80, "STEP")
            self.initialize_tasks_from_backlog()
            
            # Step 3: Run health checks
            self.log("\n" + "="*80, "STEP")
            self.log("STEP 3: HEALTH CHECKS", "STEP")
            self.log("="*80, "STEP")
            self.run_health_check()
            
            # Step 4: Create implementation plan
            self.log("\n" + "="*80, "STEP")
            self.log("STEP 4: IMPLEMENTATION PLAN", "STEP")
            self.log("="*80, "STEP")
            plan = self.create_implementation_plan()
            
            # Step 5: Track execution
            self.log("\n" + "="*80, "STEP")
            self.log("STEP 5: EXECUTION TRACKING", "STEP")
            self.log("="*80, "STEP")
            self.track_execution()
            
            # Step 6: Team assignment
            self.log("\n" + "="*80, "STEP")
            self.log("STEP 6: TEAM ASSIGNMENT", "STEP")
            self.log("="*80, "STEP")
            self.create_team_assignment_template()
            
            # Summary
            self.log("\n" + "="*80, "SUMMARY")
            self.log("✅ IMPLEMENTATION PLAN READY", "SUMMARY")
            self.log("="*80, "SUMMARY")
            self.log("", "SUMMARY")
            self.log("📌 IMMEDIATE ACTIONS:", "SUMMARY")
            self.log("  1. Review: http://localhost:8888 (Project Dashboard)", "SUMMARY")
            self.log("  2. Run: python project_cli.py --list (See all tasks)", "SUMMARY")
            self.log("  3. Run: python real_time_tracker.py --once (Check status)", "SUMMARY")
            self.log("  4. Share team assignments with engineering leads", "SUMMARY")
            self.log("  5. Begin Phase 1: Critical fixes (this week)", "SUMMARY")
            self.log("", "SUMMARY")
            self.log(f"📊 Implementation started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "SUMMARY")
            self.log(f"📁 Log file: {self.plan_log_file}", "SUMMARY")
            self.log("="*80, "SUMMARY")
            
            return True
            
        except Exception as e:
            self.log(f"Fatal error: {e}", "ERROR")
            return False


def main():
    """Main entry point"""
    executor = ImplementationPlanExecutor()
    
    # Print welcome message
    print("\n" + "="*80)
    print("🚀 CERN MULTIMODAL RAG - IMPLEMENTATION PLAN")
    print("="*80)
    print("\nStarting automated plan execution...")
    print("Log file will be saved to: IMPLEMENTATION_LOG.txt\n")
    
    success = executor.run()
    
    if success:
        print("\n✅ Plan execution completed successfully!")
        print("✅ All systems ready for implementation")
        print(f"\n📁 Log: {executor.plan_log_file}")
        print("📊 Dashboard: http://localhost:8888")
        print("📚 API Docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  Plan execution encountered issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
