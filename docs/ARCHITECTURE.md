# Architecture

> Status: **design** (OOS-0001). Component names are the stable vocabulary that
> later implementation tasks build against. Nothing described here is implemented yet.

## 1. Shape

Orchestrator OS is a **control plane** that sits above one or more **managed
projects** and one or more **execution backends**. The control plane holds no
project code. It reads project truth, plans, delegates work to agents running on
backends, and accepts results only when evidence passes a gate.

```
                ┌──────────────────────── Billy ────────────────────────┐
                │ vision / intent        escalations (D4)      approvals │
                └───────┬───────────────────────▲──────────────────▲────┘
                        │                       │                  │
┌───────────────────────▼───────────────────────┴──────────────────┴──────────┐
│                         ORCHESTRATOR CONTROL PLANE                           │
│                                                                              │
│  Intake ──► Observer ──► Planner ◄──────────── Learner ◄──────┐              │
│                │            │  (task graph)                    │              │
│                │            ▼                                  │              │
│                │      Decision Engine ──► Escalation ──► Billy │              │
│                │            │ (authorized?)                    │              │
│                │            ▼                                  │              │
│                │   Role Composer ◄── Capability Registry       │              │
│                │            │                                  │              │
│                │            ▼                                  │              │
│                │   Backend Router ◄── Backend Registry         │              │
│                │            │                                  │              │
│                │            ▼                                  │              │
│                └──► Context Router ──► context package         │              │
│                             │                                  │              │
│                             ▼                                  │              │
│   Policy Guard ═══► Dispatcher ──► (worktree + backend) ──► Verifier ─────────┘
│   (enforces authority      │            agent run               │  (gates, evidence)
│    outside the agent)      ▼                                    ▼
│                       Run Log (orchestrator state)        Memory Manager
└──────────────────────────────────────────────────────────────────────────────┘
          │ read/write (via git, on branches)               │ read only, scoped
          ▼                                                 ▼
  ┌───────────────────────┐                     ┌─────────────────────────┐
  │ MANAGED PROJECT REPO  │                     │ USER CONTEXT STORE      │
  │ code, tests, ADRs,    │                     │ curated, provenance-    │
  │ project memory (.oos/)│                     │ tracked entries (Billy) │
  └───────────────────────┘                     └─────────────────────────┘
```

## 2. Components

| Component | Responsibility | Primary inputs → outputs | Design doc |
|---|---|---|---|
| **Intake** | Turn vision or intent into goals and desired outcomes. Detect ambiguity. | vision text → GOAL/OUTCOME nodes, open questions | [TASK_GRAPH](TASK_GRAPH.md) |
| **Observer** | Inspect current project state: git, tests, CI, memory, staleness | repo → observation set | [CORE_LOOP](CORE_LOOP.md) |
| **Planner** | Create and revise the task graph. Treat plans as hypotheses. | goals + observations + learnings → graph revision | [TASK_GRAPH](TASK_GRAPH.md) |
| **Decision Engine** | Classify each decision at D1–D4 and authorize or escalate it | proposed decision → level + verdict | [DECISION_ENGINE](DECISION_ENGINE.md) |
| **Capability Registry** | Catalogue capabilities and the role templates built from them | — | [AGENT_MODEL](AGENT_MODEL.md) |
| **Role Composer** | Build an agent role for a task from required capabilities | task → role spec | [AGENT_MODEL](AGENT_MODEL.md) |
| **Backend Registry / Router** | Choose an execution backend or model by capability, cost, context and risk | role + task → backend choice | [AGENT_MODEL](AGENT_MODEL.md) |
| **Context Router** | Build the *smallest useful* context package for a task | task + role + layers → context package | [CONTEXT_ROUTER](CONTEXT_ROUTER.md) |
| **Policy Guard** | Enforce authority **outside** the agent: tool permissions, path scopes, secret scanning, protected branches | run request → allowed / denied | [SECURITY_AND_TRUST](SECURITY_AND_TRUST.md) |
| **Dispatcher** | Provision a worktree, invoke the backend, enforce timeouts and budgets, collect artifacts | run spec → run result | [GIT_WORKFLOW](GIT_WORKFLOW.md) |
| **Verifier** | Evaluate evidence against verification gates. Never trust self-reports. | run result → gate verdict | [VERIFICATION](VERIFICATION.md) |
| **Memory Manager** | Write decisions, learnings, failed approaches and handoff. Keep pointers, not copies. | verdicts + decisions → memory | [MEMORY_MODEL](MEMORY_MODEL.md) |
| **Learner** | Turn outcomes into plan-relevant knowledge and trigger replanning | memory deltas → planner signals | [CORE_LOOP](CORE_LOOP.md) |
| **Escalation** | Package D4 decisions for Billy with options, a recommendation and the cost of waiting | decision → question | [DECISION_ENGINE](DECISION_ENGINE.md) |

## 3. The four knowledge layers and where they live

The rationale is in [ADR-0002](adr/ADR-0002-four-layer-knowledge-separation.md).

| Layer | What it holds | Location | Owner | Lifetime |
|---|---|---|---|---|
| **User context** | Curated facts about Billy: preferences, style, creative DNA, decision preferences, long-term vision | User Context Store (`context/` schema here, instance location: see OQ-001) | Billy (curated) | Evolves, with provenance |
| **Project truth** | Code, tests, ADRs, git history, project requirements and constraints, project memory | Inside each managed project repo (`.oos/` + the project's own docs) | The project | Lives with the code |
| **General knowledge** | Language and framework knowledge, external docs, research results | Model weights + retrieved sources (untrusted) | Nobody (external) | Re-verified when used |
| **Orchestrator state** | Run logs, active graph pointers, leases, budgets, retry counters, escalation queue | OOS workspace (outside project repos) | OOS | Operational. Summarized into project memory. |

**Invariant:** information crosses layers only through an explicit, logged step.
For example, a user preference is cited as *evidence* in a project decision record,
and that record lives in project truth. Layers are never concatenated wholesale into
a prompt.

## 4. Key architectural decisions

| ADR | Decision |
|---|---|
| [ADR-0001](adr/ADR-0001-files-first-git-backed-state.md) | Durable state is plain files in git, validated by schemas. No database until a need is proven. |
| [ADR-0002](adr/ADR-0002-four-layer-knowledge-separation.md) | Four knowledge layers, separated by location and by routing |
| [ADR-0003](adr/ADR-0003-authority-separate-from-capability.md) | Authority (what may be done) is modelled and enforced separately from capability (what can be done) |
| [ADR-0004](adr/ADR-0004-execution-backend-abstraction.md) | Execution backends sit behind a vendor-neutral contract |
| [ADR-0005](adr/ADR-0005-evidence-gated-completion.md) | Completion requires gate-specific evidence, verified by someone other than the producer |

## 5. Explicitly not decided yet

These are tracked in the backlog and in [`memory/OPEN_QUESTIONS.md`](../memory/OPEN_QUESTIONS.md):

- Implementation language and runtime for the control plane (OOS-0002 spike).
- Physical location of the User Context Store (OQ-001, needs Billy).
- Per-project OOS state layout (`.oos/` proposed; OQ-002, decided in OOS-0004).
- Whether the orchestrator itself runs as a long-lived daemon or as scheduled sessions (OOS-0002).
