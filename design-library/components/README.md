# Component Library

Reusable slide UI components, referenced by `step3_visual_spec.json`.
Each component is a YAML/JSON template plus an optional HTML reference
implementation (720x405pt, palette strictly from the chosen archetype).

## Available Components

Each name below has a ready HTML reference template in this directory —
**reference only**: the renderer adapts weights/sizes/page-mix per brief,
templates are a starting grammar, not constraints (see `ics_kys_style`
archetype `adaptation_rule`).

- `cover_full` — full-bleed deep-navy cover / section divider
- `metric_card` — white top-bar cards with huge metric numbers
- `three_column_bento` — three left-border cards (pillars / pains)
- `split_compare` — before/after duel panels with metric band
- `diagram_plus_data` — layered stack / flow + side panel (3 variants)
- `timeline` — ask-cards + stage ladder
- `comparison_table` — DIV-grid table (html2pptx has no `<table>` support)

## Style Kits

| Archetype | Best for | Kit |
|---|---|---|
| `ics_kys_style` | Sovereign/exec-flagship strategy, metric-heavy, English only | `./components/*.html` + `../examples/ics_kys_13slide/` full 13-slide exemplar |
| `mckinsey_exec_hybrid` | CJK-capable exec strategy pitch | — |

## Rendering

Fidelity pass: one HTML slide per 720x405pt page from the component
template + archetype palette, compiled with the `powerpoint` skill's
`html2pptx.js` (driver: `examples/ics_kys_13slide/build_deck.js`).