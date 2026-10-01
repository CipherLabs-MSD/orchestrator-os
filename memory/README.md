# memory/: project memory for Orchestrator OS itself

This directory is the **project truth → memory** layer for the OOS project. OOS dogfoods
its own [memory model](../docs/MEMORY_MODEL.md). Managed projects get the same structure
in their own `ProjectStore` (repository-backed projects: `.oos/memory/`, OQ-002). Domain
packages may add record types on top.

| File | Purpose |
|---|---|
| [PROJECT_STATE.md](PROJECT_STATE.md) | Current milestone, active work, health (`as_of` bound to a commit) |
| [DECISIONS/](DECISIONS/) | D2 decision log, plus an index of ADRs (D3/D4 decisions live in `docs/adr/`) |
| [LEARNINGS.md](LEARNINGS.md) | Validated, reusable insights |
| [FAILED_APPROACHES.md](FAILED_APPROACHES.md) | Dead ends, with retry conditions |
| [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) | Unresolved questions, tagged by who must answer |
| [HANDOFF.md](HANDOFF.md) | What the next session needs in order to resume |

Rules: point, don't copy. Supersede, don't delete. Every entry is attributable.
