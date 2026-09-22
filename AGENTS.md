# AGENTS.md — Ground Rules for Coding Agents

Idea-to-Deck workflow repo. You are either (a) running the deck pipeline —
`agents/orchestrator/PROMPT.md` is the single entry point — or (b) evolving
the workflow itself — `README.md` (usage) and `ARCHITECTURE.md` (living
design) are the authoritative docs.

## Hard Rules

1. **`_archive/` — do not read it, do not git it.**
   - It is frozen local history: point-in-time reviews plus `sample_*/` run
     snapshots auto-archived by `clean`. It is NOT workflow input — reading
     it wastes context and leaks stale conclusions into runs. The only
     exception is an explicit user instruction pointing at one specific
     file (e.g. "implement this retro").
   - It is entirely out of version control (see .gitignore). Never
     `git add` or push anything under `_archive/`. The versioned records
     are git history (code/docs) and `.workflow_memory/` (lessons).
2. `workspace/outs/` is derived runtime state: progress comes from
   `python3 index.py status`, never maintained by hand. Only
   `workspace/outs/00_run_log.md` is versioned; artifacts are local.
3. `workspace/raw/` is per-run local material — never commit it.
4. Fresh session = `./clean.sh` (archives the previous run into
   `_archive/sample_<session>/`, nothing deleted). Selective redo =
   `python3 index.py reset --from <step>`.
5. Contract changes go through `schemas/` and must pass
   `python3 tools/validate.py --strict` before commit.
