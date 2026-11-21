# ADR-0009 — Billy's approval of a change covers its merge

- **Status:** accepted (owner decision)
- **Date:** 2026-11-21
- **Decision level:** D4
- **Decided by:** billy
- **Task:** OOS-0022
- **Evidence:** Billy's decision in chat on 2026-11-21, relayed word for word by the coordinating
  agent and recorded by Claude Code. He asked "why do I have to merge, I want agents to merge for me"
  and chose this option, verbatim: "Your yes covers the merge (Recommended) — Agents merge in every
  repo, SBOS and Orchestrator OS included, once you've approved the change, a different agent has
  passed the review and the tests are green. Still always yours: real money, live trading, deleting
  things and sending things outside." The conditions below write that option out; the wording is the
  agent's. Billy has not seen this file.
- **Amends:** ADR-0007 §3 (merge authority), which held "until Billy makes an explicit owner decision
  changing it". This is that decision. The rest of ADR-0007 is unchanged.

## Context
ADR-0007 §3 made Billy the only one who merges into protected canonical `main`. Every approved change
then waited for him to press merge. Billy decided that his approval of a change is enough, and that an
agent should then carry out the merge.

## Options considered
1. **Keep Billy-only merge** (ADR-0007 §3). Every approved change waits for Billy. Rejected by Billy.
2. **Earned integration authority** (DECISION_ENGINE §6, orchestrator integrates granted D1/D2
   classes without Billy). Not chosen: it removes Billy's per-change approval.
3. **Billy's approval of a change covers its merge.** Chosen.

## Decision
An agent may merge a change into `main` when all of these hold:
1. Billy approved that change, and the approval (quote or link) is recorded with the work;
2. a different agent reviewed it to pass;
3. tests are green: CI if it runs; if CI cannot run, the full local suite output is recorded;
4. the repository's checks pass (`python tools/validate.py`, `python tools/mutation_check.py` when
   the validator or a policy file changed, `python tools/prepublish_check.py`).

Never covered: real money, live trading or orders, deletion, and sending anything outside beyond the
push itself. Machine-readable: `orchestration/owner_policy.json` `integration_authority`, checked by
`tools/validate.py`. The kernel's `integration_authority.default` stays `billy`: the decision to
integrate is still Billy's; the agent only carries it out. The "earned" phase stays dormant.

## Consequences
- A merge is no longer evidence that Billy saw the final diff; his recorded approval is.
- **Not enforced:** nothing here can check that conditions 1 to 4 held for a given merge.
  `tools/validate.py` checks only that the policy names them.

## Rollback
Set `merge_to_protected_canonical` back to `billy_only` and `agent_merge_authority` to `none`
(the validator requires the pair to match) and supersede this ADR. Cheap; no data changes.

## Revisit when
Billy revokes it, an agent merges a change Billy did not approve, or a merged change has to be
reverted for a reason the review should have caught.
