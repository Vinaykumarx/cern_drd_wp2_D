# DMOS Project Status & Agent Coordination

This is the shared coordination board for every human and AI orchestrator working on DMOS. Read it before starting work and update it at handoff. The file tracks the current snapshot; the activity log preserves the coordination history.

Last updated: 2026-08-27
Coordinator: project owner

## Operating rules

1. One agent claims one task and an explicit file/path ownership set.
2. No agent edits another active agent's owned files without coordination.
3. Every agent works in its own branch or Git worktree.
4. A task is not considered started until it appears in the Active Work table.
5. Update the table at start, when blocked, and before handoff.
6. Append to the Activity Log; do not rewrite another agent's log entry.
7. A merge is allowed only after the definition of done and tests pass.
8. If two tasks require the same contract, schema, or shared file, mark one as a dependency instead of editing in parallel.

## Synchronization model

Git branches are not a live shared database. An uncommitted status change in one worktree is invisible to other worktrees. Agents must commit and push their branch when a claim, blocker, or handoff needs to be visible to remote collaborators. Other agents should fetch before claiming work. The coordinator should periodically merge or manually reconcile the status snapshot into the baseline branch.

For truly live coordination, use a single coordinator process or external shared store in addition to this file. This repository file is the durable, reviewable record; it is not a replacement for a lock service.

## Current snapshot

| Field | Value |
|---|---|
| Repository | `Vinaykumarx/DMOS` |
| Baseline branch | `codex/phase-0-baseline` |
| Current phase | Phase 1 — foundation skeleton |
| Overall status | IN PROGRESS — Phase 3 claimed |
| Latest baseline commit | `a42cab1` |
| Production publishing | Disabled |
| Wan2GP | Disabled pending licensing decision |
| Primary blocker | None — Phase 1 underway |

## Active work

| Agent | Branch / worktree | Task | Owned paths | Status | Started | Updated | Depends on |
|---|---|---|---|---|---|---|---|
| Codex | `codex/phase-0-baseline` | Baseline architecture and coordination setup | `README.md`, `AGENTS.md`, `PHASE-0-BASELINE.md`, `PROJECT_STATUS.md` | complete | 2026-08-27 | 2026-08-27 | owner scope approval |
| Antigravity | `agent/antigravity/phase-1-foundation` | Phase 1 service skeleton, runtime, health checks | `apps/`, `infra/`, `packages/`, `workers/`, `supabase/`, `.env.example`, `Makefile`, `docs/adr/` | COMPLETE | 2026-08-27 | 2026-08-27 | Phase 0 complete |
| Claude Code | `agent/claude/phase-2-domain-auth` | Phase 2 Domain & Auth Integration | `apps/api/app/auth.py`, `apps/api/app/models/`, `apps/api/app/routers/`, `apps/api/tests/`, `apps/api/alembic/versions/`, `supabase/migrations/` | complete | 2026-08-30 | 2026-08-30 | Phase 1 complete |

When claiming work, add a row with the exact branch and paths. Use `BLOCKED` if progress cannot continue. Remove a row only after its handoff is recorded; move the completed work to the Completed work table.

## Planned work allocation

| Phase | Suggested owner | Scope | Reserved paths | Dependency |
|---|---|---|---|---|
| Phase 0 approval | Owner | Approve v0.1 scope, stack, runtime, pilot, and license gates | `PROJECT_STATUS.md` decision section | none |
| Phase 1 foundation | Codex or Claude Code | Service skeleton, runtime, health checks, CI | `apps/`, `infra/`, root config | Phase 0 approval |
| Phase 2 domain/auth | Claude Code | Migrations, tenant security, auth, audit | `supabase/migrations/`, `apps/api/domain/` | Phase 1 |
| Phase 3 provider contracts | OpenCode | Ports, job envelope, mocks, contract tests | `packages/provider-contracts/`, `workers/contracts/` | Phase 2 API shape |
| Phase 4 research | Gemini CLI + implementation agent | Research adapter, sources, citations | `workers/research/`, `apps/api/research/` | Phase 3 |
| Phase 5 strategy/approval | Codex | LangGraph workflow, LLM gateway, review states | `workers/workflow/`, `apps/api/strategies/` | Phase 4 |
| Phase 6 campaign/content | Claude Code | Campaign graph, briefs, QA | `apps/api/campaigns/`, `apps/web/` | Phase 5 |
| Phase 7 media | Media agent | MoneyPrinterTurbo adapter; Wan2GP feature flag | `workers/media/`, `docs/licensing/` | Phase 3 and license gate |
| Phase 8 publishing | Publishing agent | Fake publisher, one sandbox channel, webhooks | `workers/publishing/`, `apps/api/webhooks/` | Phase 6 and human approval |
| Phase 9 measurement | Analytics agent | Metrics schema, ingestion, dashboards | `apps/api/metrics/`, `workers/metrics/` | Phase 8 |

These are allocation suggestions, not automatic assignments. An agent must claim a row before implementing it.

## Decisions and dependencies

