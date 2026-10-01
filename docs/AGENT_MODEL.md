# Agent Model: capabilities, roles and execution backends

Three concepts are kept apart:

| Concept | Question it answers | Owned by | Registry |
|---|---|---|---|
| **Capability** | *What kind of work is this?* (backend, risk analysis, …) | **Domain packages**. The kernel owns the registry mechanism. | e.g. [`domains/software-development/capabilities.json`](../domains/software-development/capabilities.json) |
| **Role** | *Who should do it, with what context, tools and authority?* Composed per task from capabilities. | Kernel (Role Composer) | Role templates (future), plus ad-hoc composition |
| **Execution backend** (agent provider) | *Which system or model actually runs it?* (Claude Code, Claude Agent SDK, Claude API, Codex, …) | Kernel. Domain-independent. | [`orchestration/backends.json`](../orchestration/backends.json) |

The system is not hard-coded around implementer, tester and reviewer. Those are
common role templates, not architecture. A specialized orchestrator is also **not** a
"Claude orchestrator" or a "Codex orchestrator". Its profile lists the backends it *may*
use, and the router picks one per task.

## 1. Capability contract

Schema: [`schemas/capability.schema.json`](../schemas/capability.schema.json). Capability
ids are local to their domain package. Across domains they are qualified as
`<domain>/<id>`, for example `software-development/database` or `finance/risk_analysis`.

```json
{
  "id": "database",
  "name": "Database",
  "description": "Schema design, migrations, queries, data integrity.",
  "typical_task_types": ["feature", "migration", "investigation"],
  "context_profile": "data",
  "default_verification_gates": ["G-TEST", "G-MIGRATION", "G-REVIEW"],
  "risk_notes": "Persistent schema changes have a D3 floor; migrating existing data is often D4.",
  "related": ["backend", "performance"]
}
```

A capability is **descriptive**. It grants no permissions ([SECURITY_AND_TRUST §2](SECURITY_AND_TRUST.md#2-capability-vs-authority)).

## 2. Role composition

The Role Composer produces a **role spec** for each task:

```
RoleSpec
  role_id:            generated or template id ("implementer.backend", "reviewer.security")
  capabilities:       [primary, ...secondary]           ← from the task node
  stance:             produce | review | investigate | verify   ← separation of duties
  context_profile:    union of capability profiles, intersected with the task's risk rules
  action_classes:     the action classes this role may invoke    ← from authority, not capability
  tool_permissions:   least privilege for the stance + task scope
  authority_ceiling:  highest D-level this role may decide (normally D2; D3 only for architecture roles)
  backend_requirements: {min_context_tokens, needs_tools: [...], needs_vision, needs_workspace, max_latency}
  evidence_required:  gate ids (composed kernel + domain)
```

Rules:

- **Separation of duties.** A `review` or `verify` stance must not run in the same
  session, and should preferably not use the same backend or model, as the `produce`
  stance it checks.
- **Least privilege.** A `review` role gets read-only tools. An `investigate` role cannot
  integrate into canonical state. Tool permissions come from the
  [authority model](SECURITY_AND_TRUST.md), never from the capability.
- **Composition before proliferation.** Prefer composing `backend + security` into
  one role over defining a new agent type. A new role template is justified when a
  composition recurs and needs a specialized prompt or toolset.

## 3. Execution backend abstraction

Rationale: [ADR-0004](adr/ADR-0004-execution-backend-abstraction.md), amended by [ADR-0006](adr/ADR-0006-domain-agnostic-kernel.md).
Schema: [`schemas/execution-backend.schema.json`](../schemas/execution-backend.schema.json).

### Backend descriptor (what the router knows)

```
id, vendor, kind (cli_agent | agent_sdk | api_model | local_model | human)
strengths: [<domain>/<capability>]  ← evidence-based, updated from outcomes
latency: low | medium | high | unknown
reliability: pointer to outcome evidence (per domain/capability/task type)
context_window_tokens
supports: {tools, file_edit, shell, web, vision, isolated_workspace, headless}
cost_model: {unit, relative_cost}   ← relative tiers until real pricing is wired
limits: {max_runtime_s, concurrency}
trust: {data_policy_ok_for: [public, private, secret]}
status: declared | integrated | deprecated
```

### Adapter contract (what every integration must implement, OOS-0007)

```
prepare(run_spec)  → handle      # Workspace (per domain binding), rendered context package, permissions
start(handle)      → run_id
poll(run_id)       → status      # running | succeeded | failed | timed_out | needs_input
collect(run_id)    → RunResult   # ChangeSet, logs, artifacts, self-report, usage
cancel(run_id)
```

`RunResult.self_report` is stored, but it is **never** evidence of completion. The Verifier
collects evidence independently.

### Selection (Backend Router)

```
eligible = backends where status = integrated
                     ∧ id ∈ profile.backends_allowed                 (authority)
                     ∧ supports ⊇ role.backend_requirements          (available tools)
                     ∧ context_window ≥ package size                 (context requirements)
                     ∧ trust.data_policy_ok_for ∋ project.data_class (data clearance, per owner policy)
                     ∧ (no user context in package ∨ trust.user_context_ok)
choose argmax( fit(strengths, capabilities, task characteristics)
               − λ·relative_cost − κ·latency_penalty − μ·(1 − reliability) )
prefer a different backend than the producer for review stances
```

The routing factors are capability, task characteristics, context requirements, cost,
latency, available tools, reliability evidence and authority. The scoring is a starting
heuristic. It is calibrated from outcome data recorded per (backend, domain, capability, task type).

## 4. Initial registry contents (OOS-0001)

- **Capabilities:** the 14 in the software-development package. The finance sketch only names
  capabilities. These are definitions only.
- **Backends:** `claude-code`, `claude-agent-sdk`, `claude-api`, `codex` and `human` (Billy as a
  backend for acceptance and D4). All have `status: declared`. **No integrations are built.**
