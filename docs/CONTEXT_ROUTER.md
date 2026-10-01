# Context Router

> **Right context, not maximum context.**

## 1. Purpose

The Context Router builds the **smallest useful context package** for one agent run.
More context is not free. It dilutes attention, raises cost, leaks unrelated user
context, and makes injected content more likely to be obeyed. Routing is
a deliberate, explainable selection with a recorded manifest.

## 2. Inputs

| Input | Source | Used for |
|---|---|---|
| Task node | Task graph | goal, acceptance criteria, `type`, file scope, dependencies |
| Project | Project registry | which project-truth store to read |
| Role / capabilities | Role Composer | which context *kinds* are relevant (`orchestration/context_routing.json`) |
| Risk / decision level | Decision Engine | higher risk means more constraints and decisions included, and stricter trust labels |
| Current milestone | Task graph | which outcomes and assumptions are in force |
| Relevant decisions | Decision log + ADR index | decisions touching the same components or files |
| Backend profile | Backend registry | token budget, tool support (affects packaging) |

## 3. Output: the context package

The package conforms to [`schemas/context-package.schema.json`](../schemas/context-package.schema.json).

```
ContextPackage
├── task_brief           (always)  objective, acceptance criteria, out-of-scope, evidence required
├── authority            (always)  allowed actions, D-level ceiling, paths in scope, escalation instructions
├── constraints          (always)  hard constraints + project requirements relevant to this task
├── project_truth        (scoped)  pointers + excerpts: files, ADRs, decisions, assumptions in force
├── memory               (scoped)  relevant learnings + failed approaches for these components/capabilities
├── user_context         (gated)   individual CTX entries matched by capability + scope (often empty)
├── general_knowledge    (gated)   retrieved docs, each labelled UNTRUSTED with source
└── manifest             (always)  every item: id, why included, layer, trust label, token cost
```

Each item carries its **layer** and **trust label** (`trusted_policy`, `project_truth`,
`user_context`, `untrusted_external`, `agent_output`). Backend adapters must render
these boundaries visibly, for example in fenced sections, so that untrusted text cannot
masquerade as instructions.

## 4. Selection algorithm (v0, rule-based)

```
1. MANDATORY: task_brief, authority, constraints that intersect the task's scope.
   (Never trimmed. If they exceed the budget, the task is too big → split it.)
2. CANDIDATES: gather from each layer using the task's keys:
     files/components in scope · capability tags · milestone · decision IDs linked in the graph
3. FILTER by routing policy (orchestration/context_routing.json):
     - drop layers the capability profile excludes (e.g. database_migration → no creative)
     - user_context: only status=active, scope matches, capability ∈ applies_to_capabilities
     - memory: only entries whose scope/capabilities intersect; FAILED_APPROACHES always
       included when they touch the same files/components
4. RANK by relevance score:
     score = w_dep·(direct dependency) + w_scope·(file/component overlap)
           + w_recency·(recency) + w_auth·(source authority rank) + w_risk·(risk relevance)
5. PACK under the backend's budget: prefer pointers + short excerpts over full documents;
   agents may fetch pointed-to files themselves if their tools allow.
6. EMIT manifest with inclusion reasons AND notable exclusions
   ("CREATIVE_DNA excluded: capability profile 'database' disallows creative").
```

The weights are calibrated in OOS-0006. The rule-based v0 is deliberate: it is
explainable and testable. A learned or embedding-based ranker may *augment* step 4 later.
It may never override step 3.

## 5. Capability profiles (examples)

Defined in [`orchestration/context_routing.json`](../orchestration/context_routing.json):

| Capability | user_context categories allowed | Always include |
|---|---|---|
| `ux`, `frontend`, `game_development` | creative, working_style (light) | design ADRs, UI constraints |
| `product_analysis` | creative, decision_preference, long_term_vision | requirements, outcomes |
| `architecture` | decision_preference, long_term_vision (milestone planning only) | ADR index, constraints |
| `database`, `backend`, `performance` | **none** | schema/data ADRs, failed approaches on same tables or modules |
| `security` | **none** | security policy, trust boundaries |
| `testing`, `code_review` | working_style (review habits only) | acceptance criteria, gate definition |

The control plane itself (Intake, Decision Engine, Escalation) may read the `profile`,
`working_style`, `decision_preference` and `long_term_vision` categories to plan, weigh
trade-offs and format escalations (`control_plane_user_context`). That does not make them
routable to agent roles.

## 6. Failure modes and responses

| Situation | Response |
|---|---|
| Mandatory context exceeds budget | Do not truncate constraints. Ask the Planner to split the task. |
| Agent reports insufficient context | Treat it as a signal, not a failure. Re-route with the specific gap, at most twice, then escalate to Planner (see [FAILURE_HANDLING](FAILURE_HANDLING.md)). |
| Pointed-to artifact changed since routing | The manifest records the commit SHA. The Verifier flags runs based on stale context. |
| User context conflicts with a project claim | Include both, labelled. Conflict order is in [KNOWLEDGE_TAXONOMY §6](KNOWLEDGE_TAXONOMY.md#6-conflict-resolution-order). |

## 7. Testability

Routing is a pure function of inputs and policy, so golden tests are possible.
"Given task T with capability `database`, the package must contain ADR-0007 and
FAILED-0003, and must contain no `user_context`." These tests are part of OOS-0006.
