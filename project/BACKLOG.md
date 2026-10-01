# Backlog

Stable IDs `OOS-NNNN`. IDs are never reused. Cancelled items stay with `cancelled` status.
Machine view: [`backlog.json`](backlog.json). The two must agree on ID, milestone, status and
dependencies, and `tools/validate.py` checks this. Questions: [`memory/OPEN_QUESTIONS.md`](../memory/OPEN_QUESTIONS.md).

## Index

| ID | Title | M | Status | Depends on | Blocked by (questions) | Expected level |
|---|---|---|---|---|---|---|
| OOS-0001 | Foundation: architecture, models, policies, schemas, backlog, validator | M0 | verifying | — | — | D3 |
| OOS-0002 | Runtime, language and execution-mode decision (spike + ADR) | M1 | ready | OOS-0001 | — | D3 |
| OOS-0003 | Record store and schema validation library | M1 | proposed | OOS-0002 | — | D2 |
| OOS-0004 | Task graph engine: states, ready-set, DAG checks, revisions; per-project storage layout | M1 | proposed | OOS-0003 | — | D3 |
| OOS-0005 | Decision Engine v0: policy classifier, golden tests, escalation records | M1 | proposed | OOS-0003 | — | D2 |
| OOS-0006 | Context Router v0: rule-based packages, manifest, golden tests | M1 | proposed | OOS-0003, OOS-0004 | — | D2 |
| OOS-0007 | Execution backend contract + first headless adapter | M1 | proposed | OOS-0002, OOS-0003 | — | D3 |
| OOS-0008 | Dispatcher, worktree manager and Policy Guard v0 | M1 | proposed | OOS-0007 | — | D3 |
| OOS-0009 | Verifier v0: gates, SHA-bound evidence collection | M1 | proposed | OOS-0004, OOS-0008 | — | D2 |
| OOS-0010 | Core loop v0 on a sandbox repo: one full iteration, digest, circuit breaker | M1 | proposed | OOS-0005, OOS-0006, OOS-0009 | OQ-003, OQ-005 | D3 |
| OOS-0011 | Memory Manager: decision log, learnings, failed approaches, handoff, staleness | M2 | proposed | OOS-0010 | — | D2 |
| OOS-0012 | User-context import tooling + first curated import (with Billy) | M2 | proposed | OOS-0003 | OQ-001 | D4 |
| OOS-0013 | Role Composer + Backend Router + second backend adapter | M3 | proposed | OOS-0010 | OQ-004 | D3 |
| OOS-0014 | Parallel execution: worktree pool, leases, merge-conflict handling | M3 | proposed | OOS-0013 | — | D3 |
| OOS-0015 | Independent review stance + conflicting-recommendation resolution | M3 | proposed | OOS-0013 | — | D2 |
| OOS-0016 | Sandbox pilot: drive a throwaway project across a milestone; calibrate D-levels | M4 | proposed | OOS-0011, OOS-0014, OOS-0015 | — | D3 |
| OOS-0017 | Demon Codex pilot onboarding (project config only; core stays agnostic) | M4 | proposed | OOS-0016, OOS-0012 | — | D4 |

## Dependency graph (topological waves)

Items in the same wave do not depend on each other and can run in parallel once their
dependencies are done.

| Wave | Items | Waits for |
|---|---|---|
| 0 | OOS-0001 | — |
| 1 | OOS-0002 | 0001 |
| 2 | OOS-0003 | 0002 |
| 3 | OOS-0004 · OOS-0005 · OOS-0007 · OOS-0012 | 0003 (+0002 for 0007; OQ-001 for 0012) |
| 4 | OOS-0006 · OOS-0008 | 0003+0004 · 0007 |
| 5 | OOS-0009 | 0004+0008 |
| 6 | OOS-0010 | 0005+0006+0009 (OQ-003, OQ-005) |
| 7 | OOS-0011 · OOS-0013 | 0010 (OQ-004 for 0013) |
| 8 | OOS-0014 · OOS-0015 | 0013 |
| 9 | OOS-0016 | 0011+0014+0015 |
| 10 | OOS-0017 | 0016+0012 |

Critical path: 0001 → 0002 → 0003 → 0007 → 0008 → 0009 → 0010 → 0013 → 0014 → 0016 → 0017.


---

## OOS-0001: Foundation

**Status:** verifying (awaiting Billy's review) · **Milestone:** M0 · **Level:** D3 (founding ADRs)

**Objective.** Establish the architectural and project-management foundation: vision,
architecture, the models for decisions, memory, personal context, context routing, task graph,
verification, failure handling, git and security, plus schemas, machine-readable policy, an initial
backlog, and a validator that keeps them consistent.

**In scope**
- Docs under `docs/` (including ADR-0001 to ADR-0005)
- `context/` placeholders and the import protocol (no facts about Billy)
- `memory/` initialized for the OOS project itself
- `orchestration/` policy and registries (declarative only)
- `schemas/` for every durable record type
- `project/` vision, milestones, OKRs and backlog
- `tools/validate.py` (stdlib only) and `tests/`

**Out of scope**
- Any orchestrator runtime: loop, router, engine, dispatcher or adapters
- Choosing an implementation language (OOS-0002)
- Integrating any backend (Claude Code, Codex)
- Importing user context
- Anything in Demon Codex

**Acceptance criteria**
1. All files listed in the README repository map exist.
2. `python tools/validate.py` passes. `python -m unittest discover tests` passes.
3. No user-context entries exist. Every context file is marked placeholder.
4. Core docs contain no pilot-project specifics.
5. The work is committed on `oos-0001/foundation`, with nothing on `main`.

**Gates:** G-DOCS, G-SCOPE, G-REVIEW (Billy), G-HUMAN (Billy).

## OOS-0002: Runtime, language and execution-mode decision

**Objective.** Choose the control-plane implementation language and runtime, and decide
whether the loop runs as scheduled sessions or as a daemon. Produce an ADR.
**Approach.** A time-boxed spike that compares 2–3 options on: availability on Billy's
platform, ease of driving CLI agents headlessly, JSON Schema tooling, testability, and
contributor familiarity (`context/` may supply evidence once populated).
**Out of scope.** Building any component.
**Gates.** G-DOCS, G-REVIEW.

## OOS-0003 to OOS-0017

Each item gets a full scope, out-of-scope list and acceptance-criteria block like the two
above when it becomes `ready`. Writing that block is part of making it ready, and it is
written with the evidence available at that time. That evidence may include replanning.
