# ADR-0006 — One domain-agnostic kernel plus domain specialization

- **Status:** accepted · owner-accepted 2026-10-01 (DEC-0004)
- **Date:** 2026-10-01
- **Decision level:** D3 (founding architecture, within the vision Billy stated in the OOS-0001 addendum)
- **Decided by:** orchestrator (founding architect, OOS-0001 addendum), at Billy's direction
- **Task:** OOS-0001
- **Amends:** ADR-0002 (adds the domain-context layer), ADR-0003 (adds the PROHIBITED tier and action-class mapping for tools), ADR-0004 (adds routing factors and non-CLI backend kinds), ADR-0005 (evidence binds to an artifact version, not specifically a commit SHA)

## Context

Billy intends Orchestrator OS to power more than software development. Planned and
plausible specializations include Software Development, Finance, Game Development, Research and
Creative Production. FinanceOS (a future finance project and candidate domain) is the motivating example. It needs the same long-running
plan → delegate → verify → learn loop, under far stricter authority: research is
autonomous, executing transactions is tightly controlled, and exposing keys is never allowed.

The initial OOS-0001 design was nominally general, but an audit found that software
assumptions had leaked into what was meant to be the core:

- All 14 capabilities, the gate set (tests, builds, migrations) and the task types were software-only.
- Decision class floors such as "dependency change" and "CI change" sat in the generic Decision Engine.
- The evidence and context schemas assumed git (`commit_sha`, `built_at_sha`, `implementing_commits`, `worktree`).
- Project memory assumed every project is a repository.
- There was no way for a domain to *tighten* risk policy, and no tier for actions that are never permitted.

## Decision

Orchestrator OS is **one domain-agnostic kernel**. Specialized orchestrators are
**profiles**: the kernel composed with **domain packages** and tighten-only overrides.

- The kernel owns mechanisms and domain-independent policy: `orchestration/kernel/`, `schemas/` and the design docs.
- Domain packages (`domains/<id>/`) own capabilities, domain policy, gates and evidence
  types, task types, context profiles, the user-context ceiling, memory record types, declared tools,
  and the **workspace binding** that maps kernel interfaces (`ProjectStore`, `Workspace`,
  `ChangeSet`, `ArtifactVersion`, `Integration`) onto real systems.
- Profiles (`orchestration/profiles/<id>.json`) select domains and allowed backends.
- Composition is **tighten-only**. Kernel floors and prohibitions cannot be loosened by any configuration.
- A **PROHIBITED** tier sits above D4.
- **Invariant I-1:** domain-specific assumptions must not be introduced into the kernel unless
  they represent a genuinely domain-independent orchestration capability and are justified by an ADR.

## Rationale

- The hard parts are the same in every domain: planning under uncertainty, delegation,
  evidence, authority, memory and escalation. Re-implementing them per domain multiplies bugs,
  and safety bugs most of all.
- Safety properties (capability ≠ authority, evidence gating, prohibitions) are only as good as
  their weakest copy. One kernel means one place to get them right, and one place to audit.
- Data-driven specialization lets a future factory *generate* specializations (OOS-0019).
  Code forks cannot be generated safely.
- Experience transfers: a calibration learned in one domain (for example escalation precision)
  improves the kernel for all of them.

## Alternatives considered

1. **Separate orchestrator codebases per domain** (a FinanceOS orchestrator, a software orchestrator, …).
   Each can be tuned freely. But the duplicated loops drift, and every safety fix must be repeated
   N times, with N different audits. Rejected.
2. **One kernel with domain logic in `if domain == …` branches.** Fast at first, but it is exactly the
   contamination I-1 forbids, and it grows unboundedly. Rejected.
3. **Plugins with arbitrary code hooks into the kernel.** Flexible, but plugins could bypass
   authority, and a factory cannot safely generate code. Deferred: code-level extension
   points may be added later through an ADR, and only behind the same Policy Guard.
4. **Kernel + declarative domain packages + profiles, composed tighten-only.** Chosen.

## Consequences

- The software config moved out of the kernel into `domains/software-development/`. The git
  workflow became that domain's workspace binding.
- Kernel records use neutral terms: `artifact_version`, `implementing_changes`, `resource_scope`,
  `isolated_workspace`. Evidence has kernel base types plus domain types.
- The Context Router gains a domain layer and a per-domain user-context ceiling.
- The Decision Engine classifies against a *composed* policy. Golden examples exist per domain,
  and the same classifier runs over both kernel and domain examples.
- A domain-package loader is needed (OOS-0018) before the Decision Engine, Context Router and
  Verifier can load real policy.
- More indirection: contributors must ask "kernel or domain?" for every concept. AGENTS.md makes
  this a review duty.

## Risks

| Risk | Mitigation |
|---|---|
| Premature abstraction: designing for domains that never arrive | Only one operational package. Finance is an illustrative sketch. A second real domain is planned only after the pilot (OOS-0020). |
| Leaky abstraction: a domain needs behaviour the kernel cannot express | Add a *general* mechanism via ADR (I-1), never a domain branch |
| Kernel contamination by gradual drift | The validator scans kernel JSON and schemas for domain vocabulary and project names. AGENTS.md makes reviewers flag violations. |
| Composition bugs that loosen policy | Tighten-only rules are enforced by the validator now and by the loader (OOS-0018) later. Golden examples per domain. |
| Illustrative finance sketch mistaken for operating policy | `operational: false`, no thresholds, and profiles cannot load it (validator) |

## Examples

| Kernel | Domain specialization |
|---|---|
| `VerificationRequirement` (gate) | finance: `PortfolioRiskVerification` · software: `G-TEST` |
| `Capability` | software: `testing` (task: run unit tests) |
| `AuthorityPolicy` | finance: `TransactionApprovalPolicy` |
| `Evidence` (base `human_acceptance`) | game development: `HumanPlaytestEvidence` |

## Rollback

If only one domain ever exists, the indirection costs some ceremony and nothing more.
Collapsing back means inlining one package. The reverse, extracting a kernel from a
software-shaped codebase later, would be far more expensive. That asymmetry is why this is decided now.

## Revisit when

- A second operational domain needs a kernel change. Test whether it is genuinely general.
- Composition rules block a legitimate need that cannot be expressed by tightening.
