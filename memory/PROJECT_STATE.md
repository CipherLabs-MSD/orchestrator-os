# Project State

- **as_of:** branch `oos-0001/foundation`, after the domain-specialization addendum commit (see `git log`). `main` has no commits yet.
- **Date:** 2026-10-01
- **Current milestone:** M0 Foundation
- **Health:** design only. No runtime code exists, by intent.
- **Active profile for OOS itself:** `software-development-orchestrator` (kernel + `domains/software-development`).

## Active work

| Task | Status | Evidence |
|---|---|---|
| OOS-0001 (incl. addendum: domain-specialized orchestration, ADR-0006) | verifying: awaiting Billy's review (G-REVIEW, G-HUMAN) | `tools/validate.py` 13/13 · unittest 31 OK · `tools/mutation_check.py` 20/20 |

## Next ready

- OOS-0002: runtime, language and execution-mode decision (do not start until OOS-0001 is accepted).

## Blockers

- OQ-001 (where the user-context instance lives) blocks OOS-0012.
- OQ-003 and OQ-005 must be answered before OOS-0010.
- OQ-004 must be answered before OOS-0013.
- OQ-007 (second operational domain) must be answered before OOS-0020. Not needed until after OOS-0016.

## Pointers

- Backlog: [`project/BACKLOG.md`](../project/BACKLOG.md)
- Architecture and the kernel/domain principle: [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md), [`docs/DOMAIN_PACKAGES.md`](../docs/DOMAIN_PACKAGES.md)
- Decisions: [`DECISIONS/`](DECISIONS/) and [`docs/adr/`](../docs/adr/)
