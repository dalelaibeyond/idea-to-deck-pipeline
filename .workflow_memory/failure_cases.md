# Failure Cases

## How to log
Add one entry per failed run: root cause, affected agent, fix.

## deck_20260919_658 — renderer fidelity gap (quality failure; validation still passed)
- Root cause: `tools/pptx_compiler.py` (v0.2) renders title+bullets with a
  flat primary-color background and ignores `step3_visual_spec.slides_ui`
  (component mapping, per-slide accents) → compiled deck does not honor the
  declarative spec and is barely readable (dark text on navy).
- Affected agent: 04_renderer (tool limitation, not prompt violation).
- Fix applied this run: kept the hard gate (compiler exit 0), then rebuilt
  `final_deck.pptx` via html2pptx honoring slides_ui; sanity checks all green.
- Permanent fix proposal: make the compiler component-aware, or bless the
  html2pptx path as the official pptx backend in `04_renderer/PROMPT.md`.

## deck_20260919_658 — verification false alarm on CJK
- Root cause: `thumbnail.py` converts via LibreOffice without CJK fonts →
  Chinese text rendered as missing/tofu in the thumbnail grid; two vision
  passes gave contradictory "defect" reports and wasted analysis cycles.
- Affected agent: 04_renderer (sanity-check step).
- Fix applied: verified via Chrome screenshots of the slide HTML (same render
  context as production); all key layouts clean.
- Proposal: check CJK font availability before trusting LibreOffice
  thumbnails; default to screenshot-from-source verification for CJK decks.