# BOOTSTRAP.md — System Entry Point

This file is the FIRST file any AI agent must read.

---

## 1. SYSTEM STATE SOURCE OF TRUTH

Always read in this order:

1. control_center/PROJECT_STATE.md
2. control_center/TASKS.json
3. knowledge_system/latest_state.md
4. control_center/ARCHITECTURE.mmd

---

## 2. EXECUTION LOOP (MANDATORY)

For every task:

STEP 1 — Understand state
STEP 2 — Identify task from TASKS.json
STEP 3 — Execute ONE task only
STEP 4 — Update:
  - TASKS.json
  - BUGS.md (if needed)
  - CHANGELOG.md
  - latest_state.md
STEP 5 — Create session log in:
  knowledge_system/session_logs/

---

## 3. SINGLE SOURCE RULE

If something is not in files:

→ It does NOT exist

No chat memory is allowed.

---

## 4. FAILURE PREVENTION RULE

Never:
- skip logging
- skip state update
- skip task update

If any of these fail → execution is considered INVALID

---

## 5. SYSTEM GOAL

Maintain a fully traceable CERN-grade RAG system with:

- reproducibility
- auditability
- no lost context
- full history of decisions
