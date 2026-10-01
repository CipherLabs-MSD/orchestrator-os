# Failure Handling

> Failure should produce information. Retries are bounded, and every failure leaves
> something behind that makes the next attempt smarter.

Record format for dead ends: [`schemas/failed-approach.schema.json`](../schemas/failed-approach.schema.json),
written to `memory/FAILED_APPROACHES.md`.

## 1. Retry budget (defaults; per project override)

| Scope | Budget | When exhausted |
|---|---|---|
| Same task, same approach | 2 attempts | must change approach (different strategy, context or backend) |
| Same task, any approach | 4 attempts | Planner replans (split, re-specify, or spike) |
| Same epic, consecutive failed tasks | 3 | ORIENT treats it as a premise failure and reviews assumptions |
| Loop iterations without a verified DONE or new information | N (OOS-0010) | circuit breaker: stop, "stuck" report |

"Retrying with exactly the same inputs" is forbidden after the first failure. Each retry
must state what is different.

## 2. Playbook

| Situation | Detect | Response | Record |
|---|---|---|---|
| **Failed implementation** | Gate fail, or run error | Attach findings and retry with the delta. Respect the budget. | attempt log. FAILED-entry if the approach is abandoned. |
| **Failed tests** | G-TEST fail | Separate *new code broke tests* from *test is wrong* from *flaky*. Never weaken or delete a test to pass. Changing a test's expectation needs review-stance approval. | evidence. LRN-entry if flaky. |
| **Conflicting agent recommendations** | Two roles disagree (e.g. reviewer vs. producer) | (1) Ask each for evidence. (2) Run a discriminating check if one exists. (3) Apply the conflict order in [KNOWLEDGE_TAXONOMY §6](KNOWLEDGE_TAXONOMY.md). (4) If still split, classify the decision: D1–D3 → orchestrator decides and logs both positions; D4 → escalate with both. | DEC-entry with dissent noted |
| **Repeated failure** | Budget exhausted | Stop the approach. Write a FAILED-entry with the hypothesis, what was tried, the evidence and a retry condition. Replan. | FAILED-entry, REV-entry |
| **Insufficient context** | Agent reports a gap, or fails on missing info | Re-route with the specific gap (max 2). If the info does not exist, it is an OPEN QUESTION, and it may be D4 if it is about intent. | OQ-entry |
| **Stale project state** | `as_of` ≠ HEAD, or context SHA ≠ current | Regenerate state. Invalidate evidence bound to old SHAs. Re-route affected runs. | none, unless it causes rework |
| **Dirty working tree** | Uncommitted changes on the canonical checkout or an assigned worktree | **Never discard.** Canonical checkout: stop and report (it may be Billy's work). Orchestrator worktree: snapshot to a `wip/` branch, then reset the worktree. | run log |
| **Merge conflicts** | Integration branch conflicts | Rebase the task branch onto the latest target in its worktree. Trivial conflicts are D1. Semantic conflicts mean re-verify both changes. If the conflict reflects contradictory decisions, raise a decision record. | DEC-entry if semantic |
| **Agent timeout** | Dispatcher deadline | Cancel and collect partial artifacts. Classify: task too big (split), environment hang (infra issue) or backend issue (try another). Counts as an attempt. | attempt log |
| **Uncertain decision** | Classifier confidence low, or uncertainty ≥ 2 | Round up a D-level. If cheap, run a spike to reduce uncertainty first. | DEC or ESC |
| **Failed experiment** | Hypothesis refuted | **This is a success of the process.** Record it in FAILED_APPROACHES with a retry condition, and update dependents' assumptions. | FAILED-entry + REV-entry |
| **Policy violation attempt** | Policy Guard denial | Abort the run. Do not retry the same action. Review the role spec. Repeated violations mean the backend or role is quarantined for that task type. | security log, LRN-entry |

## 3. Failed-approach entries

```markdown
### FAILED-0003 — Parallel test execution on Windows CI
- **Hypothesis:** running tests with 8 workers cuts CI time by 60%.
- **Tried:** pytest-xdist -n 8 (commit 1a2b3c4), -n 4 (commit 5d6e7f8)
- **Result:** file-lock flakes in 3/10 runs (EVD-0091, EVD-0094)
- **Why it failed:** fixture writes to shared temp dir
- **Retry when:** fixtures use per-worker temp dirs
- **Scope:** project · **Capabilities:** testing, devops · **Date:** 2026-10-01
```

The Context Router includes FAILED-entries that touch the same files, components or
capabilities. Agents are told: *do not repeat this unless the retry condition holds*.
