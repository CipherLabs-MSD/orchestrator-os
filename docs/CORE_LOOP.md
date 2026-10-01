# Core Loop

```
OBSERVE → ORIENT → PLAN → DELEGATE → EXECUTE → VERIFY → LEARN → REPLAN ─┐
   ▲                                                                    │
   └────────────────────────────────────────────────────────────────────┘
```

The system **never blindly continues an obsolete plan**. Each iteration begins by
observing reality, and the plan must survive contact with it.

## Phases

| Phase | Question | Does | Produces | Key failure check |
|---|---|---|---|---|
| **OBSERVE** | What is true *now*? | Read project state through the domain's Observers (software: git HEAD, branches, dirty tree, test/CI status), open runs, memory `as_of`, Billy's new input, open escalations | observation set (with artifact versions) | Stale state: regenerate PROJECT_STATE if `as_of` ≠ current version |
| **ORIENT** | What does it mean? | Compare observations with the task graph and assumptions. Detect contradictions, invalidated assumptions, drift and new risks. | orientation notes, replan triggers | Graph–reality mismatch → replan before planning more work |
| **PLAN** | What next? | Revise the graph if triggered. Compute the ready set. Pick tasks by outcome value, risk and parallelism. Classify decisions against the profile's composed policy (D1–D4, PROHIBITED). | graph revisions, selected tasks, decision records | D4 found → escalate, plan around it |
| **DELEGATE** | Who, with what? | Compose a role, select a backend, build a context package, and set authority, budget and timeout | run specs | Mandatory context exceeds budget → split the task |
| **EXECUTE** | Do it | Dispatcher provisions an isolated Workspace (per domain binding) and runs the backend under the Policy Guard | run results (ChangeSet, logs, self-report) | Timeout, policy violation, crash |
| **VERIFY** | Is it actually done? | Verifier runs the composed gates' checks independently. Review stances run here. | evidence, gate verdicts | Never accept a self-report as evidence |
| **LEARN** | What did we learn? | Memory Manager records decisions, learnings, failed approaches and calibration data | memory deltas | Failure without a recorded lesson is a defect |
| **REPLAN** | Does the plan still hold? | Feed lessons back. Mark `needs_replan` and update priorities. | replan triggers for the next ORIENT | — |

## Cadence and stopping

- The loop runs until one of these is true: the ready set is empty and no replan is
  possible, every remaining work item is blocked on D4, a budget (time, tokens, money) is
  exhausted, or Billy pauses it.
- On stopping it writes `HANDOFF.md` and a digest: progress against outcomes,
  decisions taken (D2/D3), open escalations (D4), and risks.
- **Circuit breaker.** N consecutive iterations without a verified DONE task or any
  new information end the loop with a "stuck" report. N is set in OOS-0010.

## Invariants

1. Every iteration starts at OBSERVE. There is no "continue from where I was" without re-observing.
2. Every state change to the graph is attributable to evidence, a decision or Billy.
3. Execution happens only in isolated workspaces. Canonical project state changes only through
   the integration policy.
4. Orchestrator state (leases, counters, run logs) is never authoritative project truth.
5. **No plan document is permanently authoritative.** PLAN.md, a roadmap, a backlog or the task
   graph itself are hypotheses. Evidence revises them, and an obsolete plan is a defect.
6. The loop is the same in every domain. Domains change *what* is observed, verified and
   authorized, not *how* the loop runs.
