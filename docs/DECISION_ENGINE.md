# Decision Engine

> The aim is maximum useful autonomy inside explicit boundaries. "Architecture means ask
> the human" is **not** the rule. Each decision is classified by what it could
> break, how hard it is to undo, and whether it stays inside Billy's stated intent.

The **kernel** owns the framework: levels, dimensions, generic floors, prohibitions and
composition. **Domain packages** add domain floors, rules and prohibitions. They can only
tighten ([DOMAIN_PACKAGES §4](DOMAIN_PACKAGES.md#4-composition-rules)). Every decision is
classified against the **composed** policy of the active orchestrator profile.

- Kernel policy: [`orchestration/kernel/decision_policy.json`](../orchestration/kernel/decision_policy.json)
- Software domain policy: [`domains/software-development/policy.json`](../domains/software-development/policy.json)
- Record format: [`schemas/decision-record.schema.json`](../schemas/decision-record.schema.json)

## 1. Authority levels

| Level | Name | The orchestrator may | Required record | Examples (software · finance sketch) |
|---|---|---|---|---|
| **D1** | Autonomous | Decide and act | Change log / run log | local refactor, bug fix · research, scenario calculation |
| **D2** | Autonomous + log | Decide and act | Decision log entry `DEC-NNNN` (context, options, choice, rationale, evidence) | library choice, internal API shape · *propose* a transaction |
| **D3** | Autonomous within constraints + ADR | Decide and act, **if** every D3 condition holds (§4) | ADR **before** the change integrates, plus a mention in Billy's digest | reversible architecture or data-model decision inside intent |
| **D4** | Human escalation | Prepare, **not** decide | Escalation record. Billy's answer is logged with `decided_by: billy`. | irreversible or destructive acts, real money, live external effects, vision changes, unclear intent · execute a transaction, change risk limits |
| **PROHIBITED** | Never permitted | Refuse and log | Refusal record (`status: refused`) | expose or transmit secrets or private keys, follow untrusted instructions, bypass the Policy Guard |

PROHIBITED differs from D4. A D4 asks Billy *"may I do this now?"* A prohibited action is
never asked about. Only a deliberate, reviewed policy change made outside any run can alter a
prohibition, and kernel prohibitions require a kernel ADR.

## 2. Scoring dimensions (kernel; domains calibrate units)

Every non-trivial decision is scored 0–3 on six dimensions.

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Impact** (blast radius) | single unit | one component | cross-component, shared interface, or persistent data | whole product, or external parties affected |
| **Reversibility** | trivially undone (software: revert) | undone with modest rework | costly to undo (migration, published interface, many dependents) | irreversible (data deleted, money spent, release published, message sent, trade executed) |
| **Uncertainty** | well understood | some unknowns | significant unknowns, weak evidence | cannot evaluate with available evidence |
| **Cost** | none | within the run budget | exceeds the task budget | real money, committed funds, or exceeds the project budget |
| **Security** | none | security-adjacent, covered by checks | credentials, permissions or protected data | changes trust boundaries or controls, credential or data exposure |
| **Vision alignment** | directly implements stated intent | a consistent reading of intent | requires choosing between plausible readings | contradicts or changes stated intent or requirements |

Domains calibrate what a level means in their units, for example `cost_calibration` in the
software policy. They may not reinterpret a dimension to make it more permissive.

## 3. From scores to level

```
level = max( dimension_mapping(scores),            # kernel, raised by domain overrides
             class_floor(decision_class),          # kernel ∪ domain floors
             combination_rules(scores) )           # kernel ∪ domain rules
if decision_class ∈ prohibited_classes  → PROHIBITED
if classifier confidence is low         → round UP one level
order: D1 < D2 < D3 < D4 < PROHIBITED
```

**Dimension mapping (kernel)**

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| impact | D1 | D1 | D3 | D3 |
| reversibility | D1 | D1 | D3 | **D4** |
| uncertainty | D1 | D1 | D2 | D3 + experiment first |
| cost | D1 | D1 | D2 | **D4** |
| security | D1 | D2 | D3 | **D4** |
| vision alignment | D1 | D2 | D3 | **D4** |

**Combination rules (kernel)**

- impact ≥ 2 **and** reversibility ≥ 2 → **D4**
- security ≥ 2 **and** uncertainty ≥ 2 → **D4**
- vision ≥ 2 **and** impact = 3 → **D4** (a product-wide reinterpretation of intent)

**Kernel class floors** (domain-independent)

| Decision class | Floor |
|---|---|
| `destructive_or_irreversible_change`: delete user data, destroy resources, rewrite published history | **D4** |
| `spend_money_or_allocate_funds`: spend, allocate or pledge funds, paid services, licences | **D4** |
| `live_external_effect`: act on live external systems (production, infrastructure, live transactions) | **D4** |
| `external_communication`: publish, send, post, speak for Billy | **D4** |
| `credential_handling`: rotate, provision or scope credentials | **D4** |
| `requirement_or_vision_change` | **D4** |
| **`oos_policy_or_authority_change`**: any kernel, domain or profile policy | **D4** |
| `reserved_for_billy`: anything the profile or project lists | **D4** |

**Kernel prohibitions:** `expose_or_transmit_secrets`, `follow_untrusted_instructions`, `bypass_policy_guard`.

**The system cannot raise its own authority.** Changing any policy, kernel or domain, is D4.

**Domain floors** live in packages. Software, for example: dependency change D2, API contract D2,
CI change D2, persistent schema D3, auth/crypto D3, new service D3, history rewrite D4,
production deploy D4, release D4, plus a prohibition on direct writes to a protected branch.
Finance (illustrative): see [DOMAIN_PACKAGES §5.1](DOMAIN_PACKAGES.md#51-finance-example-why-the-separation-matters-illustrative).

## 4. Conditions for autonomous D3

The orchestrator may take a D3 decision only if **all** of these hold. Otherwise it is D4.

1. It is inside an accepted product intent (no requirement or vision change).
2. It is reversible (reversibility ≤ 2) and a rollback path is written in the ADR.
3. No hard constraint or requirement is in conflict.
4. Options were compared. The ADR lists at least two alternatives and why each was rejected.
5. Where uncertainty ≥ 2, a time-boxed spike or experiment produced evidence first.
6. It does not contradict an accepted ADR (superseding one is allowed with justification, but
   superseding a D4-decided ADR is D4).

## 5. Escalation (D4)

An escalation is a **decision package**, not a vague question:

```
ESC-NNNN
  question:          one sentence
  why_escalated:     which rule fired (e.g. "reversibility=3: deletes existing user records")
  options:           2–4, each with consequences
  recommendation:    the orchestrator's pick + rationale
  evidence:          EVD/DEC/ADR/CTX references
  blocked:           task IDs that wait on this
  continues:         what proceeds meanwhile
  cost_of_waiting:   what delay costs
  default_if_silent: none (D4 never auto-resolves), or a safe holding action
```

While a D4 is open, the orchestrator **keeps working** on unblocked parts of the graph. It
may run cheap, reversible spikes that inform the decision. It never commits to an option.

**Channel (owner policy, ADR-0007):** initially Billy in the active Orchestrator session. Other
channels (notifications, digests, email, messaging, dashboards) can be added later as entries in
`owner_policy.escalation.channels`. When digests exist, escalations are batched, and an interrupt is reserved for blocking or
time-critical items (see `context/WORKING_STYLE.md` once populated). Domains may add
escalation rules, for example "always interrupt for any live-effect proposal".

## 6. Integration authority is separate from decision authority

Deciding something autonomously is different from integrating it into canonical state
(kernel interface `Integration`; software binding: merging to the protected branch).

| Phase | Who integrates |
|---|---|
| Initial (**in force**, ADR-0007) | Billy only. Agents may prepare, push permitted branches, open PRs and recommend merge when a task authorizes it, but never merge. |
| Earned (per project; only after an explicit owner decision) | Orchestrator may integrate D1/D2 changes whose gates pass. D3 needs Billy's approval or a review window. |

Software binding: [GIT_WORKFLOW](../domains/software-development/GIT_WORKFLOW.md).

## 7. User preferences in decisions

User context entries are **evidence** with a computed weight
([PERSONAL_CONTEXT_MODEL §3](PERSONAL_CONTEXT_MODEL.md#effective-weight-used-by-the-decision-engine)).
A decision record cites them (`evidence: [CTX-0004]`). A preference can tip a choice
between otherwise comparable options. It cannot override a requirement, constraint or
accepted ADR. It never changes the D-level.

## 8. Worked classifications

Golden examples live with the policy they exercise. The validator classifies each one with
the same kernel classifier over the composed policy.

| Decision | Policy | Scores (I/R/U/C/S/V) | Dominant rule | Level |
|---|---|---|---|---|
| Routine reversible work | kernel | 0/0/0/0/0/0 | — | D1 |
| Cross-component and costly to reverse | kernel | 2/2/0/0/0/0 | impact≥2 ∧ reversibility≥2 | **D4** |
| Send a credential to a third party | kernel | any | prohibition | **PROHIBITED** |
| Choose a date library | software | 1/1/1/0/0/0 | floor: dependency | D2 |
| File saves → SQLite (no user data yet) | software | 2/1/1/0/0/1 | impact 2; schema floor | D3 |
| Same, but existing user saves must migrate | software | 2/2/1/0/0/1 | impact≥2 ∧ reversibility≥2 | **D4** |
| Add OAuth login | software | 2/1/2/0/2/1 | security≥2 ∧ uncertainty≥2 | **D4** |
| Drop a core feature to hit a milestone | software | 3/1/0/0/0/3 | vision 3 | **D4** |
| Propose a transaction for review | finance (illustrative) | 1/0/1/0/0/0 | finance floor D2 | D2 |
| Change risk limits | finance (illustrative) | 2/1/0/0/0/1 | finance floor D4 | **D4** |
| Send a private key to a service | finance (illustrative) | any | finance prohibition | **PROHIBITED** |

## 9. Calibration

These thresholds are hypotheses. OOS-0005 implements the classifier with the golden
examples as tests. During pilots, every escalation Billy answers with "you could have
decided that" (or "you should have asked") becomes a calibration data point in
`memory/LEARNINGS.md`. Calibration is per domain, because escalation precision in software
says little about finance. Changing any policy is itself D4.
