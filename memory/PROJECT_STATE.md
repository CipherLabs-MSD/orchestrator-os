# Project State

- **as_of:** branch `oos-0003/record-store` (from `main` @ `109a3dc`, which includes OOS-0002 via PR #1). See `git log`.
- **Date:** 2026-10-02
- **Current milestone:** M1 Walking skeleton
- **Runtime:** Python >= 3.12 (ADR-0008). The project `.venv` uses Python 3.14.7. The system interpreter is unchanged.

## Active work

| Task | Status | Evidence |
|---|---|---|
| OOS-0002 | **DONE** (merged by Billy, PR #1) | ADR-0008 |
| OOS-0003 | **verifying** (awaiting Billy's review of the PR) | ADR-0009, DEC-0006, store/log tests, sabotage check 5/6 (fsync is an untestable, documented gap). G-STATIC only partly met (OQ-008). |

## Next ready (after OOS-0003 is merged)

- Wave 3 of the backlog: **OOS-0004** (task graph engine), **OOS-0007** (backend contract + first adapter),
  **OOS-0018** (domain loader). All depend only on OOS-0003 (and OOS-0002). OOS-0012 also depends on OOS-0003,
  but needs Billy for the private context store.

## Open items

- Billy: review and merge the OOS-0003 PR.
- OQ-008: choose a static checker (orchestrator, D2).
- OQ-007: second operational domain (deferred by Billy).

## Pointers

- Backlog: [`project/BACKLOG.md`](../project/BACKLOG.md)
- Record store: [`docs/RECORD_STORE.md`](../docs/RECORD_STORE.md) · Runtime: [`docs/EXECUTION_RUNTIME.md`](../docs/EXECUTION_RUNTIME.md)
