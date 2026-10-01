# Agent Model: capabilities, roles and execution backends

Three concepts are kept apart:

| Concept | Question it answers | Registry |
|---|---|---|
| **Capability** | *What kind of work is this?* (backend, database, security, …) | [`orchestration/capabilities.json`](../orchestration/capabilities.json) |
| **Role** | *Who should do it, with what context, tools and authority?* Composed per task from capabilities. | Role templates (future: `orchestration/roles/`), plus ad-hoc composition |
| **Execution backend** | *Which system or model actually runs it?* (Claude Code, Codex, …) | [`orchestration/backends.json`](../orchestration/backends.json) |

The system is not hard-coded around implementer, tester and reviewer. Those are
common role templates, not architecture.

## 1. Capability contract

Schema: [`schemas/capability.schema.json`](../schemas/capability.schema.json).

```json
{
  "id": "database",
  "name": "Database",
  "description": "Schema design, migrations, queries, data integrity.",
  "typical_task_types": ["implementation", "migration", "investigation"],
  "context_profile": "database",
  "default_verification_gates": ["G-TEST", "G-MIGRATION"],
  "risk_notes": "Migrations touching existing data trigger the persistent-schema class floor (D3) and may be D4.",
  "related": ["backend", "performance"]
}
```

A capability is **descriptive**. It grants no permissions.

## 2. Role composition

The Role Composer produces a **role spec** for each task:

```
RoleSpec
  role_id:            generated or template id ("implementer.backend", "reviewer.security")
  capabilities:       [primary, ...secondary]           ← from the task node
  stance:             produce | review | investigate | verify   ← separation of duties
  context_profile:    union of capability profiles, intersected with the task's risk rules
  tool_permissions:   least privilege for the stance + task scope   ← from authority, not capability
  authority_ceiling:  highest D-level this role may decide (normally D2; D3 only for architecture roles)
  backend_requirements: {min_context_tokens, needs_tools: [...], needs_vision, ...}
  evidence_required:  gate ids
```

Rules:

- **Separation of duties.** A `review` or `verify` stance must not run in the same
  session, and should preferably not use the same backend or model, as the `produce`
  stance it checks.
- **Least privilege.** A `review` role gets read-only tools. An `investigate` role gets no
  write access to the canonical branch. Tool permissions come from the
  [authority model](SECURITY_AND_TRUST.md), never from the capability.
- **Composition before proliferation.** Prefer composing `backend + security` into
  one role over defining a new agent type. A new role template is justified when a
  composition recurs and needs a specialized prompt or toolset.

## 3. Execution backend abstraction

Rationale: [ADR-0004](adr/ADR-0004-execution-backend-abstraction.md).
Schema: [`schemas/execution-backend.schema.json`](../schemas/execution-backend.schema.json).

### Backend descriptor (what the router knows)

```
id, vendor, kind (cli_agent | api_model | human | local_model)
strengths: [capability ids]        ← evidence-based, updated from outcomes
context_window_tokens
supports: {tools, file_edit, shell, web, vision, worktree, headless}
cost_model: {unit, relative_cost}  ← relative tiers until real pricing is wired
limits: {max_runtime_s, concurrency}
trust: {data_policy_ok_for: [public, private, secret]}
status: declared | integrated | deprecated
```

### Adapter contract (what every integration must implement, OOS-0007)

```
prepare(run_spec)  → handle      # worktree, rendered context package, permissions
start(handle)      → run_id
poll(run_id)       → status      # running | succeeded | failed | timed_out | needs_input
collect(run_id)    → RunResult   # diff/commits, logs, artifacts, self-report, usage
cancel(run_id)
```

`RunResult.self_report` is stored, but it is **never** evidence of completion. The Verifier
collects evidence independently.

### Selection (Backend Router)

```
eligible = backends where status=integrated
                     ∧ supports ⊇ role.backend_requirements
                     ∧ context_window ≥ package size
                     ∧ trust.data_policy_ok_for ∋ project.data_class
choose argmax( fit(strengths, capabilities) − λ·relative_cost − μ·recent_failure_rate )
prefer a different backend than the producer for review stances
```

The scoring is a starting heuristic. It is calibrated from outcome data recorded per
(backend, capability, task type).

## 4. Initial registry contents (OOS-0001)

- **Capabilities:** the 14 listed in `orchestration/capabilities.json`. These are definitions only.
- **Backends:** `claude-code`, `codex` and `human` (Billy as a backend for tasks that need a
  human, such as acceptance testing). All have `status: declared`. **No integrations are built.**
