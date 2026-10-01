# Project State

- **as_of:** branch `oos-0001/foundation`, first commit (see `git log`). `main` has no commits yet.
- **Date:** 2026-10-01
- **Current milestone:** M0 Foundation
- **Health:** design only. No runtime code exists, by intent.

## Active work

| Task | Status | Evidence |
|---|---|---|
| OOS-0001 | verifying: awaiting Billy's review (G-REVIEW, G-HUMAN) | `python tools/validate.py` and `python -m unittest discover tests` pass on the branch |

## Next ready

- OOS-0002: runtime, language and execution-mode decision (do not start until OOS-0001 is accepted).

## Blockers

- OQ-001 (where the user-context instance lives) blocks OOS-0012.
- OQ-003 and OQ-005 must be answered before OOS-0010.
- OQ-004 must be answered before OOS-0013.

## Pointers

- Backlog: [`project/BACKLOG.md`](../project/BACKLOG.md)
- Architecture: [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md)
- Decisions: [`DECISIONS/`](DECISIONS/) and [`docs/adr/`](../docs/adr/)
