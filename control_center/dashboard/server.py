"""
Control Center Dashboard Server — Port 8899
Read-only observability for the CERN Multimodal RAG system.
Integrates with core.bootstrap and core.architecture_validator.
"""

import sys
import json
import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DASHBOARD_DIR = Path(__file__).resolve().parent

sys.path.insert(0, str(PROJECT_ROOT))

from core.bootstrap import startup_enforce, get_runtime_context
from core.architecture_validator import run_architecture_validation

app = FastAPI(title="Control Center Dashboard", version="1.0.0")

_validation_report: Optional[dict] = None
_bootstrap_context: Optional[dict] = None


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup():
    global _validation_report, _bootstrap_context
    ctx = startup_enforce(exit_on_critical=True)
    _bootstrap_context = ctx.to_dict() if ctx else {}
    report = run_architecture_validation(exit_on_fail=False)
    _validation_report = report


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory=str(DASHBOARD_DIR)), name="static")


@app.get("/")
async def serve_index():
    return FileResponse(str(DASHBOARD_DIR / "index.html"))


@app.get("/app.js")
async def serve_js():
    return FileResponse(str(DASHBOARD_DIR / "app.js"), media_type="application/javascript")


@app.get("/styles.css")
async def serve_css():
    return FileResponse(str(DASHBOARD_DIR / "styles.css"), media_type="text/css")


# ---------------------------------------------------------------------------
# Data API
# ---------------------------------------------------------------------------

def read_file(path: Path) -> str:
    try:
        return path.read_text()
    except Exception:
        return ""


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


@app.get("/api/runtime-context")
async def get_runtime_context_api():
    try:
        ctx = get_runtime_context()
        return ctx.to_dict()
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/status")
async def get_status():
    return {
        "validation": _validation_report,
        "bootstrap_loaded": _bootstrap_context is not None,
    }


@app.get("/api/tasks")
async def get_tasks():
    path = PROJECT_ROOT / "control_center" / "TASKS.json"
    return read_json(path)


@app.get("/api/bugs")
async def get_bugs():
    path = PROJECT_ROOT / "control_center" / "BUGS.md"
    raw = read_file(path)
    bugs = []
    current = {}
    for line in raw.splitlines():
        if line.startswith("## BUG-"):
            if current:
                bugs.append(current)
            current = {"id": line.strip("#").strip()}
        elif line.startswith("- Description:"):
            current["description"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Severity:"):
            current["severity"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Status:"):
            current["status"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Fix:"):
            current["fix"] = line.split(":", 1)[1].strip()
    if current:
        bugs.append(current)
    return {"bugs": bugs}


@app.get("/api/sessions")
async def get_sessions():
    path = PROJECT_ROOT / "knowledge_system" / "session_index.json"
    return read_json(path)


@app.get("/api/state")
async def get_state():
    project_state = read_file(PROJECT_ROOT / "control_center" / "PROJECT_STATE.md")
    latest_state = read_file(PROJECT_ROOT / "knowledge_system" / "latest_state.md")
    system_lock = read_file(PROJECT_ROOT / "control_center" / "SYSTEM_LOCK.md")
    return {
        "project_state": project_state,
        "latest_state": latest_state,
        "system_lock": system_lock,
    }


@app.get("/api/config")
async def get_config():
    path = DASHBOARD_DIR / "dashboard_config.json"
    return read_json(path)


@app.get("/api/masterplan")
async def get_masterplan():
    path = PROJECT_ROOT / "control_center" / "MASTER_PLAN.md"
    return {"content": read_file(path)}


@app.get("/api/decisions")
async def get_decisions():
    path = PROJECT_ROOT / "control_center" / "DECISIONS.md"
    return {"content": read_file(path)}


@app.get("/api/architecture-mmd")
async def get_architecture_mmd():
    path = PROJECT_ROOT / "control_center" / "ARCHITECTURE.mmd"
    return {"content": read_file(path)}


@app.get("/api/changelog")
async def get_changelog():
    path = PROJECT_ROOT / "control_center" / "CHANGELOG.md"
    return {"content": read_file(path)}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8899)