- Core owns domain entities, tenant security, approvals, audit events, and provider contracts.
- External repositories are isolated workers behind adapters; they do not own DMOS business state.
- Postgres is transactional truth. Redis is ephemeral signaling/queue infrastructure.
- Long-running jobs return a job ID and are retryable/idempotent.
- Publishing and spend-changing actions require explicit human authorization.
- Wan2GP stays disabled until the intended hosted/API commercialization is legally cleared.

## Handoff template

Every agent must append this block before stopping:

```text
### YYYY-MM-DD HH:MM — <agent> — <phase>
Branch: agent/<tool>/<phase>-<name>
Status: PASS | BLOCKED | PAUSED
Task: <one sentence>
Files changed: <paths>
Files intentionally untouched: <paths>
API/schema changes: <summary or none>
Tests and commands: <commands + results>
Dependencies created: <items>
Dependencies consumed: <items>
Known risks: <items or none>
Next action: <exact next task>
```

## Activity log

### 2026-08-27 — Codex — repository setup

- Connected the local repository to `https://github.com/Vinaykumarx/DMOS.git`.
- Created branch `codex/phase-0-baseline`.
- Preserved the architecture HTML files and Phase 0 baseline.
- Added this coordination board and agent instructions.
- No application features have been implemented yet.

### 2026-08-27 04:49 UTC — Antigravity — Phase 1 foundation

Branch: `agent/antigravity/phase-1-foundation`
Status: PASS
Task: Implemented Phase 1 foundation skeleton — Next.js web app, FastAPI API, Docker Compose, Supabase config, DB migrations, health endpoints, typed config, structured logging, and smoke tests.
Files changed: `apps/web/`, `apps/api/`, `supabase/`, `infra/compose/`, `packages/contracts/`, `packages/provider-contracts/`, `workers/`, `docs/adr/`, `.env.example`, `Makefile`, `.gitignore`
Files intentionally untouched: `README.md`, `AGENTS.md`, `PHASE-0-BASELINE.md`, `TASKS.md`, `dashboard.html`, architecture HTML files
API/schema changes: `GET /health`, `GET /ready` added to FastAPI app; Alembic migration 0001 creates workspaces, memberships, audit_events tables
Tests and commands: `cd apps/api && .venv/bin/pytest tests/ -v` → 12/12 PASSED; `cd apps/web && npm test` → 4/4 PASSED; ruff lint CLEAN; tsc typecheck CLEAN
Dependencies created: Phase 2 may extend Alembic migrations from 0001 baseline; Phase 6 replaces apps/web home page
Dependencies consumed: Phase 0 baseline approved
Known risks: Docker not installed on dev machine — Docker Compose and Supabase local require Docker Desktop before service-level integration tests can run
Next action: Phase 2 (domain/auth) — Claude Code should add Supabase Auth, tenant RLS, domain entities, and remaining API routes

### 2026-08-30 23:45 UTC — Claude Code — Phase 2 domain/auth

Branch: agent/claude/phase-2-domain-auth
Status: PASS
Task: Implemented Phase 2 Domain & Auth Integration - added Supabase Auth verification, workspace/role RLS checks and isolation middlewares, SQLAlchemy models for Domain Entities (Client, BrandKit, Goal, Strategy), Alembic and Supabase SQL migrations with RLS policies, and nested CRUD APIs (workspaces/{workspace_id}/...) with audit logging, and wrote integration/isolation tests.
Files changed: `apps/api/app/main.py`, `apps/api/app/models/`, `apps/api/app/routers/`, `apps/api/app/schemas/domain.py`, `apps/api/app/auth.py`, `apps/api/app/utils/audit.py`, `apps/api/app/redis_client.py`, `apps/api/pyproject.toml`, `apps/api/tests/`, `supabase/migrations/20260827000002_domain_models.sql`, `apps/api/alembic/versions/0002_domain_models.py`
Files intentionally untouched: `apps/web/`
API/schema changes: Add nested workspace routers for Clients (`/workspaces/{workspace_id}/clients`), Brand Kits (`/workspaces/{workspace_id}/brand-kits`), Goals (`/workspaces/{workspace_id}/goals`), and Strategies (`/workspaces/{workspace_id}/strategies`); Database tables: `clients`, `brand_kits`, `goals`, `strategies`, and `audit_events` created with foreign key constraints, indexes, and timezone-aware timestamps.
Tests and commands: `pytest apps/api/tests/ -v && ruff check apps/api/ && mypy apps/api/` -> ALL PASSED/CLEAN
Dependencies created: Phase 3 provider contracts can now consume Domain entity models and client APIs
Dependencies consumed: Phase 1 foundation complete
Known risks: None
Next action: Phase 3 (provider contracts)

## Conflict resolution

If an agent discovers overlapping ownership:

1. Stop editing the overlapping path.
2. Add a `BLOCKED` note to Active work.
3. Record the conflicting branch and required interface.
4. Ask the coordinator to split the file, sequence the work, or designate one owner.

For simultaneous work, prefer separate Git worktrees under `/Users/vinaykumar/dmos-worktrees/`. Never switch branches in a worktree currently being used by another agent.
