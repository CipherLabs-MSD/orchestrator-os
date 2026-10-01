# Orchestrator OS

Orchestrator OS (OOS) is meant to become an autonomous software-development
organization that works under Billy's direction. Billy hands over a vision and a
plan, and OOS builds the application as far as it can intelligently and safely,
over long periods, with minimal prompting. It escalates only when a decision
exceeds its authority or genuinely needs human judgment.

> **Status: OOS-0001 (Foundation).** This repository currently contains the
> *design* of the system: architecture, models, policies, schemas, backlog, and
> a validator that keeps those artifacts consistent. There is no running
> orchestrator yet, and that is deliberate. See [`project/BACKLOG.md`](project/BACKLOG.md).

## The control loop

```
OBSERVE → ORIENT → PLAN → DELEGATE → EXECUTE → VERIFY → LEARN → REPLAN
   ↑                                                              │
   └──────────────────────────────────────────────────────────────┘
```

Plans are hypotheses. Evidence may overturn them. See [`docs/CORE_LOOP.md`](docs/CORE_LOOP.md).

## Core principles

1. **Four separate knowledge layers.** These are user context, project truth, general
   knowledge, and orchestrator state. They are never merged into one prompt.
   "Billy likes X" is evidence for a decision. It is not automatically a requirement.
2. **Right context, not maximum context.** A Context Router builds the smallest
   useful context package for each agent.
3. **Authority is separate from capability.** Being able to do something does not mean
   being allowed to do it. The decision levels are D1–D4.
4. **Evidence-gated completion.** A task does not become DONE because an agent says
   it is done.
5. **Git is the transaction log.** Work happens on isolated branches or worktrees, in small
   commits and reviewable diffs. Nothing reaches the protected branch autonomously.
6. **Model independence.** Execution backends (Claude Code, Codex, future
   systems) sit behind one contract.
7. **Project-agnostic core.** Pilot projects (first: Demon Codex) never leak
   their specifics into the core.

## Repository map

| Path | Purpose |
|---|---|
| [`docs/`](docs/) | Vision, architecture, and the design of each subsystem |
| [`docs/adr/`](docs/adr/) | Architecture Decision Records |
| [`project/`](project/) | Milestones, OKRs, and the backlog (`OOS-NNNN`) |
| [`context/`](context/) | **User context** layer (Billy). Placeholders only until a curated import |
| [`memory/`](memory/) | **Project memory** for Orchestrator OS itself (the project dogfoods its own model) |
| [`orchestration/`](orchestration/) | Machine-readable policy and registries: decision policy, capabilities, backends, gates, routing |
| [`schemas/`](schemas/) | JSON Schemas for every durable record type |
| [`tools/`](tools/) | `validate.py`, a stdlib-only consistency checker |
| [`tests/`](tests/) | Tests for the validator and the foundation artifacts |

## Start here

- New to the project: [`docs/VISION.md`](docs/VISION.md), then [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
- Agents working in this repo: [`AGENTS.md`](AGENTS.md).
- Contributors: [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Current state and next step: [`memory/PROJECT_STATE.md`](memory/PROJECT_STATE.md) and [`memory/HANDOFF.md`](memory/HANDOFF.md).

## Validate

```sh
python tools/validate.py          # structural + cross-reference checks
python -m unittest discover tests # test suite (stdlib only, Python ≥ 3.10)
```
