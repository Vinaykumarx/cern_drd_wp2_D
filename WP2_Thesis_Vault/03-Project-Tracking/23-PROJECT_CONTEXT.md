# COMPLETE PROJECT & USER CONTEXT

This file contains the full context of Vinay's system, projects, workflows, and pending work. Hermes should read this to understand everything.

---

## USER
- **Name:** Vinay
- **Role:** CERN DRD8 WP4 researcher, VR/medical physics engineer, entrepreneur
- **Location:** Works from MacBook Air (Apple M2, 8 GB RAM, 228 GB SSD)
- **Stack:** Python, Node.js, VR/XR (Unity/Unreal), database, web scraping
- **Shell:** zsh
- **Voice input:** Wispr Flow (Electron, ~200 MB)
- **Browser:** Safari (lightest on RAM)
- **ChatGPT:** ChatGPT Atlas (Electron wrapper for chatgpt.com) — pid 90904/90912

## PROJECTS

### 1. CERN DRD8 WP4 — CAD→Geant4 Pipeline
- **Goal:** Convert CATIA CAD models to Geant4 simulation geometry
- **Tools:** CATIA V5 on Windows PC (pcca2063.cern.ch), Geant4, Python
- **Pipeline:** Mac ↔ GitHub (Obsidian vault) ↔ Windows (OpenClaw monitors task queue)
- **Task queue:** `~/cern/Master-Knowledge-Vault/CERN-DRD8-WP4/CATIA_Task_Queue.md`
- **Windows PC:** pcca2063.cern.ch — port 4096 blocked by firewall
- **Linux server:** pc-dt-drd8-llm.cern.ch — not in public DNS, unreachable outside VPN
- **CERN Storage:** Mounted at `/Volumes/Storage-1` — contains 47 MB 25-slide DRD8 presentation + 54 extracted media files
- **Key doc:** `rag-system-architecture-issues.md` (36,741 lines)

### 2. Maxrad — Radiation Damage RAG System
- **Goal:** RAG pipeline for radiation damage literature (semantic scholar, CDS, arxiv)
- **Components:** Research Agent → Verification Agent (cross-encoder reranking) → Synthesis Agent (citation-grounded)
- **Storage:** LanceDB vector DB with material properties, damage mechanisms, simulation data
- **Report:** `CERN_Multimodal_RAG_Architecture_Report.html` (1234 lines, 60 KB) at `~/cernbox/Maxrad-database/`
- **Images:** 25 screenshots in `~/cernbox/Maxrad-database/images/` (43 MB)
- **Presentation:** 25-slide DRD8 Collab Meeting deck (`AI-Assisted-Knowledge-StructuringPPT_full.pptx`)
- **GPU:** RTX 5090 failed (fire incident). A100 RQF3798846 pending.

### 3. LifeLab — VR Medical Physics
- **Goal:** VR-based medical physics training/simulation
- **Status:** Early stage, presentation drafted

## SYSTEM ARCHITECTURE

### Agent Hierarchy
```
Vinay ←→ Hermes (Brain — main agent, memory, skills, Telegram gateway)
              │
    ┌─────────┼──────────────────┐
    │         │                  │
  opencode  cua-driver       research-swarm
  (Body)    (Hands)          (Nightly)
  code ops  screen control   arxiv search
  git/files UI automation    knowledge synthesis
  testing   DALL-E/ChatGPT   report generation
```

### LLM Provider Chain
1. **CERN AccGPT** (`openai/gpt-oss-120b` — reasoning model) — free, CERN-funded
2. **CERN AccGPT** (`hf-qwen3-32b-awq` — 32B, 16K context, more reliable)
3. **Groq** (`llama-3.3-70b-versatile`) — free, 14K req/day
4. **Cohere** (`command-r-08-2024`) — free, 100 req/day
5. **Xiaomi MiMo** (`mimo-v2-pro`) — free tier
6. **OpenRouter** (`nvidia/nemotron-3-ultra-550b-a55b:free`) — rate-limited 429
7. **xAI Grok** — zero credits. Visit https://console.x.ai/team/7fa1f4f7-03e4-4aaa-8dd0-c1fbf19f2e2b

### Key Endpoint
```
CERN AccGPT: https://accgpt-ui.app.cern.ch/api/v1/chat/completions
API key: [removed from public repository; configure through environment variables]
Note: ~30s cooldown, works ~50%. Refresh at https://accgpt-ui.app.cern.ch
```

## COMPLETE TOOL REGISTRY

| Tool | Path | Purpose |
|------|------|---------|
| opencode | ~/.local/share/npm/bin/opencode | Code body — file ops, git, search, bash, testing |
| cua-driver | ~/.local/bin/cua-driver | Screen control via AX API + click/type/hotkey |
| CoreGraphics (Python ctypes) | /tmp/realmouse.py approach | REAL mouse/keyboard events — works with ALL apps |
| telegram-daemon | ~/.local/bin/telegram-daemon | Legacy Telegram 24/7 (PID: /tmp/tg-daemon.pid) |
| tg-reply | ~/.local/bin/tg-reply | Legacy Telegram action handler (AppleScript + LLM) |
| research-swarm | ~/.local/bin/research-swarm | Overnight autonomous research |
| speak | ~/.local/bin/speak | Edge TTS (en-US-AriaNeural, Microsoft neural) |
| session-start/log/save/restore/status | ~/.local/bin/session-* | PostgreSQL session memory tools (port 5432, agent_memory DB) |
| guardian-agent | ~/.local/bin/guardian-agent | Protects setup files from deletion |
| mount-cern-storage | ~/.local/bin/mount-cern-storage | Mounts CERN SMB storage |
| provider-status / provider-status-web | ~/.local/bin/provider-* | Provider health checks (CLI + web on port 9191) |

