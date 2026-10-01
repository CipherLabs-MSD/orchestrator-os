# Verification

> **No task becomes DONE because an agent says it is done.**
> Rationale: [ADR-0005](adr/ADR-0005-evidence-gated-completion.md), as amended by [ADR-0006](adr/ADR-0006-domain-agnostic-kernel.md).

The **kernel** owns the verification framework: principles, evidence base types, kernel
gates, verdicts and binding to an artifact version. **Domain packages** add gates, specialized
evidence types and task types. Every domain needs different proof. A software change needs
tests, a finance analysis needs risk checks and data provenance, and game feel needs a human playtest.

- Kernel: [`orchestration/kernel/verification.json`](../orchestration/kernel/verification.json)
- Software domain: [`domains/software-development/verification.json`](../domains/software-development/verification.json)

## 1. Principles

1. **Evidence, not assertion.** Completion is a gate verdict over collected evidence.
2. **Independent collection.** The Verifier re-runs checks itself, or reads artifacts the
   Dispatcher captured. It does not rely on the producing agent's transcript.
3. **Bound to an artifact version.** Evidence is valid only for the exact `ArtifactVersion` being
   accepted (software binding: the commit SHA). A new version makes it stale.
4. **Type-appropriate.** Different task types need different proof. Requirements come from the
   composed task-type table (kernel + the profile's domains).
5. **Separation of duties.** A review stance is never the producer.

## 2. Evidence: kernel base types, domain specializations

Schema: [`schemas/evidence.schema.json`](../schemas/evidence.schema.json). Every record has a
kernel `type`, and optionally a `domain_type` (`<domain>/<name>`) that the domain declares as
extending that base.

| Kernel base type | Captured as | Software specializations | Finance sketch | Game dev (future) |
|---|---|---|---|---|
| `check_result` | procedure, exit status, log | `test_result`, `build_output`, `static_analysis`, `runtime_check` | `portfolio_risk_check` | — |
| `artifact` | artifact + what it should show | `screenshot` | — | — |
| `measurement` | metric, baseline, threshold | `benchmark` | `scenario_result` | frame-time capture |
| `review` | reviewer role, backend, findings, verdict | code/security review | — | — |
| `human_acceptance` | Billy's verdict + date | — | — | `HumanPlaytestEvidence` |
| `external` | reference + retrieval time + trust label | — | `data_source_provenance` | — |
| `scope_inspection` | what changed vs. declared resource scope | `diff_inspection` | — | — |
| `observation` | recorded system/world state, source, time | — | — | — |

## 3. Kernel gates

| Gate | Passes when |
|---|---|
| `G-SCOPE` | Changes touch only the declared resource scope. No secrets exposed. No protected resources changed. **Implicit in every gate set, in every domain.** |
| `G-REVIEW` | An independent review stance approves, with findings addressed or explicitly waived (and the waiver logged) |
| `G-HUMAN` | Billy accepts |
| `G-DOCS` | Artifact validators pass. Internal references resolve. Review confirms the content addresses the task. |

Domain gates, for example software's G-TEST, G-BUILD, G-STATIC, G-RUNTIME, G-VISUAL, G-BENCH,
G-MIGRATION and G-SECURITY, are listed in each package
([software](../domains/software-development/README.md#task-type--required-gates-plus-kernel-g-scope)).

## 4. Task types

Kernel task types apply in every domain:

| Task type | Required gates (plus G-SCOPE) |
|---|---|
| documentation | G-DOCS |
| design | G-DOCS, G-REVIEW |
| spike / experiment | evidence of the *finding* (positive or negative) plus a recorded conclusion. Not production gates. |
| outcome_validation | as defined on the OUTCOME's VALIDATION node. Often G-HUMAN. |

Domains add their own (software: bug_fix, feature_backend, feature_ui, refactor, migration,
security_sensitive, performance). A project may add gates. Removing a required gate for a
task type is D3. Removing G-SCOPE, or any gate whose `removal_level` is D4, is D4.

## 5. Verdicts

```
GateVerdict { gate, task_id, artifact_version, verdict: pass|fail|inconclusive, evidence:[EVD…], notes }
```

- `inconclusive` (for example a flaky check or a missing tool) is **not** pass. It goes back to the
  Planner as a verification-infrastructure problem.
- A `fail` returns the task to `ready` with the findings attached and increments the attempt count.

## 6. Verifying this repository (OOS-0001)

Profile: software-development. Gate set: **G-DOCS + G-SCOPE**.

```sh
python tools/validate.py
python -m unittest discover tests
```

`G-REVIEW` and `G-HUMAN` for OOS-0001 come from Billy reviewing the branch.
