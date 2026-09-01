# DMOS Agent Instructions

## Repository

This is the Digital Marketing OS repository. The target workflow is:

```text
Client → Goal → Research → Strategy → Campaign → Content → Approval → Publishing → Metrics → Optimization
```

## Required workflow for every agent

1. Inspect the repository and current git status before editing.
2. Read `PHASE-0-BASELINE.md` and the relevant implementation plan.
3. Work only on the assigned phase.
4. Use a dedicated branch named `agent/<tool>/<phase>-<short-name>`.
5. Do not commit secrets, real API keys, or customer data.
6. Keep external tools behind provider adapters.
7. Preserve existing work and never use destructive git commands.
8. Add tests for new behavior and run the project's checks.
9. Stop after the assigned phase; do not begin the next phase automatically.
10. Read and update `PROJECT_STATUS.md` before starting, when blocked, and at handoff.
11. Claim exact file/path ownership in `PROJECT_STATUS.md` before editing.
12. Use `TASKS.md` for backlog items and `PROJECT_STATUS.md` for live agent coordination.

## Handoff format

```text
STATUS: PASS | BLOCKED
PHASE:
BRANCH:
FILES_CHANGED:
API_OR_SCHEMA_CHANGES:
COMMANDS_RUN:
TEST_RESULTS:
ENVIRONMENT_VARIABLES:
KNOWN_RISKS:
NEXT_PHASE:
```

## Non-overlap rule

The shared status board is the coordination channel. An agent must not edit paths listed as owned by another active agent. If a shared contract or migration is required, record it as a dependency and coordinate the owner before editing. Use separate Git worktrees for simultaneous work.

## Integration boundaries

The core application owns domain entities, tenant security, approvals, audit events, and provider contracts. MoneyPrinterTurbo, Wan2GP, research tools, LLM vendors, and publishing tools must connect through replaceable adapters or isolated workers.

Wan2GP must remain disabled until its current license permits the intended hosted/API use. Do not expose publishing or spend-changing actions without explicit human approval.
