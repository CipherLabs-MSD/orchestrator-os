# Project State

- **as_of:** branch `oos-0002/runtime-spike` (from `main` @ `7e01119`). See `git log`.
- **Date:** 2026-10-01
- **Current milestone:** M1 Walking skeleton (M0's OOS-0001 is DONE and merged to `main`)
- **Health:** design plus a disposable spike. No production runtime code exists, by intent.
- **Owner policy in force:** [ADR-0007](../docs/adr/ADR-0007-initial-owner-policy.md)

## Active work

| Task | Status | Evidence |
|---|---|---|
| OOS-0002 | **verifying** (awaiting Billy's review of the PR) | ADR-0008. `tests/test_spike_oos0002.py`. `spikes/oos-0002/results/win32-2026-10-01.json`. |

## Next ready (after OOS-0002 is accepted and merged)

- **OOS-0003**: record store and schema validation library, in Python ≥ 3.12 (ADR-0008).

## Open owner items

- Review and merge the OOS-0002 PR (Billy holds merge authority).
- Install Python 3.12+ on the development machine (ADR-0008). The current machine has 3.10.6.
- OQ-007 (second operational domain): deferred.

## Pointers

- Backlog: [`project/BACKLOG.md`](../project/BACKLOG.md)
- Runtime design: [`docs/EXECUTION_RUNTIME.md`](../docs/EXECUTION_RUNTIME.md)
- Decisions: [`DECISIONS/`](DECISIONS/) and [`docs/adr/`](../docs/adr/)
