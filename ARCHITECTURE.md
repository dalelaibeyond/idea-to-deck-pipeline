# Idea-to-Deck Pipeline — Architecture

**Living document — the single source of truth for the current architecture.**
Baseline: **v0.1**, run-ready and validated end-to-end by sessions
`deck_20260919_658` and `deck_20260922_975` (run snapshots:
`_archive/sample_20260919_737/`, `_archive/sample_20260922_975/`).
Design tier: Prompt layer ✅ | Tools layer: local compilers ✅ | Contracts layer: JSON Schema ✅
History & point-in-time reviews: `_archive/` — **local-only, gitignored, never
read during pipeline runs** (index: `_archive/README.md`; agent rules: `AGENTS.md`).
v0.1 features (retro P1–P5, folded into the baseline): renderer two-stage
render + component fidelity, fusion rule, retrieval fallback,
production-context verification, append-only run log — see the
`_archive/sample_*` snapshots and `.workflow_memory/`.

A state-machine-based, multi-agent pipeline that turns raw ideas into visual decks (PPTx or HTML).

## Design Principles

### 7-Pillar scorecard

Absorbed from `top-level-review-02` (originals in git history). Status scored
against the first real run (`deck_20260919_658`), not against design intent.

| # | Pillar | Status | Evidence |
|---|--------|--------|----------|
| 1 | Deterministic backbone, probabilistic leaves | ✅ | Orchestrator is a fixed ordered checklist; phase is derived from artifacts (`index.py status`), never maintained |
| 2 | Context isolation via artifact bus | ◐ by convention | Each agent reads only its upstream artifact; nothing structural enforces it in a single CLI session |
| 3 | Model tiering & token economics | ◐ rendering only | Rendering = local deterministic tools (0 tokens); cross-agent model tiering deferred to v0.5 — target ladder: extraction → light models, narrative/design → reasoning models, render → local code |
| 4 | Schema-first contracts | ✅ | `schemas/*.schema.json` + `tools/validate.py` hard gate after every step |
| 5 | High-leverage HITL & state reversibility | ✅ | 3 Gates, all one-pass in the real run; `index.py reset --from <step>` keeps upstream artifacts |
| 6 | Quality gates & circuit breakers | ◐ | Breaker covers validate failures only; render sanity-check / enrichment loops have no budget yet (retro E5) |
| 7 | Telemetry & evals | ❌ deferred | Run log records gate decisions only; token/latency telemetry is a v0.5 requirement |

Standing principles alongside the scorecard: high cohesion, low coupling;
fault-tolerant messy input; CLI coding agents today → LangGraph / ADK later
with zero migration cost.

### Token economics: file-level generational passing

Absorbed from `top-level-review-01` (original in git history). Downstream
agents never carry conversation history — each reads only its upstream
artifact. Distillation shrinks the payload at every hop; rendering is
deterministic local code (0 model tokens):

```
[workspace/raw/]                     (messy, unbounded)
      │  extract                 ← model tokens, spent once
      ▼
[workspace/outs/step1_facts_sheet.json]     (distilled facts)
      │  story                  ← reads step1 only
      ▼
[workspace/outs/step2_story_outline.json]
      │  design                 ← reads step2 only
      ▼
[workspace/outs/step3_visual_spec.json]
      │  compile                ← local tools, 0 tokens
      ▼
[workspace/outs/final_deck.pptx / .html]
```

---

## 1. System Topology & State Machine

### 1.1 State Graph

```
[User Raw Input]
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│ 0. Orchestrator (Checklist Driver & HITL Dispatcher)        │
└──────┬───────────────────────────────────────────────▲──────┘
       │                                               │
       ▼                                               │ (Status Loop)
┌──────────────────────────────────────────────────┐   │
│ 1. Info Extractor                                │───┤
│    ├─ Fact/Assumption Tagger                     │   │
│    └─ Noise Filter & Web Search Enrichment       │   │
└──────┬───────────────────────────────────────────┘   │
       │ (Artifact: step1_facts_sheet.json)            │
       ▼                                               │
┌──────────────────────────────────────────────────┐   │
│ 2. Storyteller Agent                             │───┤
│    ├─ Narrative Arc Generator (Multi-options)    │   │
│    └─ Slide-by-Slide Core Content Planner        │   │
└──────┬───────────────────────────────────────────┘   │
       │ (Artifact: step2_story_outline.json)          │
       ▼                                               │
┌──────────────────────────────────────────────────┐   │
│ 3. Visual Designer Agent                         │───┤
│    ├─ Design Archetype Matcher                   │   │
│    └─ Slide Layout Component Mapper              │   │
└──────┬───────────────────────────────────────────┘   │
       │ (Artifact: step3_visual_spec.json)            │
       ▼                                               │
┌──────────────────────────────────────────────────┐   │
│ 4. Compiler & Renderer                           │───┤
│    ├─ Engine A: Marp / Reveal.js (HTML/CSS)      │   │
│    └─ Engine B: python-pptx (Native PPTx)        │   │
└──────┬───────────────────────────────────────────┘   │
       │ (Artifact: final_deck.html / final_deck.pptx) │
       ▼                                               │
┌──────────────────────────────────────────────────┐   │
│ 5. Meta-Learner (on demand)                      │───┘
│    └─ Reflection & Prompt / Library Optimization │
└──────────────────────────────────────────────────┘
```

