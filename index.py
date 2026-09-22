#!/usr/bin/env python3
"""CLI entry point for the Idea-to-Deck pipeline.

Pipeline progress is DERIVED from artifact existence in workspace/outs/ — nothing is
maintained by hand. Run the Orchestrator flow manually in your CLI agent:
    "Please act as the Orchestrator, follow
     agents/orchestrator/PROMPT.md, and process this deck from workspace/raw/."

Usage:
    python3 index.py status                      # derived progress report
    python3 index.py clean [--format pptx|html]  # fresh run (archives the
                                                 # previous run into
                                                 # _archive/sample_*, never
                                                 # deletes)
    python3 index.py reset --from step3          # selective time-travel:
                                                 # keep upstream, drop this
                                                 # step and everything after
"""

import argparse
import json
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE / "workspace" / "outs"
RAW_INFO_DIR = BASE / "workspace" / "raw"
ARCHIVE_DIR = BASE / "_archive"
RUN_LOG_NAME = "00_run_log.md"

# Generated artifacts in pipeline order. 00_run_log.md is a durable log:
# clean archives a COPY into the sample folder but keeps the original in
# place; reset leaves it untouched.
STEP_ARTIFACTS = {
    "step1": ["step1_facts_sheet.json"],
    "step2": ["step2_story_outline.json"],
    "step3": ["step3_visual_spec.json"],
    "render": ["deck.md", "final_deck.html", "final_deck.pptx"],
}


def _load_session_state():
    path = OUTPUTS_DIR / "00_session_state.json"
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _unlink_all(names):
    for name in names:
        p = OUTPUTS_DIR / name
        if p.exists():
            p.unlink()


def _report_status():
    """Print status derived purely from artifact existence (H1: derive, don't maintain)."""
    ss = _load_session_state()
    if ss:
        print(f"[session] id: {ss.get('session_id')}  "
              f"started: {ss.get('started_at')}  "
              f"target_format: {ss.get('target_format', 'unspecified')}")
    else:
        print("[session] no session state (run `python3 index.py clean` to start)")

    print("[session] progress below is derived from files in workspace/outs/ — no phase is maintained.")

    for step, names in STEP_ARTIFACTS.items():
        if step == "render":
            # html/pptx are alternative render outputs; either one counts.
            if any((OUTPUTS_DIR / n).exists() for n in names if n.startswith("final_deck")):
                print("[ok]   final_deck.pptx / final_deck.html (either)")
            else:
                print("[todo] final_deck.pptx / final_deck.html (either)")
        else:
            for name in names:
                path = OUTPUTS_DIR / name
                if path.exists():
                    print(f"[ok]   {name}")
                else:
                    print(f"[todo] {name}")

    # Derived phase: furthest step whose artifacts exist.
    phase = "EXTRACT"
    for step, next_phase in [("step1", "STORY"), ("step2", "DESIGN"), ("step3", "RENDER")]:
        if all((OUTPUTS_DIR / n).exists() for n in STEP_ARTIFACTS[step]):
            phase = next_phase
        else:
            break
    if any((OUTPUTS_DIR / n).exists() for n in STEP_ARTIFACTS["render"] if n.startswith("final_deck")):
        phase = "DONE"
    print(f"[derived] phase: {phase}")

    raw_dir = BASE / "workspace" / "raw"
    if raw_dir.exists():
        count = len([f for f in raw_dir.iterdir() if f.is_file()])
        print(f"[info] workspace/raw/ has {count} file(s)")


def status():
    _report_status()


