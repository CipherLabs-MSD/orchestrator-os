# orchestration/: kernel policy, profiles, backends

These files are the `trusted_policy` layer ([SECURITY_AND_TRUST](../docs/SECURITY_AND_TRUST.md)).
On the protected branch they are the only standing instructions the orchestrator follows,
together with the domain packages in [`domains/`](../domains/).
**Changing any of them is a D4 decision.** Kernel changes also require an ADR (invariant I-1).

| Path | Contents | Human-readable source |
|---|---|---|
| [kernel/decision_policy.json](kernel/decision_policy.json) | Levels D1–D4 + PROHIBITED, dimensions and scales, mapping, combination rules, **domain-independent** class floors, prohibitions, composition rules, kernel golden examples | [DECISION_ENGINE](../docs/DECISION_ENGINE.md) |
| [kernel/verification.json](kernel/verification.json) | Evidence base types, kernel gates (G-SCOPE, G-REVIEW, G-HUMAN, G-DOCS), kernel task types | [VERIFICATION](../docs/VERIFICATION.md) |
| [kernel/context_routing.json](kernel/context_routing.json) | Context scopes, always-include set, user-context relevance pipeline, control-plane categories | [CONTEXT_ROUTER](../docs/CONTEXT_ROUTER.md) |
| [profiles/software-development.json](profiles/software-development.json) | The Software Development Orchestrator: kernel + `software-development` + allowed backends | [DOMAIN_PACKAGES §3](../docs/DOMAIN_PACKAGES.md#3-profiles-configuration-over-a-common-kernel) |
| [owner_policy.json](owner_policy.json) | **Owner policy** (Billy, D4): private context store, escalation channels, Billy-only merge, AI provider data policy, 0 SEK spending, deferred choices | [ADR-0007](../docs/adr/ADR-0007-initial-owner-policy.md) |
| [backends.json](backends.json) | Execution backend (agent provider) registry. Domain-independent. All `declared`, none integrated. | [AGENT_MODEL §3](../docs/AGENT_MODEL.md#3-execution-backend-abstraction) |

`tools/validate.py` checks these files against `schemas/` and cross-checks them:

- **Kernel purity.** There is no domain vocabulary or project name in kernel JSON or schemas.
- **Tighten-only composition** for every domain package.
- **Golden examples.** Kernel and domain examples classify as documented, using one classifier.
- **Profiles.** A profile loads only operational domains and declared backends.