### 1.2 Global State Schema

Agents exchange data via a standard JSON bus. No natural-language drift.

**Authority rule:** the individual step files in `workspace/outs/` are the
single source of truth. The global state below is a logical view (aggregate
projection), not a physical file to maintain. The physical
`workspace/outs/00_session_state.json` carries only session identity (`session_id`,
`started_at`, `target_format`); `phase` is always derived from artifact
existence (`index.py status`), never stored.

```json
{
  "session_id": "deck_20261012_001",
  "phase": "EXTRACT | STORY | DESIGN | RENDER | OPTIMIZE",
  "meta": {
    "target_audience": "Investors / Internal Executives / Tech Team",
    "target_format": "pptx"
  },
  "raw_context": "user's original messy input ...",
  "facts_sheet": {
    "facts": [{ "id": "F1", "claim": "...", "source": "...", "verified": true }],
    "assumptions": [{ "id": "A1", "claim": "...", "confidence": "Medium" }],
    "goals": ["raise 20M", "highlight tech moat"]
  },
  "story_outline": {
    "framework": "SCQA",
    "slides": [
      {
        "slide_no": 1,
        "type": "COVER",
        "title": "...",
        "core_message": "...",
        "evidence_ids": ["F1"]
      }
    ]
  },
  "visual_spec": {
    "theme": "Modern_Tech_Dark",
    "color_palette": { "primary": "#0A192F", "accent": "#64FFDA" },
    "slides_ui": []
  },
  "build_artifacts": {
    "output_file": "./workspace/outs/final_deck.html",
    "compilation_status": "SUCCESS"
  }
}
```

### 1.3 Per-Artifact Contracts

Schema-as-code, enforced by `tools/validate.py` as a hard gate after every
step. The schema files are the authority; this table is a pointer map.

| Artifact | Schema | Essence |
|---|---|---|
| `workspace/outs/step1_facts_sheet.json` | `schemas/step1_facts_sheet.schema.json` | facts (id / claim / source / verified), assumptions (confidence), goals, status |
| `workspace/outs/step2_story_outline.json` | `schemas/step2_story_outline.schema.json` | framework; per slide: slide_no / type / title / core_message / evidence_ids; status |
| `workspace/outs/step3_visual_spec.json` | `schemas/step3_visual_spec.schema.json` | theme, color_palette; per slide: slides_ui (slide_no / component / style); status |
| `workspace/outs/00_session_state.json` | `schemas/session_state.schema.json` | session identity only (session_id / started_at / target_format) — phase never stored |

`status` is the per-artifact lifecycle flag (`ok` | `rework`) used by the
retry path; evidence IDs in step2 must resolve to step1 rows (hallucination
guard — the traceability spine).

---

## 2. Workspace Structure

