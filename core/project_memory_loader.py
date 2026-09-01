import json
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SESSION_INDEX_PATH = PROJECT_ROOT / "knowledge_system" / "session_index.json"
SESSION_LOGS_DIR = PROJECT_ROOT / "knowledge_system" / "session_logs"
TASKS_PATH = PROJECT_ROOT / "control_center" / "TASKS.json"
BUGS_PATH = PROJECT_ROOT / "control_center" / "BUGS.md"
PROJECT_STATE_PATH = PROJECT_ROOT / "control_center" / "PROJECT_STATE.md"
LATEST_STATE_PATH = PROJECT_ROOT / "knowledge_system" / "latest_state.md"


def load_session_index() -> dict:
    if SESSION_INDEX_PATH.exists():
        return json.loads(SESSION_INDEX_PATH.read_text())
    return {"index_version": 1, "sessions": {}, "session_order": []}


def load_latest_session() -> Optional[dict]:
    index = load_session_index()
    order = index.get("session_order", [])
    if not order:
        return None
    latest_id = order[-1]
    log_path = SESSION_LOGS_DIR / f"{latest_id}.json"
    if log_path.exists():
        return json.loads(log_path.read_text())
    return None


def load_recent_sessions(n: int = 5) -> List[dict]:
    index = load_session_index()
    order = index.get("session_order", [])
    recent_ids = order[-n:]
    sessions = []
    for sid in recent_ids:
        log_path = SESSION_LOGS_DIR / f"{sid}.json"
        if log_path.exists():
            sessions.append(json.loads(log_path.read_text()))
    return sessions


def load_tasks() -> list:
    if TASKS_PATH.exists():
        return json.loads(TASKS_PATH.read_text())
    return []


def load_bugs_md() -> str:
    if BUGS_PATH.exists():
        return BUGS_PATH.read_text()
    return ""


def load_project_state_md() -> str:
    if PROJECT_STATE_PATH.exists():
        return PROJECT_STATE_PATH.read_text()
    return ""


def load_latest_state_md() -> str:
    if LATEST_STATE_PATH.exists():
        return LATEST_STATE_PATH.read_text()
    return ""


def build_memory_context(n_recent_sessions: int = 5) -> Dict[str, Any]:
    return {
        "session_index": load_session_index(),
        "latest_session": load_latest_session(),
        "recent_sessions": load_recent_sessions(n_recent_sessions),
        "tasks": load_tasks(),
        "bugs_md": load_bugs_md(),
        "project_state_md": load_project_state_md(),
        "latest_state_md": load_latest_state_md(),
    }


def print_memory_summary():
    ctx = build_memory_context()
    index = ctx["session_index"]
    latest = ctx["latest_session"]
    tasks = ctx["tasks"]
    bugs = ctx["bugs_md"]

    print("=" * 60)
    print("PROJECT MEMORY SUMMARY")
    print("=" * 60)

    phases = index.get("phases", {})
    print(f"\nPhases ({len(phases)}):")
    for pid, pdata in phases.items():
        print(f"  {pid}: {pdata['name']} — {pdata['status']}")

    if latest:
        print(f"\nLatest session: {latest.get('session', 'unknown')}")
    print(f"\nTotal sessions logged: {len(index.get('sessions', {}))}")
    print(f"Tasks: {len([t for t in tasks if t.get('status') == 'completed'])} completed / {len(tasks)} total")

    open_bugs = bugs.count("Status: Open")
    fixed_bugs = bugs.count("Status: Fixed")
    print(f"Bugs: {fixed_bugs} fixed / {open_bugs + fixed_bugs} total")
    print("=" * 60)
