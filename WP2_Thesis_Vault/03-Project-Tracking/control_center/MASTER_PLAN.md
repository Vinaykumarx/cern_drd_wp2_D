# MASTER PLAN — CERN Multimodal RAG Architecture Roadmap

## Phase A — Audit & Discovery ✅
- [x] Map all ingestion paths
- [x] Map all retrieval paths
- [x] Identify direct DB bypasses
- [x] Document canonical vs non-canonical patterns

## Phase B — Runtime Safety Layer ✅
- [x] CanonicalGate — call-stack validation
- [x] SystemValidator — AST-based forbidden pattern scanner
- [x] Wired SystemValidator into FastAPI startup
- [x] Deprecated 9 standalone extraction scripts
- [x] Added 3 wrapper methods to LanceVectorStore

## Phase C — Critical Bug Fixes ✅
- [x] TASK-0001: LanceDB vector count desync
- [x] TASK-0002: Async event loop blocking
- [x] TASK-0003: Knowledge graph browser freeze

## Phase D — Global Memory Layer ✅
- [x] session_index.json — centralized session tracking
- [x] project_memory_loader.py — state file loader
- [x] AGENTS.md — session index update rule

## Phase E — System Lock ✅
- [x] architecture_validator.py — forbidden pattern enforcement
- [x] bootstrap.py — unified runtime context + startup enforcement
- [x] FastAPI refuses startup on CRITICAL violations
- [x] 11 executable scripts enforce bootstrap
- [x] SYSTEM_LOCK.md — canonical path documentation

## Phase F — Control Center Dashboard ✅
- [x] Read-only visual dashboard (port 8899)
- [x] System Health, Architecture Lock, Pipeline Flow
- [x] Active Tasks, Bug Tracker, Memory Layer
- [x] Future Architecture Roadmap
- [x] Integrated with bootstrap + architecture_validator

## Phase G — Ingestion Modernization (Next)
- [ ] TASK-0004: Replace pymupdf4llm with Docling
- [ ] TASK-0005: ColPali Visual Retrieval
- [ ] TASK-0007: Hybrid Chunking with Nomic

## Phase H — Performance & Scale (Planned)
- [ ] TASK-0008: Graph Pagination & Query Optimization
- [ ] TASK-0009: Docker Container Optimization
- [ ] TASK-0010: E2E Testing Suite
- [ ] TASK-0011: Performance Benchmarking

## Phase I — Polish & Docs (Planned)
- [ ] TASK-0012: Architecture Documentation
- [ ] TASK-0013: Physics-Aware Prompts

---

## Legend
- ✅ Completed
- 🔄 In Progress
- ⬜ Not Started
- ❌ Blocked
