# domains/: domain packages

Each subdirectory specializes the domain-agnostic kernel for one domain. The kernel
never contains domain behaviour (invariant I-1, [ARCHITECTURE §1.4](../docs/ARCHITECTURE.md#14-invariants)).
Contract and composition rules: [DOMAIN_PACKAGES](../docs/DOMAIN_PACKAGES.md). Decision: [ADR-0006](../docs/adr/ADR-0006-domain-agnostic-kernel.md).

| Package | Status | Operational | Notes |
|---|---|---|---|
| [software-development/](software-development/) | draft | yes | Capabilities, policy, gates, routing profiles, git workspace binding. Used by OOS itself. |
| [finance/](finance/) | illustrative | **no** | A sketch showing much stricter authority. No thresholds, no trading policy. No profile may load it. |

Domain policy (`policy.json`, `policy_sketch`) is `trusted_policy`. Changing it is D4.
Composition with the kernel is **tighten-only**, and `tools/validate.py` enforces that.
