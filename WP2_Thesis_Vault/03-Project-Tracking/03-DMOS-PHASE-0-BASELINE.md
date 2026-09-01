# Digital Marketing OS — Phase 0 Baseline

Status: READY FOR HUMAN APPROVAL

This document closes the Phase 0 planning gaps identified during repository inspection. The requested project directory currently contains architecture HTML documents but no application source repository. This baseline therefore defines what the first implementation agent should create once the source repository is available.

## 1. v0.1 product boundary

The first pilot is intentionally small:

- one workspace and one client;
- one measurable marketing goal;
- one research run with cited sources;
- one approved strategy;
- one campaign with copy, image, and short-video briefs;
- two publishing channels, initially in dry-run or sandbox mode;
- human approval before any external publication;
- basic metrics ingestion and a recommendation for the next experiment.

Out of scope for v0.1: autonomous publishing, ad-spend changes, multi-region billing, a general-purpose CRM, fully autonomous outbound sales, custom model training, and exposing Wan2GP as a paid hosted feature.

## 2. Proposed stack decision

| Boundary | Decision | Why | Phase 0 constraint |
|---|---|---|---|
| Web UI | Next.js + TypeScript | Good fit for an operator dashboard and typed API client | Use one app; do not build a public marketing site yet |
| Domain API | FastAPI + Python | Matches the AI/media ecosystem and produces an OpenAPI contract | Keep business rules in service modules, not route handlers |
| Transactional data | PostgreSQL through Supabase | One local workflow can provide Postgres, Auth, Storage, and local tooling | Use migrations and seed data; never edit production schema manually |
| Authentication | Supabase Auth | Avoid inventing password, session, and OAuth handling in v0.1 | All domain queries must be workspace-scoped |
| File storage | StorageProvider abstraction; Supabase Storage locally, S3-compatible storage later | Media files should not live in Postgres or the app filesystem | Store metadata, checksum, and provenance in Postgres |
| Job signaling | Redis | Appropriate for ephemeral queue, locks, progress events, and rate limits | Redis is not the source of truth for jobs or assets |
| Workflow runtime | LangGraph | Supports durable execution, persistence, streaming, and human-in-the-loop workflows | Persist serializable state; keep external side effects in idempotent tasks |
| Model gateway | LiteLLM behind LLMProvider | Centralizes model selection, fallback, budgets, and observability | No feature may hardcode a vendor SDK |
| LLM observability | Langfuse later; structured application logs immediately | Langfuse is useful but its self-hosted stack adds Postgres, ClickHouse, Redis, and workers | Start with logs and trace IDs; add Langfuse after the first vertical slice |
| Media | MediaProvider adapters | MoneyPrinterTurbo is the first short-video worker candidate | Wan2GP remains disabled until commercial hosting rights are confirmed |
| Publishing | Publisher adapters | Keeps channel APIs replaceable | Start with fake publisher and one sandbox channel |

