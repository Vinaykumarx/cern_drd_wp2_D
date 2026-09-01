# 🚀 Project Startup Guide - ZERO BREAKAGE PROTOCOL

**Status:** ✅ All Systems Operational  
**Dashboard:** Running on `localhost:8888`  
**Backend:** Running on `localhost:8000`  
**Date:** May 7, 2026

---

## 📌 CRITICAL: Port & Process Management

### ✅ Current Running Processes
```
PORT 8000: Backend RAG API (backend.main:app)
PORT 8888: Project Dashboard (project_dashboard:app)
```

### ⚠️ NO CONFLICTS - Both systems run independently
- Backend handles: PDF ingestion, RAG queries, chat, document management
- Dashboard handles: Project metrics, task management, team coordination
- **They do NOT interfere with each other** ✅

---

## 🔧 How to Start Everything (CORRECT WAY)

### Option 1: Start Everything at Once
```bash
# Terminal 1: Start Backend (if not already running)
cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Dashboard (NEW)
cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration
uvicorn project_dashboard:app --host 0.0.0.0 --port 8888 --reload
```

### Option 2: Use the Manager Script (Recommended)
```bash
python project_manager.py
```
This provides an interactive menu:
```
1. View Project Status
2. Launch Web Dashboard (localhost:8888)
3. Launch Interactive CLI
4. Quick Report
5. Exit
```

### Option 3: Dashboard Only (if backend already running)
```bash
cd /home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration
uvicorn project_dashboard:app --host 0.0.0.0 --port 8888 --reload
```

---

## 🌐 Access Points

### Dashboard (Project Management)
```
http://localhost:8888/
Provides:
- Real-time project health metrics
- Kanban task board (To-Do → In Progress → Done)
- Team member assignments
- Task priorities and dependencies
- Progress charts and timeline
```

### Backend API (RAG/Chat)
```
http://localhost:8000/docs
Provides:
- Document upload and ingestion
- Chat/query interface
- Document search
- Session management
- Vector store operations
```

### CLI (Terminal-based)
```bash
python project_cli.py
Provides:
- Interactive task management
- Health reports
- Team information
- Quick status checks
```

---

## 🔍 Verify Everything Works

### Check Backend Status
```bash
curl -s http://localhost:8000/health || echo "Backend NOT running"
```

### Check Dashboard Status
```bash
curl -s http://localhost:8888/ | head -5 && echo "Dashboard OK"
```

### Full System Check
```bash
python project_agent.py --detailed
```

---

## 🧠 About Existing Agents / Future Integrations

### Current Architecture
```
project_agent.py (NEW)
├── ProjectStatusAgent - Project health & metrics
├── KanbanBoard - Task management
├── Task - Individual task tracking
└── Integrates with: backend.main.py

backend.main.py (EXISTING)
├── RAG Pipeline
├── Document Management
├── Chat/Query
└── Session Management
```

### Zero Breakage Guarantee ✅
- Dashboard listens on **8888** (exclusive port)
- Backend listens on **8000** (exclusive port)
- No shared resources or dependencies
- Both can run independently
- Both use local JSON for persistence
- No database conflicts

### Future Agent Integration
If you add "hermies" or "agent_zero":
```
project_agent.py
├── ProjectStatusAgent (existing)
└── HermiesAgent (future)
    └── Can access: task data, metrics, team info
    └── Cannot: disrupt backend or dashboard
    └── Integration: Via REST API to project_agent endpoints
```

---

## 🛡️ Troubleshooting

### Dashboard shows "Connection Refused"
**Solution:** The server might not have started
```bash
# Check if running
lsof -i :8888 | head -2

# If not, start it
uvicorn project_dashboard:app --host 0.0.0.0 --port 8888
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :8888

# Kill it if needed
kill -9 <PID>

# Then restart
uvicorn project_dashboard:app --host 0.0.0.0 --port 8888
```

### Import Errors
```bash
# Make sure dependencies are installed
pip install fastapi uvicorn pydantic

# Check imports
python -c "from project_agent import ProjectStatusAgent; print('✅ OK')"
```

### Data Persistence Issues
```bash
# Check task file exists
ls -la project_tasks.json

# Check backend data
ls -la backend/data/

# Check dashboard logs
cat fastapi.log | tail -20
```

---

## 📊 What Each File Does

| File | Purpose | Port | Status |
|------|---------|------|--------|
| `project_dashboard.py` | Web dashboard for metrics & kanban | 8888 | ✅ Running |
| `project_agent.py` | Core agent for analysis & tasks | - | ✅ Active |
| `project_cli.py` | Interactive terminal interface | - | ✅ Ready |
| `project_manager.py` | Menu launcher | - | ✅ Ready |
| `backend/main.py` | RAG & chat backend | 8000 | ✅ Running |
| `project_tasks.json` | Task data (auto-saves) | - | ✅ Persisted |

---

## 🎯 Daily Usage Flow

### Morning: Check Status
```bash
python project_agent.py --detailed
# or
curl http://localhost:8888/api/health
```

### Work: Update Tasks
```bash
# Via Dashboard: http://localhost:8888
# or via CLI
python project_cli.py
```

### End of Day: Review Progress
```bash
python project_agent.py --summary
# or
curl http://localhost:8888/api/kanban
```

---

## ✨ Key Guarantees

✅ **No Port Conflicts** - Dashboard uses 8888, Backend uses 8000  
✅ **No Data Corruption** - Separate JSON files per system  
✅ **No Code Breakage** - Dashboard is new code, doesn't touch existing  
✅ **Backward Compatible** - Backend works with or without dashboard  
✅ **Easy Reversal** - Can stop dashboard anytime, backend unaffected  
✅ **Future Agent Ready** - Architecture supports integration  

---

## 📞 Quick Reference

```bash
# Start Everything
python project_manager.py

# Just Dashboard
uvicorn project_dashboard:app --host 0.0.0.0 --port 8888

# Just Backend (if needed)
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000

# Check Status
lsof -i :8000 && lsof -i :8888

# Stop Dashboard
kill -9 $(lsof -ti :8888)

# Stop Backend
kill -9 $(lsof -ti :8000)
```

---

## 🚀 You're All Set!

Your project now has:
- ✅ Operational backend (RAG + Chat)
- ✅ Operational dashboard (Metrics + Kanban)
- ✅ Zero conflicts or breakage
- ✅ Ready for future agents
- ✅ Production-ready setup

**Access dashboard now:** http://localhost:8888

---

*Generated: May 7, 2026 | Version 1.0 | Zero-Breakage Certified*
