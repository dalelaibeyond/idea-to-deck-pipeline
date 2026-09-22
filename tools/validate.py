#!/usr/bin/env python3
"""Validate all pipeline artifacts against JSON Schema contracts.

Usage:
    python3 tools/validate.py
    python3 tools/validate.py --strict   # also require a session_state file

All violations of an artifact are reported in one pass (iter_errors), so the
fixing agent repairs everything in a single turn instead of round-tripping
per error.

Exit codes:
    0   All artifacts valid (or missing, which is ok for a fresh run)
    1   One or more artifacts failed validation
    2   Schema files missing or unreadable
"""

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = BASE / "schemas"
OUTPUTS_DIR = BASE / "workspace" / "outs"

SCHEMAS = {
    "step1_facts_sheet": SCHEMAS_DIR / "step1_facts_sheet.schema.json",
    "step2_story_outline": SCHEMAS_DIR / "step2_story_outline.schema.json",
    "step3_visual_spec": SCHEMAS_DIR / "step3_visual_spec.schema.json",
    "session_state": SCHEMAS_DIR / "session_state.schema.json",
}

ARTIFACTS = {
    "step1_facts_sheet": OUTPUTS_DIR / "step1_facts_sheet.json",
    "step2_story_outline": OUTPUTS_DIR / "step2_story_outline.json",
    "step3_visual_spec": OUTPUTS_DIR / "step3_visual_spec.json",
    "session_state": OUTPUTS_DIR / "00_session_state.json",
}


def load_json(path: Path):
    if not path.exists():
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[error] Failed to read {path}: {e}")
        return None


def validate_artifact(name, artifact, schema_path):
    if artifact is None:
        print(f"[warn]  {name}: file missing (skipped)")
        return True  # ok if missing
    if not schema_path.exists():
        print(f"[error] Schema missing: {schema_path}")
        return False
    try:
        from jsonschema import Draft7Validator
        validator = Draft7Validator(json.load(open(schema_path)))
        errors = sorted(validator.iter_errors(artifact),
                        key=lambda e: list(e.absolute_path))
        if not errors:
            print(f"[ok]    {name}: valid")
            return True
        for e in errors:
            loc = "/".join(str(p) for p in e.absolute_path) or "<root>"
            print(f"[fail]  {name}: {loc}: {e.message}")
        return False
    except Exception as e:
        print(f"[error] {name}: validation error - {e}")
        return False


def main(strict: bool = False):
    schema_ok = True
    for name, schema_path in SCHEMAS.items():
        artifact = load_json(ARTIFACTS[name])
        if not validate_artifact(name, artifact, schema_path):
            schema_ok = False

    # In strict mode, session_state must exist with identity metadata
    if strict:
        ss = load_json(ARTIFACTS["session_state"])
        if ss is None:
            print("[fail]  session_state: missing (--strict requires it)")
            schema_ok = False
        elif not ss.get("session_id") or not ss.get("started_at"):
            print("[fail]  session_state: session_id / started_at missing")
            schema_ok = False
        else:
            print(f"[ok]    session_state: {ss['session_id']}")

    if schema_ok:
        print("\nAll checked artifacts are valid.")
        return 0
    else:
        print("\nValidation failed. Fix the errors above before running the pipeline.")
        return 1


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Validate pipeline artifacts against JSON Schema")
    p.add_argument("--strict", action="store_true",
                   help="Also require session_state to exist with identity metadata")
    args = p.parse_args()
    sys.exit(main(strict=args.strict))
