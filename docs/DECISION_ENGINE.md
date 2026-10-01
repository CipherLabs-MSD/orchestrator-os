# Decision Engine

> The aim is maximum useful autonomy inside explicit boundaries. "Architecture means ask
> the human" is **not** the rule. Each decision is classified by what it could
> break, how hard it is to undo, and whether it stays inside Billy's stated intent.

Machine-readable policy: [`orchestration/decision_policy.json`](../orchestration/decision_policy.json).
Record format: [`schemas/decision-record.schema.json`](../schemas/decision-record.schema.json).

## 1. Authority levels

| Level | Name | The orchestrator may | Required record | Examples |
|---|---|---|---|---|
| **D1** | Autonomous | Decide and act | Commit message / run log | Implementation details, local refactors, tests, bug fixes inside an existing design |
| **D2** | Autonomous + log | Decide and act | Decision log entry `DEC-NNNN` (context, options, choice, rationale, evidence) | Library choice, internal API shape, reversible technical choices, test strategy |
| **D3** | Autonomous within constraints + ADR | Decide and act, **if** every D3 condition holds (§4) | ADR (accepted by the orchestrator) **before** the change integrates, plus a mention in Billy's digest | Meaningful architecture or data-model decisions that are reversible and inside established product intent |
| **D4** | Human escalation | Prepare, **not** decide | Escalation record. Billy's answer is logged as a decision with `decided_by: billy`. | Irreversible or destructive actions, substantial cost, security-sensitive actions, product or vision changes, unclear intent, reserved decisions |

## 2. Scoring dimensions

Every non-trivial decision is scored 0–3 on six dimensions.

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Impact** (blast radius) | single function/file | one module | cross-component, public interface, or data model | product-wide, user-visible, or external parties affected |
| **Reversibility** | `git revert` | revert + modest rework | costly to reverse (data migration, published API, many dependents) | irreversible (data deleted, money spent, release published, message sent) |
| **Uncertainty** (technical) | well understood | some unknowns | significant unknowns, weak evidence | cannot evaluate with available evidence |
| **Cost** | none | within the run budget | exceeds the task budget, within the project budget | real money, or exceeds the project budget |
| **Security** | none | security-adjacent, covered by tests | auth, crypto, secrets handling, permissions | changes trust boundaries or security controls, credential or data exposure |
| **Vision alignment** | directly implements stated intent | a consistent reading of intent | requires choosing between plausible readings of intent | contradicts or changes stated intent or requirements |

## 3. From scores to level

```
level = max( dimension_mapping(scores),
             class_floor(decision_class),
             combination_rules(scores) )
then: if classifier confidence is low → round UP one level
```

**Dimension mapping**

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| impact | D1 | D1 | D3 | D3 |
| reversibility | D1 | D1 | D3 | **D4** |
| uncertainty | D1 | D1 | D2 | D3 + experiment first |
| cost | D1 | D1 | D2 | **D4** |
| security | D1 | D2 | D3 | **D4** |
| vision alignment | D1 | D2 | D3 | **D4** |

**Combination rules** (they catch decisions that are risky in combination)

- impact ≥ 2 **and** reversibility ≥ 2 → **D4**
- security ≥ 2 **and** uncertainty ≥ 2 → **D4**
- vision ≥ 2 **and** impact = 3 → **D4** (a product-wide reinterpretation of intent)

**Class floors** (minimum level regardless of score)

| Decision class | Floor |
|---|---|
| add or replace a runtime dependency | D2 |
| change a public or internal API contract | D2 |
| change CI/CD pipeline | D2 |
| change a persistent data schema | D3 |
| change auth, authorization or crypto | D3 |
| introduce a new service, process or datastore | D3 |
| delete user data · destructive migration · force-push · rewrite published history | **D4** |
| spend money · new paid service · license change | **D4** |
| deploy to production · create or destroy real infrastructure | **D4** |
| external communication (publish, email, post, open public issue) | **D4** |
| change a project requirement, hard constraint or product vision | **D4** |
| **change Orchestrator OS's own policy, authority or security config** | **D4** |
| anything listed in the project's `reserved_for_billy` | **D4** |

The last two rows matter. **The system cannot raise its own authority.**

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
  why_escalated:     which rule fired (e.g. "reversibility=3: drops table `saves`")
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

Escalations are batched into a digest. An interrupt is reserved for blocking or
time-critical items (see `context/WORKING_STYLE.md` once populated).

## 6. Integration authority is separate from decision authority

Deciding something autonomously is different from merging it to the protected branch.

| Phase | Who merges to `main` |
|---|---|
| Initial (default) | Billy only, via PR |
| Earned (per project, granted by Billy as a D4 decision) | Orchestrator may auto-merge D1/D2 changes whose gates pass. D3 needs Billy's approval or a review window. |

See [GIT_WORKFLOW.md](GIT_WORKFLOW.md).

## 7. User preferences in decisions

User context entries are **evidence** with a computed weight
([PERSONAL_CONTEXT_MODEL §3](PERSONAL_CONTEXT_MODEL.md#effective-weight-used-by-the-decision-engine)).
A decision record cites them (`evidence: [CTX-0004]`). A preference can tip a choice
between otherwise comparable options. It cannot override a requirement, constraint or
accepted ADR. It never changes the D-level.

## 8. Worked classifications

| Decision | Scores (I/R/U/C/S/V) | Rule that dominates | Level |
|---|---|---|---|
| Rename a private helper | 0/0/0/0/0/0 | — | D1 |
| Fix off-by-one with a regression test | 0/0/0/0/0/0 | — | D1 |
| Choose a date library | 1/1/1/0/0/0 | class floor: dependency | D2 |
| Shape a new internal service interface | 1/1/1/0/0/1 | vision 1 → D2 | D2 |
| Move from file-based saves to SQLite (no user data yet) | 2/1/1/0/0/1 | impact 2 → D3; schema floor D3 | D3 |
| Same, but existing user saves must migrate | 2/2/1/0/0/1 | impact≥2 ∧ reversibility≥2 | **D4** |
| Add OAuth login | 2/1/2/0/2/1 | security≥2 ∧ uncertainty≥2 | **D4** |
| Drop multiplayer to hit a milestone | 3/1/0/0/0/3 | vision 3 | **D4** |
| Subscribe to a paid API tier | 1/1/0/3/0/1 | cost 3 | **D4** |

## 9. Calibration

These thresholds are hypotheses. OOS-0005 implements the classifier with the table above
as golden tests. During pilots, every escalation Billy answers with "you could have
decided that" (or "you should have asked") becomes a calibration data point in
`memory/LEARNINGS.md`. Changing the policy is itself D4.
