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

0. **Domain-specialized orchestration.** One domain-agnostic kernel. Specialized
   orchestrators (software development, finance, game development, research, …) are
   *configured* from it through domain packages and profiles, never forked
   ([ARCHITECTURE §1](docs/ARCHITECTURE.md#1-core-architectural-principle-domain-specialized-orchestration)).
1. **Separate knowledge layers.** These are user context, domain context, project truth, general
   knowledge, and orchestrator state. They are never merged into one prompt.
   "Billy likes X" is evidence for a decision. It is not automatically a requirement.
2. **Right context, not maximum context.** A Context Router builds the smallest
   useful context package for each agent.
3. **Authority is separate from capability.** Being able to do something does not mean
   being allowed to do it. The decision levels are D1–D4, plus PROHIBITED.
4. **Evidence-gated completion.** A task does not become DONE because an agent says
   it is done.
5. **Transactional, revertible change.** Work happens in isolated workspaces, as small
   reviewable change sets. Nothing reaches canonical state autonomously. For software,
   the binding is git: branches, worktrees and commits.
6. **Model independence.** Execution backends (Claude Code, Claude Agent SDK, Claude API,
   Codex, future systems) sit behind one contract and are chosen per task.
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
| [`orchestration/kernel/`](orchestration/kernel/) | **Kernel** policy: decision authority, verification framework, context-routing mechanism |
| [`orchestration/profiles/`](orchestration/profiles/) | Orchestrator profiles: kernel + domain packages = a specialized orchestrator |
| [`orchestration/backends.json`](orchestration/backends.json) | Execution backend (agent provider) registry |
| [`domains/`](domains/) | **Domain packages**: `software-development` (draft) and `finance` (illustrative only) |
| [`schemas/`](schemas/) | JSON Schemas for every durable record type |
| [`spikes/`](spikes/) | **Disposable** experiments that produce evidence for ADRs (OOS-0002 runtime spike). Never a dependency. |
| [`tools/`](tools/) | `validate.py`, a stdlib-only consistency checker |
| [`tests/`](tests/) | Tests for the validator and the foundation artifacts |

## Start here

- New to the project: [`docs/VISION.md`](docs/VISION.md), then [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
- Agents working in this repo: [`AGENTS.md`](AGENTS.md).
- Contributors: [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Current state and next step: [`memory/PROJECT_STATE.md`](memory/PROJECT_STATE.md) and [`memory/HANDOFF.md`](memory/HANDOFF.md).

## Validate

```sh
python tools/validate.py          # structure, cross-references, tighten-only composition, kernel purity, links
python -m unittest discover tests # test suite (stdlib only, Python ≥ 3.10)
python tools/mutation_check.py    # plants known defects in a temp copy; every one must be caught
python tools/prepublish_check.py   # before any push: scans the commits to be published
```
