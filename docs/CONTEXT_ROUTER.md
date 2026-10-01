# Context Router

> **Right context, not maximum context.**

## 1. Purpose

The Context Router builds the **smallest useful context package** for one agent run.
More context is not free. It dilutes attention, raises cost, leaks unrelated user
context, and makes injected content more likely to be obeyed. Routing is
a deliberate, explainable selection with a recorded manifest.

The routing **mechanism** is kernel ([`orchestration/kernel/context_routing.json`](../orchestration/kernel/context_routing.json)).
Capability **profiles** and the **user-context ceiling** come from domain packages
(for example [`domains/software-development/context_routing.json`](../domains/software-development/context_routing.json)).

## 2. Four context scopes

| Scope | Holds | Example |
|---|---|---|
| **User context** | Information about Billy that *may* influence decisions across projects | a hypothetical aesthetic preference, risk appetite, review habits |
| **Domain context** | Knowledge and policy for a domain | software: gates, floors, conventions · finance: risk vocabulary, stricter authority |
| **Project context** | Canonical truth and decisions for one project | requirements, ADRs, claims, memory |
| **Task context** | The smallest useful package for one agent on one task, built from the three above | *the router's output* |

**User preference ≠ project requirement.** A user preference reaches a task only after
relevance is established through domain, project and task. It arrives labelled as evidence.

## 3. Inputs

| Input | Source | Used for |
|---|---|---|
| Task node | Task graph | goal, acceptance criteria, `task_type`, resource scope, dependencies |
| Profile | Orchestrator profile | which domain packages, and therefore which capability profiles and ceilings, apply |
| Project | Project registry | which `ProjectStore` to read |
| Role / capabilities | Role Composer | which context *kinds* are relevant (domain capability profile) |
| Risk / decision level | Decision Engine | higher risk means more constraints and decisions included, and stricter trust labels |
| Current milestone | Task graph | which outcomes and assumptions are in force |
| Relevant decisions | Decision log + ADR index | decisions touching the same resources or components |
| Backend descriptor | Backend registry | token budget, tool support (affects packaging) |

## 4. Output: the context package

The package conforms to [`schemas/context-package.schema.json`](../schemas/context-package.schema.json).

```
ContextPackage  (profile_id, built_at_version)
├── task_brief           (always)  objective, acceptance criteria, out-of-scope, evidence required
├── authority            (always)  allowed action classes, D-level ceiling, resource scope, escalation instructions
├── constraints          (always)  kernel/domain prohibitions + hard constraints + requirements relevant to this task
├── domain_context       (scoped)  domain conventions, gates and policies that bear on this task
├── project_truth        (scoped)  pointers + excerpts: resources, ADRs, claims, assumptions in force
├── memory               (scoped)  relevant learnings + failed approaches for these resources/capabilities
├── user_context         (gated)   individual CTX entries that passed the relevance pipeline (often empty)
├── general_knowledge    (gated)   retrieved docs, each labelled UNTRUSTED with source
└── manifest             (always)  every item: ref, why included, layer, trust label, token cost
```

Each item carries its **layer** and **trust label** (`trusted_policy`, `project_truth`,
`user_context`, `untrusted_external`, `agent_output`). Backend adapters must render
these boundaries visibly, for example in fenced sections, so that untrusted text cannot
masquerade as instructions.

## 5. Selection algorithm (v0, rule-based)

```
1. MANDATORY: task_brief, authority, constraints that intersect the task's scope.
   (Never trimmed. If they exceed the budget, the task is too big → split it.)
2. CANDIDATES: gather from each layer using the task's keys:
     resources in scope · capability tags · milestone · decision IDs linked in the graph
3. FILTER by routing policy:
     - domain_context: only the active profile's domains; only items relevant to the task type
     - user_context: the relevance pipeline (§6). An entry must pass every step.
     - memory: only entries whose scope/capabilities intersect; FAILED_APPROACHES always
       included when they touch the same resources
4. RANK by relevance score:
     score = w_dep·(direct dependency) + w_scope·(resource overlap)
           + w_recency·(recency) + w_auth·(source authority rank) + w_risk·(risk relevance)
5. PACK under the backend's budget: prefer pointers + short excerpts over full documents.
6. EMIT manifest with inclusion reasons AND notable exclusions
   ("CTX-0012 excluded: category 'creative' outside finance ceiling").
```

The weights are calibrated in OOS-0006. The rule-based v0 is deliberate: it is
explainable and testable. A learned or embedding-based ranker may *augment* step 4 later.
It may never override step 3.

## 6. User-context relevance pipeline

Defined in the kernel. Every step must pass:

1. `status == active`
2. category is within the **domain ceiling** (`user_context_ceiling` of the domain package)
3. category is within the **capability profile** allowance
4. `scope` matches: `global`, `domain:<this domain>`, or `project:<this project>`
5. the task capability is in `applies_to_capabilities`
6. any profile condition holds (for example `milestone_planning_only`)

**Hypothetical example.** A preference for dark, symbolic, mythological aesthetics
(`category: creative`):

| Task | Domain ceiling | Profile | Result |
|---|---|---|---|
| UI/art/naming for a dark-fantasy game | software allows `creative` | `creative_engineering` allows `creative` | **routed** (as evidence; a project decision may already bind) |
| Branding for another creative product | allows | `creative` allows | routed, weighted by scope match |
| Database migration in the same game | allows | `data` allows none | **excluded** |
| Portfolio calculation in a finance project | finance ceiling excludes `creative` | — | **excluded at step 2** |

## 7. Capability profiles (software-development domain)

| Capability | user_context categories allowed | Always include |
|---|---|---|
| `ux`, `frontend`, `game_development` | creative, working_style | design ADRs, UI constraints |
| `product_analysis` | creative, decision_preference, long_term_vision | requirements, outcomes |
| `architecture` | decision_preference, long_term_vision (milestone planning only) | ADR index, constraints |
| `database`, `backend`, `performance` | **none** | schema/data ADRs, failed approaches on the same resources |
| `security` | **none** | security policy, trust boundaries |
| `testing`, `code_review` | working_style (review habits only) | acceptance criteria, gate definition |

The control plane itself (Intake, Decision Engine, Escalation) may read the `profile`,
`working_style`, `decision_preference` and `long_term_vision` categories to plan, weigh
trade-offs and format escalations (`control_plane_user_context`). That does not make them
routable to agent roles.

## 8. Failure modes and responses

| Situation | Response |
|---|---|
| Mandatory context exceeds budget | Do not truncate constraints. Ask the Planner to split the task. |
| Agent reports insufficient context | Treat it as a signal, not a failure. Re-route with the specific gap, at most twice, then escalate to Planner (see [FAILURE_HANDLING](FAILURE_HANDLING.md)). |
| Pointed-to artifact changed since routing | The package records `built_at_version`. The Verifier flags runs based on stale context. |
| User context conflicts with a project claim | Include both, labelled. Conflict order is in [KNOWLEDGE_TAXONOMY §6](KNOWLEDGE_TAXONOMY.md#6-conflict-resolution-order). |

## 9. Testability

Routing is a pure function of inputs and policy, so golden tests are possible.
For example: "Given task T with capability `database`, the package must contain ADR-0007 and
FAILED-0003, and must contain no `user_context`." Another: "No finance-domain package ever
contains a `creative` entry." These tests are part of OOS-0006.