The Supabase CLI can create a version-controlled `supabase/` directory and run the local Postgres/Auth/Storage stack, but it requires a Docker-compatible runtime. Supabase explicitly describes the local stack as development-only, with default credentials, no TLS, and no rate limiting; it must not be exposed to the internet. [Supabase local CLI](https://supabase.com/docs/guides/local-development/cli/getting-started) · [Supabase local workflow](https://supabase.com/docs/guides/local-development/cli-workflows)

## 3. Runtime prerequisites

Before Phase 1, the operator must choose one local container runtime:

1. Docker Desktop for Mac (recommended for the first run), or
2. Podman, OrbStack, Rancher Desktop, or Colima if Docker-compatible behavior is verified.

Docker Desktop for Mac requires a supported macOS version and at least 4 GB RAM; the current Docker documentation also notes that the latest releases may require macOS Sonoma or later. Supabase recommends at least 7 GB RAM for starting its complete local stack. [Docker Mac installation](https://docs.docker.com/desktop/setup/install/mac-install/) · [Supabase CLI requirements](https://supabase.com/docs/reference/cli/supabase-orgs-list)

Required checks:

```text
git --version
node --version              # Node 20+ is required by the Supabase CLI when installed through npm
python3 --version
docker version              # or a verified Docker-compatible runtime
docker compose version
```

The project must not proceed to service integration until the container runtime passes a hello-world test and local ports are documented.

## 4. Repository structure to create

```text
dm proj/
├── apps/
│   ├── web/                    # Next.js operator UI
│   └── api/                    # FastAPI application
├── packages/
│   ├── contracts/              # OpenAPI-generated or shared schemas
│   └── provider-contracts/     # Research, LLM, media, publisher, metrics ports
├── workers/
│   ├── workflow/               # LangGraph workflows
│   ├── jobs/                   # Redis-backed job consumers
│   └── media/                  # Isolated media worker adapters
├── supabase/
│   ├── config.toml
│   ├── migrations/
│   └── seed.sql
├── docs/
│   ├── adr/
│   ├── api/
│   ├── security/
│   └── licensing/
├── infra/
│   └── compose/                # only project-owned supporting services
├── .env.example
├── AGENTS.md
├── README.md
└── Makefile or task runner
```

Do not copy MoneyPrinterTurbo or Wan2GP into the core repository during Phase 0. Run them as separately versioned workers and connect through a contract.

## 5. Core entities and minimum fields

All entities below require `id`, `created_at`, `updated_at`, and an immutable audit event for sensitive state changes. Tenant-owned entities require `workspace_id`.

| Entity | Minimum fields | State / rule |
|---|---|---|
| Workspace | name, owner_user_id | Tenant boundary |
| Membership | workspace_id, user_id, role | Roles: owner, admin, editor, reviewer, viewer |
| Client | workspace_id, name, timezone, status | Client belongs to one workspace |
| BrandKit | client_id, voice, colors, prohibited_claims, assets | Versioned; never overwrite approved version |
| Goal | client_id, objective, audience, offer, KPI, deadline, constraints | `draft → approved → active → closed` |
| ResearchRun | goal_id, provider, status, started_at, completed_at, error | `queued → running → succeeded/failed/cancelled` |
| Source | research_run_id, url, title, retrieved_at, excerpt, hash, citation | Keep provenance and retrieval timestamp |
| Strategy | goal_id, research_run_id, version, structured_json, model, prompt_version | `draft → in_review → approved/rejected` |
| Campaign | client_id, strategy_id, name, objective, status | Cannot activate without approved strategy |
| ContentBrief | campaign_id, channel, format, angle, CTA, constraints | Input to production jobs |
| MediaJob | brief_id, provider, input_json, status, progress, error_code | Idempotency key required |
| Asset | client_id, media_job_id, storage_uri, mime_type, checksum, provenance | `draft → qa → pending_approval → approved/rejected` |
| Approval | subject_type, subject_id, reviewer_id, decision, comment | Append-only decision record |
| PublishJob | asset_id, channel, scheduled_at, provider, status, external_id | Must reference approved asset and strategy |
| MetricFact | campaign_id, publish_job_id, channel, metric, value, observed_at, source | Upsert by source event identity |
| AuditEvent | workspace_id, actor, action, subject, before, after, request_id | Never store secrets in before/after payloads |

## 6. Initial API contract

The API is the control plane. External providers never write directly to domain tables.

```text
POST /api/v1/workspaces
POST /api/v1/clients
POST /api/v1/clients/{client_id}/brand-kits
POST /api/v1/goals
POST /api/v1/research-runs
GET  /api/v1/research-runs/{run_id}
POST /api/v1/strategies/generate
POST /api/v1/strategies/{strategy_id}/approve
POST /api/v1/strategies/{strategy_id}/reject
POST /api/v1/campaigns/from-strategy
POST /api/v1/media/jobs
GET  /api/v1/media/jobs/{job_id}
POST /api/v1/assets/{asset_id}/approve
POST /api/v1/assets/{asset_id}/reject
POST /api/v1/publish/jobs
POST /api/v1/webhooks/publish/{provider}
POST /api/v1/metrics/ingest
GET  /api/v1/campaigns/{campaign_id}/performance
POST /api/v1/optimization/recommend
GET  /health
GET  /ready
```

Every mutating request must support an `Idempotency-Key` header. Every response should include a request ID. Long-running operations return a job ID and status rather than holding an HTTP request open.

## 7. Provider contracts

```text
ResearchProvider.run(query, constraints) -> ResearchResult
LLMProvider.generate(schema, messages, model_policy) -> StructuredResult
MediaProvider.submit(brief, input_assets) -> MediaJob
MediaProvider.status(provider_job_id) -> MediaProgress
Publisher.validate(payload) -> ValidationResult
Publisher.publish(payload, idempotency_key) -> DeliveryResult
MetricsProvider.fetch(account, time_window) -> MetricPage
StorageProvider.put(stream, metadata) -> StoredObject
StorageProvider.get(uri) -> stream
```

The contract must include timeout, cancellation, retryability, provider error code, provenance, cost estimate, and output validation. A mock provider for every contract is required before connecting a real provider.

## 8. Workflow and side-effect rules

```text
goal.created
  → research.run
  → evidence.validated
  → strategy.draft
  → human.strategy_approved
  → campaign.created
  → content.briefs_created
  → media.jobs_completed
  → human.assets_approved
  → publish.dry_run
  → human.publish_authorized
  → publish.delivered
  → metrics.ingested
  → optimization.recommendation
```

LangGraph is appropriate for the resumable workflow because its documented persistence/checkpoint model supports fault tolerance and human pauses. Workflow state must be JSON-serializable, and nondeterministic work belongs inside tasks. [LangGraph reference](https://langchain-ai.github.io/langgraph/reference/) · [LangGraph persistence](https://langchain-ai.github.io/langgraph/concepts/time-travel/) · [LangGraph human-in-the-loop](https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/breakpoints/)

Side-effect rules:

- generating a draft is reversible;
- uploading an asset is idempotent by checksum and job ID;
- publishing requires both approved asset and explicit authorization;
- webhook handlers verify signatures and tolerate replay;
- metrics ingestion is append-or-upsert, never destructive;
- optimization produces recommendations only in v0.1.

## 9. Environment contract

Create `.env.example` with names only. Keep real values in a local secret manager or untracked `.env` file.

```text
APP_ENV=local
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
DATABASE_URL=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
REDIS_URL=redis://localhost:6379/0
STORAGE_PROVIDER=supabase
STORAGE_BUCKET=marketing-assets
LLM_PROVIDER=litellm
LITELLM_BASE_URL=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
RESEARCH_PROVIDER=
RESEARCH_PROVIDER_API_KEY=
PUBLISHING_PROVIDER=
PUBLISHING_PROVIDER_API_KEY=
LANGFUSE_ENABLED=false
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
WAN2GP_ENABLED=false
WAN2GP_BASE_URL=
```

Rules: fail fast when required secrets are missing, redact keys from logs, separate local/staging/production values, rotate credentials, and never put provider keys in browser code.

## 10. Reuse and licensing gates

MoneyPrinterTurbo is MIT-licensed in its repository, so an adapter or separately distributed worker can generally be evaluated for reuse subject to retaining the license notice and checking its dependencies. [MoneyPrinterTurbo license](https://github.com/harry0703/MoneyPrinterTurbo/blob/main/LICENSE)

Wan2GP/WanGP currently publishes a Community License 2.0. Its binding terms distinguish internal/company/agency/client use from restricted commercialization. Paid API, hosted, SaaS, white-label, OEM, or embedded access requires a separate written commercial/reseller license. The output and model/weight licenses must also be checked independently. Therefore:

- keep Wan2GP out of the core distribution;
- keep `WAN2GP_ENABLED=false` by default;
- use it first only as a private/internal worker;
- maintain a `THIRD_PARTY_NOTICES` file for any redistributed bundle;
- obtain written permission before exposing it as a paid customer-facing backend.

Source: [Wan2GP license](https://github.com/deepbeepmeep/Wan2GP/blob/main/LICENSE.txt)

Langfuse can be self-hosted with Docker Compose, but its current architecture adds web and worker containers plus Postgres, ClickHouse, and Redis/Valkey. It is a good observability phase, not a prerequisite for the first API/database slice. [Langfuse self-hosting](https://langfuse.com/self-hosting)

## 11. Security and compliance acceptance criteria

- Every request is authenticated or explicitly marked public.
- Every workspace-owned query includes tenant authorization.
- RLS or equivalent database policies are tested for cross-tenant reads and writes.
- Provider tokens are encrypted at rest or stored outside the database.
- Uploads validate MIME type, size, extension, checksum, and malware-scan status where available.
- Webhook signatures, timestamps, and replay protection are tested.
- Research source terms, robots rules, privacy, and personal-data retention are documented.
- AI output is labeled as draft until reviewed.
- Claims in strategy/content reference stored evidence or are marked as hypotheses.
- Local Supabase is never exposed to public traffic.
- Logs contain request IDs and job IDs but no secrets or unnecessary personal data.

## 12. Phase 0 acceptance tests

Phase 0 is complete when an agent can prove all of the following without implementing the full product:

1. A clean checkout can reproduce the documented directory and commands.
2. The chosen container runtime passes a hello-world test.
3. `supabase init`, local startup, migration, reset, and seed procedures are documented.
4. The API contract is stored as OpenAPI or equivalent typed schemas.
5. The entity/state model and tenant boundary are documented.
6. Provider contracts have mock request/response examples.
7. `.env.example` contains no secrets and all required names are documented.
8. The approval and publishing safety rules are explicit.
9. MoneyPrinterTurbo and Wan2GP licensing decisions are recorded.
10. The owner has approved the v0.1 scope and the first real implementation phase.

## 13. Exact Phase 0 agent prompt

```text
Work in /Users/vinaykumar/dm proj.

This folder currently contains planning HTML documents and PHASE-0-BASELINE.md, not an application repository. Inspect the folder first and do not assume source code exists.

Implement only Phase 0 foundation preparation:

1. If no source repository exists, stop and report BLOCKED; do not invent a codebase.
2. If the source repository is present, inspect it and preserve existing work.
3. Apply the decisions in PHASE-0-BASELINE.md.
4. Create or update README.md, AGENTS.md, .env.example, docs/adr, docs/api, docs/security, and docs/licensing as appropriate.
5. Do not connect production credentials.
6. Do not copy MoneyPrinterTurbo or Wan2GP into the core repository.
7. Do not implement business features yet.
8. Run only safe repository and configuration checks.

End with:
STATUS: PASS or BLOCKED
REPOSITORY_FOUND: yes or no
FILES_CHANGED:
DECISIONS_CONFIRMED:
OPEN_HUMAN_DECISIONS:
COMMANDS_RUN:
TESTS:
NEXT_PHASE:
```

## 14. Human decisions still required

Before Phase 1, approve these items:

- the exact application source repository/path;
- Next.js + FastAPI + Supabase as the v0.1 stack;
- Docker Desktop or another Docker-compatible runtime;
- the first pilot client, channels, and KPI;
- whether local Supabase or managed Supabase will be used for development;
- whether Wan2GP is private/internal-only until a commercial license is obtained;
- whether Langfuse is deferred until after the first vertical slice.

Once these are approved and the source repository exists, Phase 1 can begin with platform foundation rather than further architecture discovery.
