# Best Practices

## Workflow
- Always enforce the JSON data contract between agents.
- Ask at most 2 clarifying questions per turn.
- Present every HITL gate as 2-3 curated options + an explicit recommendation
  with reasoning sourced from design-library / best practice — never open-ended
  questions. Humans pick from a menu; the agent does the legwork.
  (Validated in deck_20260919_658: user cited this as the run's best trait.)
- When user requirements span two archetypes (e.g., McKinsey authority +
  120s punch), offer a principled fusion option: skeleton from archetype A,
  selective accents from B, with explicit rules for which elements come from
  where. See `design-library/archetypes/mckinsey_exec_hybrid.yaml`.
- Record negative enrichment findings in the facts sheet ("no public financials
  for X, checked YYYY-MM-DD via search + official site") so later runs never
  re-search the same dead end.
- Enrichment fallback chain: web search → direct fetch of official pages.
  Search quotas can exhaust mid-run; official-site fetching keeps Gate 1 moving.
- Confidence tags on assumptions drive editorial exclusion: Low-confidence,
  derogatory, or unverifiable claims stay out of the deck body (case A5:
  "management too old" dropped from slides).

## Design
- Match the archetype to the audience, not to personal taste.
- ics_kys_style (Latin-only, sovereign metric-dominant, navy/gold) lives in
  `design-library/` (archetype + components + 13-slide exemplar) and is staged
  for install at `_archive/SKILLs/ics_kys_style/` — templates are reference,
  adapt per brief, narrative wins.
- Every final deck must pass overflow/collision validation.
- CJK decks via html2pptx: font stack Arial + 'PingFang SC' / 'Microsoft
  YaHei' fallback (web-safe primary); html2pptx does NOT support `<table>` —
  build comparison tables as div grids with per-cell background fills.

## Rendering
- v0.2 `tools/pptx_compiler.py` renders title+bullets only and ignores the
  step3 `slides_ui` component mapping. For component fidelity use the
  html2pptx path: one HTML per slide at 720x405pt, palette strictly from
  design-library variables, build via the powerpoint skill scripts.
- Verify in the production render context, not a lossy proxy: LibreOffice-based
  thumbnail grids produce false "missing text" alarms on CJK decks when the
  backend lacks Chinese fonts. Prefer Chrome screenshots of the slide HTML.

## Verification
- Keep evidence-ID traceability from outline → facts sheet; it makes the
  final sanity check mechanical (page count / no empty slides / no
  unresolved evidence IDs).