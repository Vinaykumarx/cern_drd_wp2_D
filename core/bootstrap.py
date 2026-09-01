"""
Bootstrap — Unified runtime context loader for architecture enforcement.

Orchestrates:
  - project_memory_loader: loads session_index, task list, bug list, project state
  - architecture_validator: detects forbidden patterns, deprecated scripts
  - system_validator: AST-based canonical architecture scanning

Provides:
  - RuntimeContext: single source of runtime truth
  - require_bootstrap(): scripts must call this before execution
  - startup_enforce(): FastAPI startup enforcement (refuses on violation)
"""

import os
import sys
import json
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_bootstrapped: bool = False
_runtime_context: Optional["RuntimeContext"] = None


class RuntimeContext:
    def __init__(self):
        self.project_root: Path = PROJECT_ROOT
        self.session_index: dict = {}
        self.tasks: list = []
        self.bugs_md: str = ""
        self.project_state_md: str = ""
        self.latest_state_md: str = ""
        self.validation_report: dict = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_root": str(self.project_root),
            "session_index": self.session_index,
            "tasks": self.tasks,
            "validation_report": self.validation_report,
        }


def initialize_context() -> RuntimeContext:
    from core.project_memory_loader import (
        load_session_index,
        load_tasks,
        load_bugs_md,
        load_project_state_md,
        load_latest_state_md,
        load_latest_session,
    )
    ctx = RuntimeContext()
    ctx.session_index = load_session_index()
    ctx.tasks = load_tasks()
    ctx.bugs_md = load_bugs_md()
    ctx.project_state_md = load_project_state_md()
    ctx.latest_state_md = load_latest_state_md()
    return ctx


def run_validations(ctx: RuntimeContext, exit_on_fail: bool = False) -> Dict[str, Any]:
    from core.architecture_validator import run_architecture_validation
    report = run_architecture_validation(exit_on_fail=exit_on_fail)
    ctx.validation_report = report
    return report


def startup_enforce(exit_on_critical: bool = True) -> RuntimeContext:
    ctx = initialize_context()
    print("[Bootstrap] Loading runtime context...")
    print(f"  Tasks: {len(ctx.tasks)}")
    print(f"  Sessions: {len(ctx.session_index.get('sessions', {}))}")
    report = run_validations(ctx, exit_on_fail=False)
    critical_count = report.get("by_severity", {}).get("CRITICAL", 0)
    high_count = report.get("by_severity", {}).get("HIGH", 0)
    if critical_count > 0 and exit_on_critical:
        print(f"[Bootstrap] REFUSING STARTUP — {critical_count} CRITICAL violations found.")
        for v in report["violations"]:
            if v["severity"] == "CRITICAL":
                print(f"  [CRITICAL] {v['file']}:{v['line']} — {v['message']}")
        sys.exit(1)
    if report["status"] == "FAIL":
        print(f"[Bootstrap] Warning: {report['total_violations']} non-critical violations (severity: {report['by_severity']})")
    global _bootstrapped, _runtime_context
    _bootstrapped = True
    _runtime_context = ctx
    print("[Bootstrap] Context loaded. System architecture locked.")
    return ctx


def require_bootstrap():
    if not _bootstrapped:
        print("[Bootstrap] Runtime context not loaded. Running bootstrap...")
        startup_enforce(exit_on_fail=True)


def get_runtime_context() -> RuntimeContext:
    require_bootstrap()
    return _runtime_context
