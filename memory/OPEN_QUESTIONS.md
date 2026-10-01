# Open Questions

Each question says **who must answer** it: `billy` (a D4 decision, or information only Billy
has) or `orchestrator` (resolvable by an agent within its authority, in the named task).

| ID | Question | Answer by | Blocks | Status |
|---|---|---|---|---|
| OQ-001 | Where should the user-context instance live, given this repo is public? | billy | — | **resolved** (ADR-0007: private store `orchestrator-context`) |
| OQ-002 | Where does per-project OOS state live for managed projects (`.oos/` in the project repo, or a central workspace)? | orchestrator (OOS-0004, D3) | OOS-0004 | open |
| OQ-003 | How should escalations and digests reach Billy, and who holds merge authority at start? | billy | — | **resolved** (ADR-0007: active session; Billy-only merge) |
| OQ-004 | Which execution backends may receive private project code or user context? | billy | — | **resolved** (ADR-0007: Claude + Codex, task-relevant, never secrets) |
| OQ-005 | Spending and usage budget for autonomous runs | billy | — | **resolved** (ADR-0007: 0 SEK; every cost escalates) |
| OQ-006 | Implementation language and runtime for the control plane | orchestrator (OOS-0002, D3). Billy's preference welcome as evidence. | OOS-0003 | open |
| OQ-007 | Which domain becomes the second *operational* package, and when? (Finance is the documented candidate.) | billy | OOS-0020 | **deferred** by Billy (2026-10-01); not selected |

---

### OQ-001 — Location of the user-context instance
- **Resolved 2026-10-01 by Billy ([ADR-0007](../docs/adr/ADR-0007-initial-owner-policy.md) §1):** a separate private store,
  working name `orchestrator-context`. It is not yet created. The history below is kept.
- **Why it matters:** `context/` will hold curated personal preferences. This repository is
  public (LRN-0001). Publishing personal context would be irreversible (D4).
- **Options:**
  1. **Separate private repo** (for example `CipherLabs-MSD/oos-user-context`) using the schema
     from this repo. OOS reads it via a configured path. *(recommended: keeps the public core
     clean, gives versioning and provenance, and is easy to share selectively later)*
  2. Make `orchestrator-os` private and keep entries in `context/`.
  3. A local-only, git-ignored directory. Simple, but no history and easy to lose.
- **Meanwhile:** `context/` holds placeholders only.

### OQ-002 — Per-project OOS state location
- **Default proposal:** `.oos/` inside each managed project repo, so memory and graph travel
  with the code. The orchestrator decides this in OOS-0004 as a D3 decision, unless Billy objects to OOS files
  appearing in his project repos.

### OQ-003 — Escalation channel and initial merge authority
- **Resolved 2026-10-01 by Billy (ADR-0007 §2–3):** escalations go to the active session. Billy alone merges to `main`.
  No extra `reserved_for_billy` classes.
- **Needs from Billy:** (a) where D4 escalations and digests go (a file in the repo, GitHub
  issues on a private repo, email, or something else), and the acceptable interrupt frequency.
  (b) Confirmation that he alone merges to `main` at first (the current default).
  (c) Any additions to `reserved_for_billy` beyond the class floors.

### OQ-004 — Backend data policy
- **Resolved 2026-10-01 by Billy (ADR-0007 §4):** Claude and Codex backends may receive task-relevant private code and
  approved user context. Others need explicit authorization. Signing secrets never go into model context.
- **Needs from Billy:** for each vendor (Anthropic, OpenAI, …), whether `private` project code
  and/or user-context entries may be sent. Until he answers, `trust.data_policy_ok_for` is empty
  for vendor backends, and only public sandbox work is routable.

### OQ-005 — Budget
- **Resolved 2026-10-01 by Billy (ADR-0007 §5):** the autonomous limit is 0 SEK. Any financial commitment escalates.
- **Needs from Billy:** caps per run, per day and per project for paid model usage, and whether
  a subscription versus API-billed usage changes the picture. Until he answers, any action that
  spends money is D4 (the current policy).

### OQ-006 — Implementation runtime
- Resolved in OOS-0002 by spike and ADR. Billy may state a preference, which would be recorded as
  evidence, not as a requirement.

### OQ-007 — Second operational domain
- **Deferred by Billy 2026-10-01 (ADR-0007 §6).** FinanceOS is a strong candidate and is **not selected**.
- **Why it matters:** the kernel/domain split (ADR-0006) is only proven by a second *real*
  domain. Finance is the documented example. It also carries the highest authority risk,
  because every threshold and transaction rule is a D4 decision for Billy.
- **Not needed now.** It only matters after the sandbox pilot (OOS-0016). Until then the finance
  package stays `illustrative` and non-operational.
