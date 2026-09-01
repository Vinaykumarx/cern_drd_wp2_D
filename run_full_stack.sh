#!/bin/bash
# ------------------------------------------------------------
# run_full_stack.sh – Starts both FastAPI Backend and Next.js Frontend
# Fixes applied:
#  1. Uses explicit venv Python binary (no source activate needed)
#  2. Properly daemonizes with nohup + disown so SIGHUP can't kill them
#  3. CWD is set to project root for .env and relative path resolution
#  4. Waits for backend /api/health before starting frontend
#  5. /api/sessions now returns all required fields (title, updated_at)
# ------------------------------------------------------------

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "------------------------------------------------------------"
echo "  CERN Multimodal RAG – Full Stack Launcher"
echo "  Project: $PROJECT_ROOT"
echo "------------------------------------------------------------"

# ── 1. Kill any existing processes on ports 8000 and 3000 ───────────────────
echo ""
echo "🧹 Cleaning up existing processes on ports 8000 and 3000..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 3000/tcp 2>/dev/null || true
sleep 1

# ── 2. Locate Virtual Environment Python ────────────────────────────────────
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/.venv/bin/python"
    echo "✅ Using .venv Python: $PYTHON"
elif [ -f "$PROJECT_ROOT/venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/venv/bin/python"
    echo "✅ Using venv Python: $PYTHON"
else
    echo "❌ No virtual environment found (.venv or venv). Please run setup first."
    exit 1
fi

# ── 3. Start Backend (FastAPI via uvicorn) ───────────────────────────────────
# Key fix: use explicit Python binary path so venv is always respected.
# nohup + disown ensures the process survives shell exit (no SIGHUP).
echo ""
echo "🚀 Starting Backend on http://localhost:8000..."
BACKEND_LOG="$PROJECT_ROOT/backend.log"

nohup "$PYTHON" -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
disown $BACKEND_PID
echo "   Backend PID: $BACKEND_PID → logging to: $BACKEND_LOG"

# ── 4. Wait for Backend to be healthy ───────────────────────────────────────
echo ""
echo "⏳ Waiting for backend to become ready..."
MAX_WAIT=45
WAITED=0
until curl -sf "http://localhost:8000/api/health" > /dev/null 2>&1; do
    sleep 1
    WAITED=$((WAITED + 1))
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo ""
        echo "❌ Backend failed to start within ${MAX_WAIT}s!"
        echo "   Last 30 lines of backend.log:"
        tail -30 "$BACKEND_LOG"
        echo ""
        echo "Common fixes:"
        echo "  - Check that all Python deps are installed: $PYTHON -m pip install -r requirements.txt"
        echo "  - Check .env for correct API keys"
        exit 1
    fi
    printf "."
done
echo ""
echo "✅ Backend is healthy and ready!"

# ── 5. Start Frontend (Next.js) ──────────────────────────────────────────────
echo ""
echo "🚀 Starting Frontend on http://localhost:3000..."
FRONTEND_LOG="$PROJECT_ROOT/frontend.log"

# Check node_modules exist
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo "⏳ node_modules not found, running npm install first..."
    cd "$PROJECT_ROOT/frontend"
    npm install
    cd "$PROJECT_ROOT"
fi

cd "$PROJECT_ROOT/frontend"
nohup npm run dev -- -p 3000 \
    > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
disown $FRONTEND_PID
cd "$PROJECT_ROOT"
echo "   Frontend PID: $FRONTEND_PID → logging to: $FRONTEND_LOG"

# ── 6. Wait for Frontend to be ready ────────────────────────────────────────
echo ""
echo "⏳ Waiting for frontend to become ready..."
MAX_WAIT=30
WAITED=0
until curl -sf "http://localhost:3000" > /dev/null 2>&1; do
    sleep 1
    WAITED=$((WAITED + 1))
    if [ $WAITED -ge $MAX_WAIT ]; then
        echo ""
        echo "⚠️  Frontend is slow to start (this is normal for Next.js compilation)."
        echo "   Check progress: tail -f $FRONTEND_LOG"
        break
    fi
    printf "."
done
echo ""

# ── 7. Summary ───────────────────────────────────────────────────────────────
echo "============================================================"
echo "  ✅ CERN RAG FULL STACK IS UP"
echo "============================================================"
echo "  🌐 Frontend:   http://localhost:3000"
echo "  🔧 Backend:    http://localhost:8000"
echo "  📖 API Docs:   http://localhost:8000/docs"
echo "  ❤️  Health:     http://localhost:8000/api/health"
echo "============================================================"
echo "  Backend PID:  $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo "============================================================"
echo "  Stop all:    kill $BACKEND_PID $FRONTEND_PID"
echo "  Kill ports:  fuser -k 8000/tcp 3000/tcp"
echo "============================================================"
echo "  Logs:"
echo "    tail -f $BACKEND_LOG"
echo "    tail -f $FRONTEND_LOG"
echo "============================================================"
