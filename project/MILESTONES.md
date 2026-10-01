# Milestones

Milestones are demonstrable increments. Each has an exit criterion that is proven with
evidence, not asserted. Like every plan here, this sequence is a hypothesis and will be
revised as evidence arrives.

| ID | Name | Goal | Exit criterion (evidence) | Backlog |
|---|---|---|---|---|
| **M0** | Foundation | A coherent, validated design that implementation can build against without redesign | OOS-0001 merged after Billy's review. `tools/validate.py` and tests pass. | OOS-0001 |
| **M1** | Walking skeleton | One task goes through the full loop on a **sandbox** repo: observe, plan, classify, route, execute in a worktree, verify, record | Recorded run with a verified task branch, a PR, a gate verdict bound to its SHA, and a generated escalation for a seeded D4 scenario. No protected-branch writes. | OOS-0002 – OOS-0010 |
| **M2** | Memory and personal context | Learning persists across sessions. Curated user context is routed selectively. | A second session resumes from HANDOFF without human re-briefing. Routing golden tests show zero user-context leakage. | OOS-0011, OOS-0012 |
| **M3** | Multi-agent organization | Composed roles, two or more backends, parallel worktrees, independent review | Two tasks run in parallel without conflict. A review stance runs on a different backend from its producer. Conflicting recommendations are resolved and logged. | OOS-0013 – OOS-0015 |
| **M4** | Pilot | OOS advances a real project across a milestone | Sandbox pilot completes a milestone. Then the Demon Codex pilot starts (Billy's go-ahead, D4). | OOS-0016, OOS-0017 |
| **M5** | Sustained autonomy | Multi-day operation supervised through digests, with calibrated authority | *Defined after M4 evidence.* | — |

## Not in any milestone yet (deliberately)

- Hosted or daemon deployment. OOS-0002 decides whether the loop starts as scheduled sessions or a daemon.
- Web UI or dashboard.
- Learned or embedding-based context ranking.
