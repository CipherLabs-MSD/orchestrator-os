# Architecture

> Status: **design** (OOS-0001). Component names are the stable vocabulary that
> later implementation tasks build against. Nothing described here is implemented yet.

## 1. Core Architectural Principle: Domain-Specialized Orchestration

> **Orchestrator OS provides one domain-agnostic orchestration kernel. Specialized
> orchestrators (Software Development, Finance, Game Development, Research, Creative
> Production, …) are configured instances of that kernel. They are never forks of it.**

Decision record: [ADR-0006](adr/ADR-0006-domain-agnostic-kernel.md). Package contract,
composition rules, the factory direction and worked examples: [DOMAIN_PACKAGES](DOMAIN_PACKAGES.md).

```
                         ORCHESTRATOR OS KERNEL  (orchestration/kernel/, docs/*)
                 ┌──────────────────────────────────────────────┐
                 │ Orchestration loop      Decision Engine       │
                 │ Task graph              Context Router        │
                 │ Capability registry     Backend (model) Router│
                 │ Memory interfaces       Verification framework│
                 │ Authority & permissions Escalation, audit     │
                 └──────────────────────┬───────────────────────┘
                                        │ loads
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
  domains/software-development   domains/finance (illustrative)   domains/<future>
           │                            │                            │
           ▼ composed by a profile      ▼                            ▼
  Software Development           Finance Orchestrator           Future Orchestrator
  Orchestrator                   (not operational)
  (orchestration/profiles/software-development.json)
```

### 1.1 Responsibilities

