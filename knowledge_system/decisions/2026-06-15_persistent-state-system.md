# Decision: Implement Persistent State & Memory System

**Date**: 2026-06-15
**Status**: Accepted

## Context
AI agents lacked a file-based state system, relying on conversational memory for task tracking and project state. This caused state loss between sessions and mode switches.

## Decision
Create two new directory trees at project root:
- `control_center/` — authoritative project state (TASKS.json, BUGS.md, PROJECT_STATE.md, ARCHITECTURE.mmd, CHANGELOG.md)
- `knowledge_system/` — agent knowledge persistence (latest_state.md, session_logs/, decisions/)

## Rationale
- Single source of truth — no assumptions from chat history
- Mode-switching safe — state is file-based, not conversational
- Audit trail — every interaction generates a session log
- Enables multi-agent collaboration with shared state

## Consequences
- All agents MUST read `PROJECT_STATE.md`, `TASKS.json`, `latest_state.md` before any implementation
- All agents MUST update state files and create session logs after any implementation
- Chat history is no longer considered authoritative
