# Architecture Decision Records

ADRs record **D3** decisions (taken autonomously within constraints) and the outcomes of
**D4** decisions (taken by Billy). D2 decisions go to `memory/DECISIONS/` instead.
See [DECISION_ENGINE](../DECISION_ENGINE.md).

ADRs are append-only. To change a decision, write a new ADR that supersedes the old one,
and update the old ADR's status line only. Purely editorial repairs, such as fixing a broken link, are allowed
and never change the decision text.

| ADR | Title | Status | Level |
|---|---|---|---|
| [ADR-0001](ADR-0001-files-first-git-backed-state.md) | Files-first, git-backed durable state | accepted | D3 |
| [ADR-0002](ADR-0002-four-layer-knowledge-separation.md) | Four-layer knowledge separation | accepted | D3 |
| [ADR-0003](ADR-0003-authority-separate-from-capability.md) | Authority separate from capability | accepted | D3 |
| [ADR-0004](ADR-0004-execution-backend-abstraction.md) | Vendor-neutral execution backend abstraction | accepted | D3 |
| [ADR-0005](ADR-0005-evidence-gated-completion.md) | Evidence-gated completion | accepted | D3 |
| [ADR-0006](ADR-0006-domain-agnostic-kernel.md) | One domain-agnostic kernel plus domain specialization | accepted (amends 0002–0005) | D3 |

Template: [TEMPLATE.md](TEMPLATE.md).

> These six were accepted as founding decisions in OOS-0001. They are reversible
> design commitments and stay subject to Billy's review of the OOS-0001 branch.