| Layer | Owns | Must not contain |
|---|---|---|
| **Kernel** | Control loop. Goal/outcome/task graph. Dependencies, planning and replanning. Capability *registry mechanism*. Backend/model routing. Context routing *mechanism*. Memory *interfaces*. Decision-authority framework (levels, dimensions, generic floors, prohibitions, composition rules). Verification framework (gates, evidence base types, verdicts). Permission framework and Policy Guard. Escalation. Execution state. Failure/retry policy. Audit and provenance. Human decision gates. | Any domain vocabulary or threshold: no tests/builds/commits, no trades/portfolios, no engines, no named projects |
| **Domain package** (`domains/<id>/`) | Capabilities. Domain policy (extra class floors, rules, prohibitions, cost calibration). Verification gates and specialized evidence types. Task types. Context profiles and the user-context ceiling. Memory record types. Declared tools. **Workspace binding** (how the kernel's project-store, workspace and change-set interfaces map onto real systems). Domain escalation rules. | Changes to kernel mechanisms. Any loosening of kernel policy. |
| **Orchestrator profile** (`orchestration/profiles/<id>.json`) | Which domain packages are loaded. Allowed backends. Tighten-only overrides and `reserved_for_billy`. | Code. A profile is configuration only. |
| **Project** (in its own store) | Project truth, requirements, constraints, memory, project overrides | Kernel or domain changes |

### 1.2 Kernel interfaces (bound per domain)

The kernel talks to the world only through interfaces. Each domain's **workspace binding**
says what they mean concretely. Git is the software binding, not a kernel assumption.

| Kernel interface | Meaning | Software-development binding | Finance binding (illustrative) |
|---|---|---|---|
| `ProjectStore` | Canonical, versioned project truth | git repository (+ `.oos/`) | research archive + proposal ledger |
| `Workspace` | Isolated place where one run makes changes | branch + worktree | sandboxed analysis workspace |
| `ChangeSet` | Reviewable, revertible unit of change | commits on a task branch | analysis artifacts, transaction *proposals* |
| `ArtifactVersion` | Immutable identifier evidence is bound to | commit SHA | content hash + data snapshot id |
| `Integration` | Acceptance into canonical state, under integration authority | reviewed merge to a protected branch | approved execution (a D4 action) |
| `Observer` | Reads current state at OBSERVE | git status, tests, CI | data feeds, positions (read-only) |
| `ToolAdapter` | A tool, with every action mapped to an action class | git, test runner, build | market data (read), broker (prepare-only) |

### 1.3 Kernel vs. domain naming

| Kernel concept | Software-development specialization | Finance (illustrative) | Game-development (future) |
|---|---|---|---|
| `Capability` | `backend`, `testing` (task: *run unit tests*) | `risk_analysis` | `gameplay_systems` |
| `AuthorityPolicy` | `history_rewrite_or_force_push` floor D4 | `TransactionApprovalPolicy` | — |
| `VerificationRequirement` (gate) | `G-TEST`, `G-BUILD` | `PortfolioRiskVerification` | `G-PLAYTEST` |
| `Evidence` (base type) | `test_result` extends `check_result` | `portfolio_risk_check` extends `check_result` | `HumanPlaytestEvidence` extends `human_acceptance` |
| `ContextProfile` | `data`, `creative_engineering` | `quant` | `art_direction` |

### 1.4 Invariants

- **I-1 No domain contamination.** *Domain-specific assumptions must not be introduced
  into the Orchestrator OS kernel unless they represent a genuinely domain-independent
  orchestration capability and are justified by an architectural decision (ADR).*
  Examples that would violate it: hard-coded trading concepts, game-engine concepts, or
  repository-host assumptions where a generic interface would do. Pilot-project
  terminology in orchestration logic. Domain risk thresholds in the generic Decision Engine.
- **I-2 Tighten-only composition.** Domains, profiles and projects may raise kernel
  levels, floors and prohibitions. They may never lower them ([DOMAIN_PACKAGES §4](DOMAIN_PACKAGES.md#4-composition-rules)).
- **I-3 Capability ≠ authority, in the kernel.** Every tool action maps to an action class
  that the kernel authority framework decides. No domain can opt out of this.
- **I-4 Configuration, not forks.** A new specialized orchestrator is a new profile, plus
  possibly a new domain package. It is never a copy of the kernel.
- **I-5 Provider-independent.** A specialized orchestrator is not tied to a model vendor.
  Backends are selected per task (§3, [AGENT_MODEL](AGENT_MODEL.md)).
- **I-6 Interfaces, not systems.** The kernel names `ProjectStore`, `Workspace`,
  `ChangeSet` and `ArtifactVersion`, never a specific VCS or hosting service.

`tools/validate.py` enforces I-1, as far as text can be checked, on the kernel's
machine-readable files and schemas. It enforces I-2 on every domain package, including
illustrative ones.

## 2. Shape

Orchestrator OS is a **control plane** that sits above one or more **managed projects**
and one or more **execution backends**. It runs as a specialized orchestrator, meaning a
profile, for each project's domain. The control plane holds no project content. It reads
project truth, plans, delegates work to agents running on backends, and accepts results
only when evidence passes a gate.

```
                ┌──────────────────────── Billy ────────────────────────┐
                │ vision / intent        escalations (D4)      approvals │
                └───────┬───────────────────────▲──────────────────▲────┘
                        │                       │                  │
┌───────────────────────▼───────────────────────┴──────────────────┴──────────┐
│        ORCHESTRATOR CONTROL PLANE  (kernel + profile's domain packages)      │
│                                                                              │
│  Intake ──► Observer ──► Planner ◄──────────── Learner ◄──────┐              │
│                │            │  (task graph)                    │              │
│                │            ▼                                  │              │
│                │      Decision Engine ──► Escalation ──► Billy │              │
│                │            │ (composed policy: authorized?)   │              │
│                │            ▼                                  │              │
│                │   Role Composer ◄── Capability Registry (domains)            │
│                │            │                                  │              │
│                │            ▼                                  │              │
│                │   Backend Router ◄── Backend Registry         │              │
│                │            │                                  │              │
│                │            ▼                                  │              │
│                └──► Context Router ──► context package         │              │
│                             │                                  │              │
│                             ▼                                  │              │
│   Policy Guard ═══► Dispatcher ──► (Workspace + backend) ──► Verifier ────────┘
│   (enforces authority      │            agent run               │  (gates, evidence)
│    outside the agent)      ▼                                    ▼
│                       Run Log (orchestrator state)        Memory Manager
└──────────────────────────────────────────────────────────────────────────────┘
          │ ChangeSets via the domain's workspace binding     │ read only, scoped
          ▼                                                   ▼
  ┌───────────────────────┐                     ┌─────────────────────────┐
  │ PROJECT STORE         │                     │ USER CONTEXT STORE      │
  │ content, ADRs, claims,│                     │ curated, provenance-    │
  │ project memory        │                     │ tracked entries (Billy) │
  └───────────────────────┘                     └─────────────────────────┘
```

## 3. Components (all kernel)

| Component | Responsibility | Primary inputs → outputs | Design doc |
|---|---|---|---|
| **Intake** | Turn vision or intent into goals and desired outcomes. Detect ambiguity. | vision text → GOAL/OUTCOME nodes, open questions | [TASK_GRAPH](TASK_GRAPH.md) |
| **Observer** | Inspect current project state through the domain's observers. Detect staleness. | project store → observation set | [CORE_LOOP](CORE_LOOP.md) |
| **Planner** | Create and revise the task graph. Treat plans as hypotheses. | goals + observations + learnings → graph revision | [TASK_GRAPH](TASK_GRAPH.md) |
| **Decision Engine** | Classify each decision against the **composed** policy (D1–D4, PROHIBITED). Authorize, escalate or refuse. | proposed decision → level + verdict | [DECISION_ENGINE](DECISION_ENGINE.md) |
| **Capability Registry** | Load capabilities from the profile's domain packages | — | [AGENT_MODEL](AGENT_MODEL.md) |
| **Role Composer** | Build an agent role for a task from required capabilities | task → role spec | [AGENT_MODEL](AGENT_MODEL.md) |
| **Backend Router** | Choose a backend by capability, task characteristics, context size, cost, latency, tools, reliability and data clearance | role + task → backend choice | [AGENT_MODEL](AGENT_MODEL.md) |
| **Context Router** | Build the *smallest useful* task context from user, domain and project context | task + role + profile → context package | [CONTEXT_ROUTER](CONTEXT_ROUTER.md) |
| **Policy Guard** | Enforce authority **outside** the agent: tool-action classes, resource scopes, secret scanning, protected resources | run request → allowed / denied | [SECURITY_AND_TRUST](SECURITY_AND_TRUST.md) |
| **Dispatcher** | Provision a `Workspace`, invoke the backend, enforce timeouts and budgets, collect artifacts | run spec → run result | [AGENT_MODEL](AGENT_MODEL.md) |
| **Verifier** | Evaluate evidence against the composed gates. Never trust self-reports. | run result → gate verdict | [VERIFICATION](VERIFICATION.md) |
| **Memory Manager** | Write decisions, learnings, failed approaches and handoff. Keep pointers, not copies. | verdicts + decisions → memory | [MEMORY_MODEL](MEMORY_MODEL.md) |
| **Learner** | Turn outcomes into plan-relevant knowledge and trigger replanning | memory deltas → planner signals | [CORE_LOOP](CORE_LOOP.md) |
| **Escalation** | Package D4 decisions for Billy with options, a recommendation and the cost of waiting | decision → question | [DECISION_ENGINE](DECISION_ENGINE.md) |

## 4. Knowledge layers and context scopes

Rationale: [ADR-0002](adr/ADR-0002-four-layer-knowledge-separation.md), amended by
[ADR-0006](adr/ADR-0006-domain-agnostic-kernel.md) to add the domain layer.

| Layer | What it holds | Location | Owner | Lifetime |
|---|---|---|---|---|
| **User context** | Curated facts about Billy that may influence decisions across projects | User Context Store (schema in `context/`, instance location: OQ-001) | Billy (curated) | Evolves, with provenance |
| **Domain context** | Domain knowledge and policy: capabilities, gates, floors, domain defaults and constraints | `domains/<id>/` | OOS (changes are D4 for policy) | Versioned with OOS |
| **Project truth** | Content, ADRs, history, requirements, constraints, project memory | The project's `ProjectStore` (repository-backed: `.oos/` + the project's docs) | The project | Lives with the project |
| **General knowledge** | Model knowledge, external docs, research results | Model weights + retrieved sources (untrusted) | Nobody (external) | Re-verified when used |
| **Orchestrator state** | Run logs, graph pointers, leases, budgets, retry counters, escalation queue | OOS workspace (outside project stores) | OOS | Operational. Summarized into project memory. |

The **task context** is not a store. It is the Context Router's *output*: the smallest
useful selection from the layers above, for one agent and one task
([CONTEXT_ROUTER](CONTEXT_ROUTER.md)).

**Invariant:** information crosses layers only through an explicit, logged step.
For example, a user preference is cited as *evidence* in a project decision record. Layers
are never concatenated wholesale into a prompt.

## 5. Key architectural decisions

| ADR | Decision |
|---|---|
| [ADR-0001](adr/ADR-0001-files-first-git-backed-state.md) | OOS's own durable state is plain files in git, validated by schemas |
| [ADR-0002](adr/ADR-0002-four-layer-knowledge-separation.md) | Separated knowledge layers, routed selectively (domain layer added by ADR-0006) |
| [ADR-0003](adr/ADR-0003-authority-separate-from-capability.md) | Authority is modelled and enforced separately from capability |
| [ADR-0004](adr/ADR-0004-execution-backend-abstraction.md) | Execution backends sit behind a vendor-neutral contract |
| [ADR-0005](adr/ADR-0005-evidence-gated-completion.md) | Completion requires gate-specific evidence, verified independently |
| [ADR-0006](adr/ADR-0006-domain-agnostic-kernel.md) | One domain-agnostic kernel plus domain packages, composed into profiles, instead of separate orchestrator codebases |

## 6. Future direction: an orchestrator that generates orchestrators

The kernel is shaped so that OOS can eventually *produce* a domain package and profile
from a domain definition, with high-impact authority rules approved by Billy. This is
documented in [DOMAIN_PACKAGES §6](DOMAIN_PACKAGES.md#6-future-the-orchestrator-factory)
and is not built (OOS-0019).

## 7. Explicitly not decided yet

These are tracked in the backlog and in [`memory/OPEN_QUESTIONS.md`](../memory/OPEN_QUESTIONS.md):

- Implementation language and runtime for the control plane (OOS-0002 spike).
- Whether the orchestrator runs as a long-lived daemon or as scheduled sessions (OOS-0002).
- Physical location of the User Context Store (OQ-001, needs Billy).
- Per-project OOS state layout for repository-backed projects (`.oos/` proposed; OQ-002, decided in OOS-0004).
- Domain package loading and composition implementation (OOS-0018).