```
.
├── workspace/                     # Single-session runtime root: raw input → finalized output
│   ├── raw/                        #   Input pool: any messy files (txt, md, pdf, docx, screenshots)
│   │   └── (user drops fragmented material here anytime)
│   │
│   └── outs/                       #   All agent artifacts + final deliverables
│       ├── step1_facts_sheet.json
│       ├── step2_story_outline.json
│       ├── step3_visual_spec.json
│       ├── final_deck.html
│       └── final_deck.pptx
│
├── schemas/                       # JSON Schema data contracts (one per artifact)
│   ├── step1_facts_sheet.schema.json
│   ├── step2_story_outline.schema.json
│   ├── step3_visual_spec.schema.json
│   └── session_state.schema.json
│
├── design-library/                # Reusable best-practice templates & style library
│   ├── archetypes/                # Style archetypes (YAML + CSS/masters)
│   │   ├── apple_keynote.yaml
│   │   ├── mckinsey_consulting.yaml
│   │   ├── high_density_tech.yaml
│   │   ├── exec_120s_hook.yaml
│   │   └── mckinsey_exec_hybrid.yaml   # fusion archetype (derived in run deck_20260919_658)
│   └── components/                # Reusable UI components (compare table, timeline, metric cards)
│
├── agents/                        # Role prompt definitions
│   ├── orchestrator/
│   │   └── PROMPT.md
│   ├── 01_info_extractor/
│   │   ├── PROMPT.md
│   │   └── sub_tagger.md
│   ├── 02_storyteller/
│   │   ├── PROMPT.md
│   │   └── sub_frameworks.md
│   ├── 03_visual_designer/
│   │   ├── PROMPT.md
│   │   └── sub_templates.md
│   ├── 04_renderer/
│   │   └── PROMPT.md
│   └── 05_meta_learner/
│       └── PROMPT.md
│
├── tools/                         # Local deterministic compilers & validators
│   ├── pptx_compiler.py           # python-pptx native builder
│   └── validate.py                # JSON Schema contract gate (run after every step)
│
├── .workflow_memory/              # Learning agent's persistent memory
│   ├── best_practices.md
│   └── failure_cases.md
│
├── clean.sh                       # Fresh run: archives previous run to _archive/sample_*/
└── index.py                       # CLI entry: status / clean / reset --from
```

---

## 3. Agent Roles

The `agents/*/PROMPT.md` files are the single source of truth for each role's
behavior. This section holds pointers and one-line contracts, **not copies** —
embedded copies drift from the real prompts (that drift was found and removed
during an earlier review cycle).

| Agent | Role | Input (only) | Output | HITL |
|---|---|---|---|---|
| 0 Orchestrator | Fixed ordered checklist; never routes by judgment; derives progress from artifacts | `index.py status` | run_log lines | dispatches all gates |
| 1 Info Extractor | Ingest `workspace/raw/`, tag facts/assumptions, surface gaps on one sheet | `workspace/raw/` | `step1_facts_sheet.json` | **Gate 1**: single facts-confirmation sheet |
| 2 Storyteller | 2–3 narrative frameworks + recommendation | `step1_facts_sheet.json` | `step2_story_outline.json` | **Gate 2**: framework selection |
| 3 Visual Designer | Archetype matching (+ fusion option when requirements span two), slide→component mapping | `step2_story_outline.json`, `design-library/` | `step3_visual_spec.json` | **Gate 3**: archetype selection |
| 4 Renderer | Declarative translator: spec → deck; pptx = two-stage (structural gate → html2pptx fidelity pass), 4-item post-render check incl. component fidelity | `step3_visual_spec.json`, `step2_story_outline.json`, `design-library/` | `final_deck.pptx` / `.html` | — |
| 5 Meta-Learner | On-demand retro: memory + design-library enrichment | `workspace/outs/` + run evidence | `.workflow_memory/` updates, retro docs | user-triggered only |

Sub-agent extensions: `01/sub_tagger.md` (fact-check & cross-validation),
`02/sub_frameworks.md` (industry narrative structures), `03/sub_templates.md`
(layout component library).

Failure path (deterministic circuit breaker, owned by the Orchestrator):
`validate.py` exit 1 → same-turn fix by the writing agent (context still warm)
→ retry #1 → second consecutive failure = STOP, log, ask the user. Never more
than one retry per step.

---

## 4. Design Archetype Library

Preset industrial-grade style archetypes. The Designer Agent matches them to
the scenario and may propose a principled fusion when requirements span two.

| Archetype                  | Visual Identity                                            | Best For                       | Layout Preference                          |
| :------------------------- | :--------------------------------------------------------- | :----------------------------- | :----------------------------------------- |
| **Apple Keynote**          | Big typography, whitespace, cinematic dark/light, one focus | Product launches, vision talks | Single image + one-line quote, full-bleed  |
| **McKinsey Consulting**    | Pyramid structure, action titles, chart-driven, cited data  | Board reports, strategy reviews | Diagram + data split, 3-part reasoning     |
| **High-Density Tech**      | Dense info, bento grid, multi-level comparison              | Architecture reviews, deep dives | Card grids, comparison tables, flow charts |
| **Executive 120s Hook**    | Conclusion-first, pain/ROI emphasis, strong visuals         | Elevator pitch, fast decisions  | Huge metric numbers, pain-vs-gain contrast |
| **McKinsey × Exec Hybrid** | McKinsey skeleton + selective 120s accents, derivation rules in YAML | Mixed executive briefings | Per `mckinsey_exec_hybrid.yaml` |

