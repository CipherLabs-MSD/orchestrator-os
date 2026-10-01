# orchestration/: machine-readable policy and registries

These files are the `trusted_policy` layer ([SECURITY_AND_TRUST](../docs/SECURITY_AND_TRUST.md)).
On the protected branch they are the only standing instructions the orchestrator follows.
**Changing them is a D4 decision.**

| File | Contents | Human-readable source |
|---|---|---|
| [decision_policy.json](decision_policy.json) | D-levels, scoring mappings, combination rules, class floors, golden examples | [DECISION_ENGINE](../docs/DECISION_ENGINE.md) |
| [capabilities.json](capabilities.json) | Capability registry (descriptive, grants nothing) | [AGENT_MODEL](../docs/AGENT_MODEL.md) |
| [backends.json](backends.json) | Execution backend registry (all `declared`, none integrated) | [AGENT_MODEL §3](../docs/AGENT_MODEL.md#3-execution-backend-abstraction) |
| [verification_gates.json](verification_gates.json) | Gates and task-type requirements | [VERIFICATION](../docs/VERIFICATION.md) |
| [context_routing.json](context_routing.json) | Per-profile context selection rules | [CONTEXT_ROUTER](../docs/CONTEXT_ROUTER.md) |

`tools/validate.py` checks these files against `schemas/`, and cross-checks them. For example,
every capability's `context_profile` must exist and every referenced gate must be defined.
The golden examples must also classify as documented.
