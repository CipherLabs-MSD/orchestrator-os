# Backlog

Stable IDs `OOS-NNNN`. IDs are never reused. Cancelled items stay with `cancelled` status.
Machine view: [`backlog.json`](backlog.json). The two must agree on ID, milestone, status and
dependencies, and `tools/validate.py` checks this. Questions: [`memory/OPEN_QUESTIONS.md`](../memory/OPEN_QUESTIONS.md).

## Index

| ID | Title | M | Status | Depends on | Blocked by (questions) | Expected level |
|---|---|---|---|---|---|---|
| OOS-0001 | Foundation: architecture, kernel/domain separation, models, policies, schemas, backlog, validator | M0 | done | — | — | D3 |
| OOS-0002 | Runtime, language and execution-mode decision (spike + ADR) | M1 | done | OOS-0001 | — | D3 |
| OOS-0003 | Record store and schema validation library | M1 | verifying | OOS-0002 | — | D2 |
| OOS-0004 | Task graph engine: states, ready-set, DAG checks, revisions; per-project storage layout | M1 | proposed | OOS-0003 | — | D3 |
| OOS-0005 | Decision Engine v0: policy classifier, golden tests, escalation records | M1 | proposed | OOS-0003, OOS-0018 | — | D2 |
| OOS-0006 | Context Router v0: rule-based packages, manifest, golden tests | M1 | proposed | OOS-0003, OOS-0004, OOS-0018 | — | D2 |
| OOS-0007 | Execution backend contract + first headless adapter | M1 | proposed | OOS-0002, OOS-0003 | — | D3 |
| OOS-0008 | Dispatcher, Workspace manager (software binding: worktrees) and Policy Guard v0 | M1 | proposed | OOS-0007 | — | D3 |
| OOS-0009 | Verifier v0: composed gates, version-bound evidence collection | M1 | proposed | OOS-0004, OOS-0008, OOS-0018 | — | D2 |
| OOS-0010 | Core loop v0 on a sandbox repo: one full iteration, digest, circuit breaker | M1 | proposed | OOS-0005, OOS-0006, OOS-0009 | — | D3 |
| OOS-0011 | Memory Manager: decision log, learnings, failed approaches, handoff, staleness | M2 | proposed | OOS-0010 | — | D2 |
| OOS-0012 | Private user-context store (orchestrator-context) + import tooling + first curated import (with Billy) | M2 | proposed | OOS-0003 | — | D4 |
| OOS-0013 | Role Composer + Backend Router + second backend adapter | M3 | proposed | OOS-0010 | — | D3 |
| OOS-0014 | Parallel execution: workspace pool, leases, change-set conflict handling | M3 | proposed | OOS-0013 | — | D3 |
| OOS-0015 | Independent review stance + conflicting-recommendation resolution | M3 | proposed | OOS-0013 | — | D2 |
| OOS-0016 | Sandbox pilot: drive a throwaway project across a milestone; calibrate D-levels | M4 | proposed | OOS-0011, OOS-0014, OOS-0015 | — | D3 |
| OOS-0017 | Demon Codex pilot onboarding (project config only; core stays agnostic) | M4 | proposed | OOS-0016, OOS-0012 | — | D4 |
| OOS-0018 | Domain package loader + profile composition (tighten-only merge, kernel purity) | M1 | proposed | OOS-0003 | — | D3 |
| OOS-0019 | Orchestrator Factory: generate draft domain package + profile from a domain definition | M5 | proposed | OOS-0020 | — | D3 |
| OOS-0020 | Second operational domain package (candidate: finance) with Billy-approved authority rules | M5 | proposed | OOS-0016, OOS-0018 | OQ-007 | D4 |

## Dependency graph (topological waves)

Items in the same wave do not depend on each other and can run in parallel once their
dependencies are done.

| Wave | Items | Waits for |
|---|---|---|
| 0 | OOS-0001 | — |
| 1 | OOS-0002 | 0001 |
| 2 | OOS-0003 | 0002 |
| 3 | OOS-0004 · OOS-0007 · OOS-0012 · OOS-0018 | 0003 · 0002+0003 · 0003 · 0003 |
| 4 | OOS-0005 · OOS-0006 · OOS-0008 | 0003+0018 · 0003+0004+0018 · 0007 |
| 5 | OOS-0009 | 0004+0008+0018 |
| 6 | OOS-0010 | 0005+0006+0009 |
| 7 | OOS-0011 · OOS-0013 | 0010 · 0010 |
| 8 | OOS-0014 · OOS-0015 | 0013 · 0013 |
| 9 | OOS-0016 | 0011+0014+0015 |
| 10 | OOS-0017 · OOS-0020 | 0016+0012 · 0016+0018 (OQ-007) |
| 11 | OOS-0019 | 0020 |