---

## 5. Compile/Render Toolchain

1. **HTML route: Marp (declarative)**
   - Best for CLI agents: fast, beautiful, CSS-customizable, responsive.
   - Agent 4 (LLM leaf node) translates `slides_ui` + design-library presets into `workspace/outs/deck.md`, then compiles with one local command — `npx @marp-team/marp-cli workspace/outs/deck.md -o workspace/outs/final_deck.html` (0 tokens; the old JS middle layer was deleted; a nonzero exit code is a hard failure).
2. **PPTx native route: two-stage render (renderer fidelity, closes retro E4 / P1)**
   - Compatible with office suites; editable afterward.
   - Stage 1 — structural gate: `tools/pptx_compiler.py` reads the three
     artifacts from `workspace/outs/` and applies theme/palette (failures are loud,
     never silent); nonzero exit = hard failure.
   - Stage 2 — fidelity pass (the deliverable): each slide's `slides_ui`
     component becomes one 720x405pt HTML page (palette strictly from
     design-library variables; CJK font stack Arial + PingFang SC /
     Microsoft YaHei; tables as div grids), compiled via the powerpoint
     skill's `html2pptx.js` to overwrite `workspace/outs/final_deck.pptx`.
   - Post-render check is four items: page count / no empty pages / evidence
     IDs resolve / **component fidelity**. Visual verification runs in the
     production render context (slide-HTML screenshots), never a lossy
     LibreOffice proxy on CJK decks (retro E5).

---

## 6. CLI → Production Evolution Path

| Phase   | Runtime                                             | Orchestration                        | State Storage              | Use Case                                  |
| :------ | :-------------------------------------------------- | :----------------------------------- | :------------------------- | :---------------------------------------- |
| **v0.1** | OpenCode CLI / Codex CLI / Antigravity             | FS (JSON) + shell scripts + markdown | Local files (`workspace/outs/`)   | Solo fast builds, CLI automation, prompt tuning |
| **v0.5** | Python LangGraph / LlamaIndex Workflows            | Native async StateGraph topology     | MemorySaver / Redis        | Web UI, team sharing, multi-session       |
| **v1.0** | Google GenAI ADK / Semantic Kernel / AutoGen       | Declarative DAG, agent workers, vector store | Postgres + S3/OSS   | Enterprise SaaS, multimodal, private depl |

### 6.1 Maturity ladder

| Level | Pattern | Where we are |
|---|---|---|
| 1 — Prompt scripting | One mega-prompt, zero fault tolerance | past |
| 2 — Conversational multi-agent | Agents chat in one context; token burn, hallucination cascade | past (rejected at design time) |
| 3 — Stateful artifact graph | Deterministic DAG + artifact isolation + typed contracts + HITL gates | **current (v0.1)** |
| 4 — Autonomous adaptive ADK | Distributed actors, semantic caching, prompt A/B, full tracing + CI evals | v0.5+ target |

### 6.2 Migration sketch for v0.5 — *unvalidated design note*

- Each `agents/*/PROMPT.md` → a graph node function (e.g. LangGraph async node over a typed state)
- HITL Gates → `interrupt()` breakpoints surfaced by a web UI
- `.workflow_memory/` → persistent store + eval set (e.g. Postgres + LangSmith)
- `workspace/outs/` artifacts → graph state channels; schema validation unchanged

---

## 7. Daily Workflow CLI

```bash
# 1. Start a new project (previous run archived to _archive/sample_*/, nothing deleted)
$ python3 index.py clean            # or ./clean.sh

# 2. Drop material into workspace/raw/
$ cp ~/Desktop/notes.txt ./workspace/raw/
$ cp ~/Downloads/product_spec.md ./workspace/raw/

# 3. Run the pipeline
$ ai-agent "Please start the Orchestrator and build a deck from workspace/raw/"

# Sample agent interaction:
# [Agent 1] "Read 2 files. Audience and goal are clear, but competitor data is missing. Do you have data, or should I search the web?"
# [User]    "Please search."
# [Agent 2] "Generated 2 narratives (1. SCQA 2. Pain-Point Breakout). I recommend #2. Which one?"
# [Agent 3] "For an executive audience, I recommend Executive 120s Hook or McKinsey. Which do you prefer?"
# [Agent 4] "Done! All artifacts are in workspace/outs/ (final_deck.html & final_deck.pptx)"
```