## SESSION MEMORY
- **PostgreSQL:** `agent_memory` DB on port 5432 (brew postgresql@14)
- **Schema:** sessions (UUIDs), conversations (role+content+tokens), agent_state, checkpoints
- **Current session:** Most recent session with opencode
- **Hermes memory:** FTS5 built-in (just enabled) + Honcho user modeling

## PENDING TASKS (Most Urgent First)

### P0 — DALL-E Diagrams (CURRENT FOCUS)
Generate 4 professional architecture diagrams to replace Mermaid renders in HTML report:
1. Three-Phase Pipeline Architecture
2. CDS Integration Flow
3. LanceDB Schema
4. Full System Architecture

**Approach:** Use CoreGraphics (ctypes) → ChatGPT Atlas → DALL-E → save PNGs
- Reference image: `~/cernbox/Maxrad-database/images/grounded-rag-architecture.png`
- Target: `~/cernbox/Maxrad-database/images/dalle-{name}.png`
- ChatGPT Atlas window at (0,87) to (1710,1112). Chat input at ~(855, 1060).
- Pids: 90904 (main), 90912 (renderer)

### P1 — RLayout Folder
Wait for zip to complete, then delete original folder.

### P2 — OpenClaw on Windows
Ask user to run firewall rule:
```
New-NetFirewallRule -DisplayName 'opencode' -Direction Inbound -Protocol TCP -LocalPort 4096 -Action Allow
```
Then: `opencode attach http://pcca2063.cern.ch:4096`

### P3 — Slide Decks
- Build LifeLab board meeting presentation from drafted 10-slide structure
- Build Maxrad board meeting presentation from drafted 10-slide structure

### P4 — Research Swarm Improvements
- Integrate Tavily API for real web scraping
- Add source citation tracking
- Add multi-agent fact-checking

### P5 — Voice Pipeline
- End-to-end test: Wispr Flow → Hermes → Edge TTS

## KEY FILES & LOCATIONS
- `~/cern/` — Main working directory
- `~/cern/_opencode/AGENTS.md` — Project context for agent
- `~/cern/_opencode/research-reports/` — Research swarm output
- `~/cern/Master-Knowledge-Vault/` — Obsidian vault (520 notes, GitHub-synced)
- `~/cernbox/Maxrad-database/` — CERNBOX-synced project files (5.2 GB)
- `~/cernbox/Maxrad-database/images/` — 25 screenshots (43 MB)
- `~/cernbox/Maxrad-database/CERN_Multimodal_RAG_Architecture_Report.html` — 60 KB report
- `~/.hermes/config.yaml` — Hermes configuration
- `~/.hermes/SOUL.md` — Hermes identity
- `~/.hermes/.env` — Environment variables (API keys)
- `~/.hermes/skills/` — Hermes skills directory
- `~/.config/opencode/opencode.jsonc` — opencode configuration
- `/tmp/tg-daemon.log` — Telegram daemon log
- `/tmp/tg-last.txt` — Last Telegram message

## RECENT SESSION HISTORY (July 1, 2026)

### Key Accomplishments Today
1. **CoreGraphics mouse/keyboard** — Built REAL mouse event script using Python ctypes → CoreGraphics.framework. Proved it works with ChatGPT Atlas (typed "Hello, this is a test from real CoreGraphics events!" and pressed Enter successfully — user saw it on screen)
2. **Hermes research** — Web research completed on Hermes Agent capabilities, top developer workflows (Karpathy pattern, Vaibhav Srinivasan pattern), token optimization strategies, self-improvement mechanisms
3. **Architecture reorg** — Changed from opencode-as-main-agent to Hermes-as-main-agent. Updated SOUL.md, AGENTS.md, config.yaml
4. **Config changes** — Enabled memory (FTS5), compression, cost tracking, Telegram gateway, needed toolsets

### What Was Working
- CoreGraphics ctypes approach for REAL mouse/keyboard events ✅
- cua-driver for AX-based screen interaction (limited to non-Electron apps)
- Hermes TUI + dashboard on port 9119
- Telegram daemon + tg-reply (legacy, still works)

### What Was NOT Working
- cua-driver `type_text` on ChatGPT Atlas (Electron webview ignores AX input)
- cua-driver `click` on Electron web content (AX events ignored by Chromium)
- osascript `tell process "ChatGPT Atlas"` (Electron app doesn't register with System Events)

## TOKEN EFFICIENCY STRATEGY
1. **Compression ON** (threshold 0.4, target 0.15) — auto-compresses when context reaches 40%
2. **Progressive skill loading** — skills load only ~3K tokens at a time
3. **Cheap models for simple work** — Gemini Flash, DeepSeek for cron/research
4. **opencode for code** — zero token cost for Hermes
5. **Cost tracking** — `show_cost: true` shows per-turn spending
6. **Session pruning** — Hermes auto-prunes old sessions
7. **Avoid `code_execution` for heavy work** — delegate to opencode instead