Critical path: 0001 → 0002 → 0003 → 0007 → 0008 → 0009 → 0010 → 0013 → 0014 → 0016 → 0020 → 0019.


---

## OOS-0001: Foundation

**Status:** **DONE** (2026-10-01) · owner-accepted ([DEC-0004](../memory/DECISIONS/DEC-0004-oos-0001-owner-acceptance.md)) · PRIV-0001 resolved ([DEC-0005](../memory/DECISIONS/DEC-0005-priv-0001-history-rewrite.md)) · **Milestone:** M0 · **Level:** D3 (founding ADRs) · owner policy: [ADR-0007](../docs/adr/ADR-0007-initial-owner-policy.md)

**Objective.** Establish the architectural and project-management foundation: vision,
architecture, the models for decisions, memory, personal context, context routing, task graph,
verification, failure handling, git and security, plus schemas, machine-readable policy, an initial
backlog, and a validator that keeps them consistent.
**Addendum (same task):** make *domain-specialized orchestration* a founding principle, with a
domain-agnostic kernel, domain packages and orchestrator profiles (ADR-0006). Audit and correct
software, vendor and git assumptions in the kernel.

**In scope**
- Docs under `docs/` (including ADR-0001 to ADR-0005)
- `context/` placeholders and the import protocol (no facts about Billy)
- `memory/` initialized for the OOS project itself
- `orchestration/kernel/` (domain-independent policy), `orchestration/profiles/`, `orchestration/backends.json`
- `domains/software-development/` (moved software config), `domains/finance/` (**illustrative sketch only**)
- `schemas/` for every durable record type
- `project/` vision, milestones, OKRs and backlog
- `tools/validate.py` (stdlib only) and `tests/`

**Out of scope**
- Any orchestrator runtime: loop, router, engine, dispatcher or adapters
- Choosing an implementation language (OOS-0002)
- Integrating any backend (Claude Code, Claude Agent SDK, Claude API, Codex)
- Building FinanceOS, a real finance package, any financial threshold or trading policy
- Implementing the domain loader (OOS-0018) or the Orchestrator Factory (OOS-0019)
- Importing user context
- Anything in Demon Codex

**Acceptance criteria**
1. All files listed in the README repository map exist.
2. `python tools/validate.py` passes. `python -m unittest discover tests` passes.
3. No user-context entries exist. Every context file is marked placeholder.
4. Core docs contain no pilot-project specifics. Kernel JSON and schemas contain no domain
   vocabulary. Every domain package composes tighten-only (validator).
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

**Result (2026-10-01). DONE: Billy reviewed and merged PR #1 on 2026-10-02.**
- Decision: [ADR-0008](../docs/adr/ADR-0008-runtime-and-execution-model.md). **Python ≥ 3.12** (stdlib-first, asyncio).
  **Hybrid execution model**: session-oriented resumable runs now, with a scheduler or daemon later as a trigger only.
- Design constraints for OOS-0003, 0007 and 0008: [EXECUTION_RUNTIME](../docs/EXECUTION_RUNTIME.md).
- Evidence: [`spikes/oos-0002/`](../spikes/oos-0002/) (disposable), `tests/test_spike_oos0002.py`.
- Tested on Windows 11 only. macOS is **unverified**, and OOS-0008 must collect macOS evidence.
- Owner action: install Python 3.12+ on the development machine before OOS-0003 needs it.

## OOS-0003: Record store and schema validation library

**Status:** verifying (awaiting Billy's review of the PR) · **Gates:** G-TEST, G-STATIC, G-REVIEW

- Delivered: `oos/records/` (SchemaRegistry, RecordStore, AppendLog), envelope and log-entry schemas,
  `x-oos-schema-version` on every schema, `orchestration/kernel/record_types.json`,
  [ADR-0009](../docs/adr/ADR-0009-record-store.md), [DEC-0006](../memory/DECISIONS/DEC-0006-fail-closed-schema-subset.md)
  and [RECORD_STORE](../docs/RECORD_STORE.md).
- G-TEST: store and log tests, plus `tools/store_sabotage_check.py` (5/6 caught; fsync is a documented untestable gap).
- G-STATIC: **only partly met.** `compileall -W error` is clean, but no linter or type checker is adopted yet (OQ-008, a D2 decision).
- Not in scope: task graph, decision engine, router, adapters, scheduler, private context store.

## OOS-0004 to OOS-0020

Each item gets a full scope, out-of-scope list and acceptance-criteria block like the two
above when it becomes `ready`. Writing that block is part of making it ready, and it is
written with the evidence available at that time. That evidence may include replanning.
