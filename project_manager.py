#!/usr/bin/env python3
from core.bootstrap import require_bootstrap; require_bootstrap()
"""
Quick startup script for project management tools
Run this to get a menu-driven interface for all tools
"""

import subprocess
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent


def main():
    while True:
        print("\n" + "="*80)
        print("🤖 PROJECT STATUS AGENT - QUICK START")
        print("="*80)
        print("""
1. Quick Status Report      Run quick health check & task count
2. Full Detailed Report     Generate comprehensive analysis
3. Interactive Kanban       Browse tasks by status
4. Task Management          Add, assign, or update tasks (Interactive)
5. Resource Allocation      See engineer recommendations
6. Web Dashboard            Launch web dashboard (http://localhost:8888)
7. Help & Documentation     View detailed documentation
8. Exit                     Quit

TIP: You can also run Python tools directly:
     python project_agent.py
     python project_agent.py --detailed
     python project_cli.py menu
        """)
        print("="*80)

        choice = input("Select option (1-8): ").strip()

        try:
            if choice == '1':
                print("\n🔍 Running quick status report...\n")
                subprocess.run([sys.executable, 'project_agent.py'], cwd=PROJECT_ROOT)

            elif choice == '2':
                print("\n📊 Generating detailed report...\n")
                subprocess.run([sys.executable, 'project_agent.py', '--detailed'], cwd=PROJECT_ROOT)

            elif choice == '3':
                print("\n📋 Displaying kanban board...\n")
                subprocess.run([sys.executable, 'project_cli.py', 'kanban'], cwd=PROJECT_ROOT)

            elif choice == '4':
                print("\n✏️ Starting task management...\n")
                subprocess.run([sys.executable, 'project_cli.py', 'menu'], cwd=PROJECT_ROOT)

            elif choice == '5':
                print("\n👥 Showing allocations...\n")
                subprocess.run([sys.executable, 'project_cli.py', 'allocate'], cwd=PROJECT_ROOT)

            elif choice == '6':
                print("\n🌐 Starting web dashboard on http://localhost:8888...")
                print("   Press Ctrl+C to stop\n")
                try:
                    subprocess.run(
                        [sys.executable, '-m', 'uvicorn', 'project_dashboard:app', 
                         '--reload', '--port', '8888'],
                        cwd=PROJECT_ROOT
                    )
                except KeyboardInterrupt:
                    print("\n✅ Dashboard stopped")

            elif choice == '7':
                print_help()

            elif choice == '8':
                print("\n👋 Goodbye!\n")
                break

            else:
                print("❌ Invalid option, please try again")

        except KeyboardInterrupt:
            print("\n(Interrupted)")
        except Exception as e:
            print(f"❌ Error: {e}")


def print_help():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     PROJECT STATUS AGENT - USER GUIDE                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

📖 WHAT IS THE PROJECT STATUS AGENT?

The Project Status Agent is a comprehensive project management system that helps:
  • Analyze project health and identify critical issues
  • Track tasks using a kanban board (Backlog → Todo → In Progress → Done)
  • Recommend task assignments to engineers based on skills and availability
  • Monitor progress and generate reports

═══════════════════════════════════════════════════════════════════════════════

🚀 GETTING STARTED

1. Initial Assessment:
   python project_agent.py
   
2. Full Report with Recommendations:
   python project_agent.py --detailed

3. Interactive Task Management:
   python project_cli.py menu

4. Web Dashboard (Recommended):
   uvicorn project_dashboard:app --reload --port 8888
   Then visit: http://localhost:8888

═══════════════════════════════════════════════════════════════════════════════

📊 UNDERSTANDING THE DASHBOARD

Health Score (0-100):
  • 90+   🟢 Production Ready
  • 70-89 🟡 Needs Minor Fixes
  • 50-69 🟠 Major Issues
  • <50   🔴 Critical Issues

Task Statuses:
  • 📋 Backlog    - Not yet started
  • 🔲 Todo       - Ready to start
  • ⏳ In Progress - Currently being worked on
  • 👀 In Review  - Waiting for review/approval
  • ✅ Done       - Completed
  • 🚫 Blocked    - Cannot proceed (waiting on dependencies)

Priority Levels:
  • 🔴 Critical  - Must fix before production
  • 🟠 High      - Important for feature completeness
  • 🟡 Medium    - Should complete soon
  • 🟢 Low       - Nice to have

