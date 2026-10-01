# Verification

> **No task becomes DONE because an agent says it is done.**
> Rationale: [ADR-0005](adr/ADR-0005-evidence-gated-completion.md).

## 1. Principles

1. **Evidence, not assertion.** Completion is a gate verdict over collected evidence.
2. **Independent collection.** The Verifier re-runs checks itself, or reads artifacts the
   Dispatcher captured. It does not rely on the producing agent's transcript.
3. **Bound to a commit.** Evidence is valid only for the exact commit SHA being accepted.
   New commits make it stale.
4. **Type-appropriate.** Different task types need different proof. A UI change without a
   visual check is not verified, and neither is a migration without a dry run.
5. **Separation of duties.** A review stance is never the producer.

## 2. Evidence types

Schema: [`schemas/evidence.schema.json`](../schemas/evidence.schema.json).

| Type | Captured as | Typical source |
|---|---|---|
| `test_result` | command, exit code, pass/fail counts, log artifact | test runner |
| `build_output` | command, exit code, artifact hashes | build system |
| `static_analysis` | tool, rule set, findings count by severity | linters, type checkers, SAST |
| `runtime_check` | scripted interaction, expected vs. observed | app launch, smoke script, API probe |
| `screenshot` | image artifact + what it should show + reviewer verdict | UI/visual tasks |
| `benchmark` | metric, baseline, observed, threshold | performance work |
| `review` | reviewer role, backend, findings, verdict | code/security/design review |
| `human_acceptance` | Billy's verdict + date | G-HUMAN gates |
| `external` | URL or reference + retrieval time + trust label | third-party confirmation (untrusted by default) |
| `diff_inspection` | files touched vs. declared write scope | Policy Guard, always collected |

## 3. Verification gates

Machine-readable: [`orchestration/verification_gates.json`](../orchestration/verification_gates.json).

| Gate | Passes when |
|---|---|
| `G-SCOPE` | Diff touches only the declared write scope. No secrets detected. No protected paths changed. **Implicit in every gate set.** |
| `G-TEST` | Relevant tests pass at the commit. New behaviour has new tests. No previously passing test now fails. |
| `G-BUILD` | Clean build from the commit |
| `G-STATIC` | No new findings at or above the configured severity |
| `G-REVIEW` | An independent review stance approves, with findings addressed or explicitly waived (and the waiver logged) |
| `G-RUNTIME` | Scripted runtime check passes |
| `G-VISUAL` | Screenshot(s) match the stated expectation (reviewed by a vision-capable role or by Billy) |
| `G-BENCH` | Metric is within threshold of the baseline |
| `G-MIGRATION` | Dry run on a copy succeeds. Rollback was tested. Data counts and checksums are reconciled. |
| `G-SECURITY` | Security review passes. Dependency audit is clean at the threshold. |
| `G-HUMAN` | Billy accepts |
| `G-DOCS` | Validator passes. Internal links resolve. Review stance confirms the content addresses the task. |

## 4. Task type → required gates

| Task type | Required gates (plus G-SCOPE) |
|---|---|
| bug_fix | G-TEST (incl. regression test), G-REVIEW |
| feature (backend) | G-TEST, G-BUILD, G-STATIC, G-REVIEW |
| feature (UI) | G-TEST, G-BUILD, G-VISUAL, G-REVIEW |
| refactor | G-TEST (no behaviour change), G-STATIC, G-REVIEW |
| migration | G-MIGRATION, G-TEST, G-REVIEW (+ D-level per policy) |
| security-sensitive | G-SECURITY, G-TEST, G-REVIEW |
| performance | G-BENCH, G-TEST |
| documentation / design | G-DOCS |
| spike / experiment | evidence of the *finding* (positive or negative) plus a recorded conclusion. Not production gates. |
| outcome validation | as defined on the OUTCOME's VALIDATION node, often G-HUMAN or G-RUNTIME |

A project may add gates. Removing a required gate for a task type is D3. Removing
G-SCOPE or G-SECURITY is D4.

## 5. Verdicts

```
GateVerdict { gate, task_id, commit_sha, verdict: pass|fail|inconclusive, evidence:[EVD…], notes }
```

- `inconclusive` (for example, a flaky test or a missing tool) is **not** pass. It goes back to the
  Planner as a verification-infrastructure problem.
- A `fail` returns the task to `ready` with the findings attached and increments the attempt count.

## 6. Verifying this repository (OOS-0001)

Gate set: **G-DOCS + G-SCOPE**.

```sh
python tools/validate.py
python -m unittest discover tests
```

`G-REVIEW` and `G-HUMAN` for OOS-0001 come from Billy reviewing the branch.
