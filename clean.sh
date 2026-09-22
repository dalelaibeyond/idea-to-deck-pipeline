#!/usr/bin/env bash
# Start a fresh run: archive the previous one (workspace/raw/ + workspace/outs/) into
# _archive/sample_<session>/ — nothing is deleted. workspace/outs/00_run_log.md
# stays in place (a copy rides along with the archive).
# Thin wrapper: all logic lives in index.py so shell and CLI stay in sync.
# Extra args pass through, e.g. ./clean.sh --format html

set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${PROJECT_DIR}"
python3 index.py clean "$@"