═══════════════════════════════════════════════════════════════════════════════

👥 TEAM STRUCTURE

The agent recommends a team of specialists:

  • Senior Architect (Staff Engineer, 5+ years)
    → System design, architecture decisions, LLM/RAG expertise
    → Handle CRITICAL issues and major refactors

  • Backend Engineer (Senior, 5+ years)
    → FastAPI, Python, async systems, database optimization
    → Core pipeline development

  • Frontend Engineer (Senior, 5+ years)
    → Next.js, TypeScript, UI/UX, data visualization
    → Dashboard and user interface

  • ML/AI Specialist (Senior, 5+ years)
    → Transformers, embeddings, vision models
    → Extraction pipeline, vector search optimization

  • DevOps/Infrastructure (Senior, 5+ years)
    → Docker, Kubernetes, CI/CD, monitoring
    → Deployment and scalability

  • Additional Support Engineers (Mid-level)
    → Testing, bug fixes, documentation
    → Feature implementation under guidance

═══════════════════════════════════════════════════════════════════════════════

⚙️ COMMAND REFERENCE

PROJECT AGENT:
  python project_agent.py                 # Quick summary
  python project_agent.py --detailed      # Full report with recommendations

PROJECT CLI:
  python project_cli.py status            # Quick status
  python project_cli.py kanban            # Show kanban board
  python project_cli.py allocate          # Resource recommendations
  python project_cli.py report            # Detailed report
  python project_cli.py add               # Add new task (interactive)
  python project_cli.py menu              # Interactive menu
  python project_cli.py help              # Show help

PROJECT DASHBOARD:
  uvicorn project_dashboard:app --reload --port 8888
  # Visit http://localhost:8888 in your browser

═══════════════════════════════════════════════════════════════════════════════

📋 CURRENT PROJECT STATUS

CRITICAL ISSUES TO FIX:
  1. LanceDB synchronization bugs
  2. Async/await blocking issues in FastAPI
  3. Knowledge graph memory leak (loading all vectors)

HIGH PRIORITY:
  1. Replace PDF parser with Docling
  2. Implement ColPali for visual retrieval
  3. Consolidate UI (deprecate Streamlit)

═══════════════════════════════════════════════════════════════════════════════

🎯 WORKFLOW FOR USING THE AGENT

1. Run Initial Assessment:
   $ python project_agent.py

2. Review Full Report:
   $ python project_agent.py --detailed
   
3. View Tasks (by status):
   $ python project_cli.py kanban

4. Get Team Recommendations:
   $ python project_cli.py allocate

5. Add Tasks as Needed:
   $ python project_cli.py add

6. Assign to Team:
   $ python project_cli.py menu  → Choose option 6

7. Track Progress:
   • Use web dashboard for visual progress
   • Update statuses as work completes
   • Monitor timeline and blockers

═══════════════════════════════════════════════════════════════════════════════

💾 DATA PERSISTENCE

Tasks are saved in: project_tasks.json
  • Persists across tool invocations
  • JSON format for easy integration
  • Can be imported/exported for reporting

═══════════════════════════════════════════════════════════════════════════════

🔗 INTEGRATION WITH EXISTING TOOLS

The agent integrates with:
  • FastAPI backend (can add endpoints)
  • Next.js frontend (can add dashboard page)
  • Existing workflows (non-invasive)

═══════════════════════════════════════════════════════════════════════════════

❓ FAQ

Q: How do I get accurate task time estimates?
A: The "estimated_hours" field helps track effort. Use your team's historical
   data to calibrate estimates.

Q: Can I integrate this with CI/CD?
A: Yes! The API endpoints can be called from GitHub Actions, GitLab CI, etc.
   Example: curl http://localhost:8888/api/health

Q: How do I export reports for stakeholders?
A: Run: python project_agent.py --detailed > project_report.txt
   Then share the text file or convert to PDF.

Q: Can I customize the engineer team?
A: Yes! Edit the _initialize_team() method in project_agent.py to match
   your actual team structure.

═══════════════════════════════════════════════════════════════════════════════

📞 SUPPORT

For issues or feature requests, refer to:
  • ARCHITECTURE_REVIEW.md - Technical decisions
  • CTO_PROJECT_MANIFEST.md - Project goals
  • README.md - Installation and setup

═══════════════════════════════════════════════════════════════════════════════
""")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Agent shutdown\n")
        sys.exit(0)
