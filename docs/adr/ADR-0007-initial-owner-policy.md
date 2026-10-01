# ADR-0007 — Initial owner policy

- **Status:** accepted (owner decision)
- **Date:** 2026-10-01
- **Decision level:** D4
- **Decided by:** billy
- **Task:** OOS-0001 (owner acceptance)
- **Resolves:** OQ-001, OQ-003, OQ-004, OQ-005 · **Defers:** OQ-007
- **Machine-readable:** [`orchestration/owner_policy.json`](../../orchestration/owner_policy.json)

## Context

OOS-0001 left open questions that only Billy could answer: where his personal context
lives, how escalations reach him, who merges, which AI systems may see private material,
and what may be spent. He answered them when accepting OOS-0001. This ADR records the answers
as **owner policy**: installation-level trusted policy that applies to every orchestrator
profile. It sits above domain packages and profiles. It is not part of the kernel, which stays
vendor- and currency-neutral.

## Decisions

### 1. Personal context storage (resolves OQ-001)
- Billy's actual personal context is **not** stored in the public `orchestrator-os` repository.
- It goes in a separate **private** store or repository, working name **`orchestrator-context`**.
  It is **not created yet**. Creating and populating it is part of OOS-0012, with Billy.
- The public repository may contain schemas, interfaces, documentation, fictional or
  hypothetical examples, import/export protocols and validation rules. It must not contain
  Billy's actual personal context unless he explicitly approves publication.
- The private store keeps the full model: approval, provenance, scope, confidence, strength,
  conflicts and supersession ([PERSONAL_CONTEXT_MODEL](../PERSONAL_CONTEXT_MODEL.md)).

### 2. Escalations (resolves OQ-003, part a)
- The initial escalation destination is **Billy in the active Orchestrator interaction/session**.
- The `escalation.channels` list keeps room for later channels (notifications, digests, email,
  messaging, dashboards). None are implemented, and adding one is an owner decision.

### 3. Merge authority (resolves OQ-003, parts b and c)
- **Billy alone** may merge into protected canonical `main` (software binding of kernel `Integration`).
- With a task's authorization, agents and OOS may create branches/workspaces, modify permitted
  files, run tests, create commits, push permitted branches, create or update pull requests,
  review work, and recommend merge. **None of these is merge authority.**
- This holds until Billy makes an explicit owner decision changing it. The kernel's "earned
  integration authority" phase stays dormant until then. No `reserved_for_billy` classes beyond
  this were added.

### 4. Private code, personal context and AI systems (resolves OQ-004)
- **Claude and Codex** may receive relevant private project code and relevant *approved*
  personal context when an authorized task requires it. In the registry this covers the backends
  `claude-code`, `claude-agent-sdk`, `claude-api` and `codex`.
- Conditions: least privilege. Selection by the Context Router. Task-relevant context only. Never
  the complete personal profile by default. No unrelated project information.
- Secrets are governed separately and are never ordinary context. **Private keys, seed phrases and
  equivalent signing secrets are never supplied as model context.** This is a kernel prohibition
  (`expose_or_transmit_secrets`), whose description now names them explicitly.
- Any other AI/model provider needs explicit owner authorization or a later policy decision before
  it receives private code or personal context.
- **Clarification (Billy, 2026-10-01).** The approved backends are exactly Claude Code, Claude Agent SDK,
  Claude API and Codex. They may receive task-relevant *private project code* and *approved personal
  context* only when an authorized task requires it and the Context Router and owner policy permit it.
  This grants **no access to secrets**. Private keys, seed phrases, signing credentials, authentication
  secrets, passwords, API secrets and equivalent secret material are never ordinary model context.
  Least privilege applies. Other providers need a later explicit authorization.
- Vendor names appear only in owner policy and the backend registry, **never in the kernel**. The
  Backend Router enforces `trust` clearances, and the validator checks that no backend's clearance
  exceeds this owner policy.

### 5. Autonomous spending (resolves OQ-005)
- The initial autonomous spending limit is **0 SEK**.
- Agents may identify paid services, compare costs, estimate required spending, recommend
  purchases and prepare a proposed action.
- Any action that creates a financial commitment or incurs external cost **escalates to Billy (D4)**.
  This matches the kernel floor `spend_money_or_allocate_funds` and cost score 3 → D4.
- Later replacements (per-run, provider, domain or project budgets, transaction thresholds) are
  future owner decisions. No payment system is built.

### 6. Second real domain (OQ-007, deferred)
- **No decision.** FinanceOS is a strong candidate but is **not selected**. The finance package stays
  `illustrative` and non-operational. Nothing about FinanceOS is implemented.

### 7. Publication
- Pushing the accepted OOS-0001 branch to the public `CipherLabs-MSD/orchestrator-os` repository is
  approved, after pre-push privacy and secret checks. Billy keeps merge authority, so agents do not merge.

## Consequences

- `context/` in this repository will only ever hold placeholders and fictional examples.
- The Backend Router may route private work to the four approved backends. All others stay public-only.
- Escalations are designed for a synchronous session first. Batching and digests come later.
- Every spend escalates. This is slower, but safe at the start.

## Rollback

Any item can be replaced by a later owner decision recorded as a new ADR that supersedes the
relevant section, together with an edit to `orchestration/owner_policy.json`.

## Revisit when

- A second escalation channel is needed (long unattended runs).
- Escalations for trivial costs dominate. Then consider budgets.
- A new AI provider is considered for private work.
- OOS-0016 (sandbox pilot) is done. Then decide OQ-007.