def _archive_previous_run():
    """Move the previous run into _archive/sample_<session>/ — nothing is deleted.

    workspace/raw/ contents and every workspace/outs/ entry except the durable run log
    become a self-contained snapshot (a COPY of the run log rides along; the
    original stays in workspace/outs/). Folder name: sample_<session id
    without the deck_ prefix>, timestamp fallback when no session state exists, _2/_3
    suffix on collision. Returns the archive dir, or None when there was
    nothing to archive (no empty sample folders on a fresh repo).
    """
    # .gitkeep is dir infrastructure, not run content — leave it in place.
    raw_entries = ([p for p in RAW_INFO_DIR.iterdir() if p.name != ".gitkeep"]
                   if RAW_INFO_DIR.exists() else [])
    out_entries = ([p for p in OUTPUTS_DIR.iterdir() if p.name != RUN_LOG_NAME]
                   if OUTPUTS_DIR.exists() else [])
    # A bare session state (pipeline never ran) with no raw material is not
    # worth an archive folder — skip instead of littering _archive/.
    meaningful = raw_entries or [p for p in out_entries
                                 if p.name != "00_session_state.json"]
    if not meaningful:
        return None

    ss = _load_session_state() or {}
    sid = str(ss.get("session_id", "")).removeprefix("deck_")
    stamp = sid or datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"sample_{stamp}"
    archive = ARCHIVE_DIR / base_name
    n = 1
    while archive.exists():
        n += 1
        archive = ARCHIVE_DIR / f"{base_name}_{n}"

    (archive / "raw-info").mkdir(parents=True)
    (archive / "outputs").mkdir(parents=True)
    for p in out_entries:
        p.rename(archive / "outputs" / p.name)
    for p in raw_entries:
        p.rename(archive / "raw-info" / p.name)
    log = OUTPUTS_DIR / RUN_LOG_NAME
    if log.exists():
        shutil.copy2(log, archive / "outputs" / RUN_LOG_NAME)
    return archive


def clean(target_format: str = "pptx"):
    """Archive the previous run into _archive/sample_* (nothing deleted), write a fresh session."""
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_INFO_DIR.mkdir(parents=True, exist_ok=True)
    archive = _archive_previous_run()
    if archive:
        print(f"[archive] previous run moved to {archive.relative_to(BASE)} "
              f"(workspace/raw/ + workspace/outs/; run log copied, original kept)")

    state = {
        "session_id": f"deck_{datetime.now(timezone.utc):%Y%m%d}_{random.randint(0, 999):03d}",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "target_format": target_format,
    }
    with open(OUTPUTS_DIR / "00_session_state.json", "w") as f:
        json.dump(state, f, indent=2)
    print(f"Fresh session {state['session_id']}, target_format={target_format}. "
          f"Nothing was deleted.")
    print("Drop material into workspace/raw/ and start the pipeline.")


def reset_from(step: str):
    """Selective reset: delete this step's artifacts and everything downstream.

    Upstream artifacts survive, so e.g. `reset --from step3` lets the user
    re-pick a template without paying for extraction again.
    """
    keys = list(STEP_ARTIFACTS)
    if step not in keys:
        print(f"[error] unknown step '{step}' (choose from {keys})")
        return
    for key in keys[keys.index(step):]:
        _unlink_all(STEP_ARTIFACTS[key])
    print(f"Reset from {step}: downstream artifacts removed, upstream kept.")
    print("Re-run the Orchestrator; it will resume at the first missing artifact.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Idea-to-Deck pipeline CLI")
    sub = p.add_subparsers(dest="action", required=True)
    sub.add_parser("status", help="show derived pipeline progress")
    c = sub.add_parser("clean", help="fresh run (archives previous run into _archive/sample_*)")
    c.add_argument("--format", choices=["pptx", "html"], default="pptx",
                   help="target_format consumed by Agent 4 (default: pptx)")
    r = sub.add_parser("reset", help="selective reset; keeps upstream artifacts")
    r.add_argument("--from", dest="from_step", required=True,
                   choices=list(STEP_ARTIFACTS), metavar="STEP",
                   help="step1 | step2 | step3 | render")
    args = p.parse_args()
    if args.action == "status":
        status()
    elif args.action == "clean":
        clean(target_format=args.format)
    else:
        reset_from(args.from_step)
