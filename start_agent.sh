#!/bin/bash
# 🤖 PROJECT STATUS AGENT - Quick Launch Script
# For: CERN Multimodal RAG Project
# Created: May 7, 2026

clear

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║            🤖  PROJECT STATUS AGENT - CERN Multimodal RAG                      ║
║                                                                                ║
║         Production-Grade Project Management & Task Tracking System            ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝


📋 QUICK START - Choose Your Interface:

1. 🌐 WEB DASHBOARD (Recommended - Beautiful, Real-Time)
   uvicorn project_dashboard:app --reload --port 8888
   Then open: http://localhost:8888

2. 💻 INTERACTIVE MENU (All-in-One)
   python project_manager.py

3. 📊 TERMINAL REPORT (Quick Summary)
   python project_agent.py

4. 📈 DETAILED REPORT (Full Analysis)
   python project_agent.py --detailed

5. 💬 COMMAND LINE (Advanced)
   python project_cli.py menu


📖 DOCUMENTATION:

• QUICK_START_AGENT.md ........... 5-minute quick start guide
• PROJECT_AGENT_README.md ........ Comprehensive 400+ line guide
• DELIVERABLES_SUMMARY.md ........ Feature checklist & overview


📦 WHAT'S INCLUDED:

✓ Project health analysis engine
✓ 13 pre-identified tasks (ready to assign)
✓ Kanban board task management
✓ Intelligent engineer allocation
✓ Real-time web dashboard
✓ REST API with 8+ endpoints
✓ Interactive CLI menus
✓ Stakeholder reporting
✓ Persistent data storage


🎯 CURRENT PROJECT STATUS:

Health Score: ✅ 100/100 (Structurally Complete)
Tasks Identified: 📋 13 (166 hours estimated)
Recommended Team: 👥 7 engineers
Critical Issues: 🔴 3 (LanceDB, Async, Graph Memory)
Implementation Plan: 📅 3 phases (6-8 weeks)


════════════════════════════════════════════════════════════════════════════════

Choose an option above and press Enter to continue, or:

Q = Quit this menu
H = Show full help information
R = Generate detailed report

════════════════════════════════════════════════════════════════════════════════
EOF

echo ""
read -p "Select (1-5, Q, H, or R): " choice

case $choice in
    1)
        echo ""
        echo "🌐 Launching Web Dashboard on http://localhost:8888"
        echo "Press Ctrl+C to stop"
        echo ""
        cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration
        uvicorn project_dashboard:app --reload --port 8888
        ;;
    2)
        echo ""
        echo "💻 Launching Interactive Menu..."
        echo ""
        cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration
        python project_manager.py
        ;;
    3)
        echo ""
        echo "📊 Generating Quick Status Report..."
        echo ""
        cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration
        python project_agent.py
        ;;
    4)
        echo ""
        echo "📈 Generating Detailed Report..."
        echo ""
        cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration
        python project_agent.py --detailed
        ;;
    5)
        echo ""
        echo "💬 Launching Command-Line Interface..."
        echo ""
        cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration
        python project_cli.py menu
        ;;
    Q|q)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    H|h)
        clear
        cat PROJECT_AGENT_README.md | head -100
        ;;
    R|r)
        echo ""
        echo "📈 Generating Detailed Report..."
        echo ""
        cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration
        python project_agent.py --detailed
        ;;
    *)
        echo ""
        echo "❌ Invalid option. Please try again."
        ;;
esac
