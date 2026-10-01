# Domain Packages, Profiles and Specialized Orchestrators

> Canonical principle: [ARCHITECTURE §1](ARCHITECTURE.md#1-core-architectural-principle-domain-specialized-orchestration).
> Decision: [ADR-0006](adr/ADR-0006-domain-agnostic-kernel.md).
> This document defines the **contract**. Only the software-development package has
> real content. The finance package is an illustrative sketch.

## 1. Vocabulary

| Term | Meaning | Where |
|---|---|---|
| **Kernel** | Domain-agnostic orchestration mechanisms and policy | `orchestration/kernel/`, `schemas/`, `docs/` |
| **Domain package** | Specialization data for one domain | `domains/<id>/` |
| **Orchestrator profile** | Kernel + one or more operational domain packages + allowed backends + tighten-only overrides | `orchestration/profiles/<id>.json` |
| **Specialized orchestrator** | A running instance of the kernel loaded with a profile | (runtime, from OOS-0010 on) |

## 2. Package anatomy

```
domains/<id>/
  domain.json            manifest (schemas/domain-package.schema.json)
  capabilities.json      capabilities (schemas/capability.schema.json); ids local to the domain
  policy.json            extra class floors, combination rules, prohibitions, cost calibration, golden examples
  verification.json      gates, specialized evidence types (each extends a kernel base type), task types
  context_routing.json   capability profiles + user_context_ceiling
  <binding doc>.md       workspace binding: how ProjectStore / Workspace / ChangeSet / ArtifactVersion map to real systems
  README.md
```

| Manifest `status` | `operational` | Meaning |
|---|---|---|
| `illustrative` | false | Teaching sketch. It can never be loaded by a profile. |
| `draft` | true | Usable for sandbox and own-project work. Under active design. |
| `active` | true | Accepted for real projects (accepting a package is D4) |
| `deprecated` | false | Kept for history |

Present packages:

| Package | Status | Purpose |
|---|---|---|
| [`software-development`](../domains/software-development/) | draft, operational | Everything software-specific that used to sit in the kernel. Used by OOS itself. |
| [`finance`](../domains/finance/) | illustrative, **not** operational | Demonstrates a domain with much stricter authority. It has no thresholds and no trading policy. |

## 3. Profiles: configuration over a common kernel

```
Orchestrator OS kernel
      ↓ + domain definition       (domain.json)
      ↓ + capabilities            (capabilities.json)
      ↓ + policies                (policy.json, composed tighten-only)
      ↓ + context rules           (context_routing.json, ceiling ∩ profile)
      ↓ + memory schema           (memory_record_types)
      ↓ + verification rules      (verification.json)
      ↓ + authority rules         (floors, prohibitions, reserved_for_billy)
      ↓ + tool access             (tools_declared → ToolAdapters, each action mapped to a class)
      ↓ + allowed backends        (profile.backends_allowed)
      = specialized orchestrator  (orchestration/profiles/<id>.json)
```

The present profile is [`software-development.json`](../orchestration/profiles/software-development.json).
It is the one OOS uses to build itself. A profile names **no** model vendor as identity.
`backends_allowed` is a permission list, and the Backend Router still chooses per task.

## 4. Composition rules

The kernel composes `kernel ⊕ domain(s) ⊕ profile ⊕ project` with these rules. The
validator enforces them for every domain package.

| Element | Rule |
|---|---|
| Decision levels | Order D1 < D2 < D3 < D4 < PROHIBITED. Composition takes the **max**. |
| Dimension mapping | A domain override must be ≥ the kernel cell by cell |
| Class floors | Domains add new classes. A class the kernel defines may only be **raised**. A domain class that `specializes` a kernel class is ≥ that class. |
| Combination rules | Add only |
| Prohibitions | Add only. Nothing may remove or downgrade a prohibition. |
| Gates | Domains add gates. Kernel gates keep their meaning. Implicit gates (G-SCOPE) always apply. |
| Evidence types | Domains declare `<name>: <kernel base type>`. Evidence records carry the base `type` plus `domain_type`. |
| Capabilities | Ids are local to a domain. Across domains, qualify them as `<domain>/<id>`. A profile that loads two domains with colliding ids must use qualified ids. |
| User context | A domain declares a `user_context_ceiling`. A capability profile may allow only categories inside it. The relevance pipeline runs after both. |
| Multiple domains in one profile | When two domains disagree, the stricter level wins. Conflicting *requirements* are D4. |
| Project overrides | Tighten freely. Loosening a domain floor for one project is D4 and logged. Kernel floors and prohibitions can never be loosened by configuration. |

## 5. Worked examples

### 5.1 Finance example: why the separation matters (illustrative)

*FinanceOS is the motivating project. It is not modified or implemented.*

FinanceOS, a future finance project and candidate domain, motivates this example. A future **Finance Orchestrator**
would run the *same* kernel loop as the Software Development Orchestrator: plan, delegate,
verify, learn and replan, across many cycles. It would do so under a very different authority
profile. The sketch in [`domains/finance/domain.json`](../domains/finance/domain.json)
encodes this shape. It sets no thresholds and no trading rules.

| Action | Illustrative authority | Where the rule lives |
|---|---|---|
| Research | autonomous (D1) | finance policy sketch |
| Read portfolio | autonomous (D1) **only with** a data-access grant | finance precondition + kernel authority |
| Calculate scenarios | autonomous (D1) | finance |
| Generate investment hypothesis | autonomous (D1); it is an `experimental_hypothesis` claim, never an instruction | finance + kernel taxonomy |
| Propose transaction | autonomous + log (D2) | finance |
| Prepare transaction | policy-controlled; D4 until Billy defines a `TransactionApprovalPolicy` | finance |
| Execute transaction | strict: D4 (and `live_external_effect` in the kernel is already D4) | kernel floor, raised/named by finance |
| Large transaction | human approval. Any size threshold is **Billy's** D4 decision and deliberately undefined. | future finance policy |
| Change risk limits | human approval (D4); it specializes `oos_policy_or_authority_change` | kernel + finance |
| Expose or transmit private keys | **PROHIBITED**. The kernel already prohibits `expose_or_transmit_secrets`. Finance names wallet keys explicitly. | kernel + finance |

What the kernel provides unchanged: the loop, task graph, D-level framework, PROHIBITED
tier, tighten-only composition, Policy Guard, evidence gating, escalation and audit. What the
finance package adds: capabilities, action classes, preconditions, finance evidence types
(for example `portfolio_risk_check`), a user-context ceiling (`decision_preference` and
`working_style` only, so no creative context), and later its workspace binding and thresholds.

The validator classifies the sketch's golden examples with the **same** kernel classifier
that classifies software decisions. That proves that the stricter behaviour comes from data,
not from finance-aware kernel code.

**The lesson is CAPABILITY ≠ AUTHORITY.** An agent that *can* call a broker API is not
thereby *permitted* to place an order. That rule lives in the kernel ([SECURITY_AND_TRUST §2](SECURITY_AND_TRUST.md#2-capability-vs-authority)),
so it applies to every domain. Finance merely makes it vivid.

### 5.2 One user preference, four context scopes (hypothetical)

> Hypothetical user context: *"Billy may prefer dark, occult, symbolic, mythological design."*
> In the addendum it is offered as an example only. It is **not** recorded as a context entry,
> because entries enter only via [IMPORT_PROTOCOL](../context/IMPORT_PROTOCOL.md).

| Scope | What happens |
|---|---|
| **User** | Stored once as `kind: user_preference`, `category: creative`, `scope: global` (or `domain:game-development`), with provenance. |
| **Domain** | The software-development ceiling allows `creative`. The finance ceiling does **not**, so the entry can never reach a finance agent. |
| **Project** | Demon Codex might, *after an explicit project decision*, adopt "infernal manuscript / black-forge visual language" as a `project_preference` or `project_requirement`. That claim is owned by the project and cites the CTX entry as evidence. Another creative product might weigh the same preference at lower strength for branding. |
| **Task** | A Demon Codex UI/naming task (profile `creative_engineering`) receives the project claim and possibly the CTX entry. A database-migration task in the same project receives neither. A FinanceOS portfolio-calculation task receives neither. |

User preference ≠ project requirement. The router decides relevance *before*
anything propagates. The project decision, not the preference, binds.

### 5.3 Other kinds, same discipline

| Statement | Kind | Owner |
|---|---|---|
| "Do not expose private keys." | hard constraint (kernel prohibition) | kernel / domain |
| "Players may prefer shorter matches." | experimental hypothesis. Test it before building on it. | project |
| "Software projects default to small PRs." | domain default (the project may override it with a logged reason) | domain |

## 6. Future: the Orchestrator Factory

**Preserved capability, not built (OOS-0019).** Given a request such as *"Build an
orchestrator for FinanceOS"*, a future OOS would:

1. inspect the project (read-only)
2. identify domain capabilities
3. identify data sources and their trust levels
4. identify the risk model
5. define agent capabilities
6. define authority boundaries, starting **maximally restrictive**
7. define verification requirements and evidence types
8. define context routing and the user-context ceiling
9. define domain memory record types
10. generate a domain package (status `draft`, `operational: false`) and a profile
11. validate them (schemas, tighten-only composition, golden examples)
12. request Billy's approval for every high-impact authority rule (D4) before `operational: true`

Guardrails: the factory is itself a kernel workflow under kernel policy. It cannot generate
rules looser than the kernel. Generating or activating authority policy is
`oos_policy_or_authority_change` (D4). Its output is a reviewable change set, like any other.
The schemas, the composition rules and the validator built in OOS-0001 are what make step 11
possible.

## 7. Adding a domain package (procedure)

1. Create `domains/<id>/domain.json` with `status: illustrative` or `draft`.
2. Add components and the workspace binding. Map every declared tool action to an action class.
3. Run `python tools/validate.py`. It checks the schema, references and tighten-only composition, and classifies the golden examples.
4. Write an ADR if the package needs a *kernel* change. That is allowed only if the change is genuinely domain-independent (invariant I-1).
5. Activating a package (`active`) and creating a profile for real projects are D4.
