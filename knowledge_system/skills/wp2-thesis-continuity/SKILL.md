---
name: wp2-thesis-continuity
description: Maintains continuity for the CERN DRD8 WP2 EPITA thesis by reading the project evidence register, preserving verified project framing, mapping chapters to sources and visuals, preventing duplication, and recording unresolved gaps. Use for any thesis-writing, manuscript-editing, evidence-mapping, or future-orchestrator task in this repository.
---

# WP2 Thesis Continuity

## Required context

Before thesis work, read:

- `knowledge_system/THESIS_CONTINUITY.md`
- `knowledge_system/latest_state.md`
- `knowledge_system/session_index.json`
- `WP2_Thesis_Vault/09-Thesis-Knowledge-Graph/03-THESIS-EVIDENCE-MAP.md`
- `WP2_Thesis_Vault/09-Thesis-Knowledge-Graph/05-CLAIMS-REGISTER.md`
- the relevant source code, report, presentation, PDF, or visual asset files

## Evidence discipline

- Distinguish prototype, production direction, implemented behavior, demonstration, migration, proposal, blocked work, and untested work.
- Treat “local-first” as self-hosted execution under project control, not as “the system runs on the Mac”. The Mac was the constrained prototype environment; the intended production system is server-hosted and remotely accessible.
- Do not convert plans, generated diagrams, or presentation claims into measured results without supporting logs or benchmarks.
- Preserve unresolved facts in the gaps register rather than filling them by inference.

## Chapter and page workflow

1. Announce the chapter, subtopics, target pages, source files, and intended visuals.
2. Audit the evidence and classify each claim.
3. Choose one primary visual per concept and record its assignment in `THESIS_CONTINUITY.md`.
4. Write the manuscript with crisp human-readable prose, tables, and captions; avoid repeating earlier chapters.
5. Render the DOCX and inspect all affected pages plus both pagination boundaries.
6. Update `control_center/TASKS.json`, `knowledge_system/latest_state.md`, `knowledge_system/session_index.json`, and a timestamped session log.

## Visual selection

Prefer readable technical diagrams and real project screens. Use `end-to-end-multimodal.png` for the main pipeline, `architecture-diagram.png` for the historical prototype, `result-with-context.png` for a grounded researcher workflow, and the OCR/source-verification/processing screens for evidence. Do not use decorative illustrations as primary technical evidence.

## Deliverable quality gate

- No unsupported claims presented as facts.
- No duplicated narrative or repeated screenshots without a new analytical purpose.
- No placeholder wording such as “draft” in the official manuscript.
- No blank-page pagination introduced by tables or figures.
- All edits are reflected in the project state and session log.
