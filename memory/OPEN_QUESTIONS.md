# Open Questions

Each question says **who must answer** it: `billy` (a D4 decision, or information only Billy
has) or `orchestrator` (resolvable by an agent within its authority, in the named task).

| ID | Question | Answer by | Blocks | Status |
|---|---|---|---|---|
| OQ-001 | Where should the user-context instance live, given this repo is public? | billy | OOS-0012 | open |
| OQ-002 | Where does per-project OOS state live for managed projects (`.oos/` in the project repo, or a central workspace)? | orchestrator (OOS-0004, D3) | OOS-0004 | open |
| OQ-003 | How should escalations and digests reach Billy, and who holds merge authority at start? | billy | OOS-0010 | open |
| OQ-004 | Which execution backends may receive private project code or user context? | billy | OOS-0013 | open |
| OQ-005 | Spending and usage budget for autonomous runs | billy | OOS-0010 | open |
| OQ-006 | Implementation language and runtime for the control plane | orchestrator (OOS-0002, D3). Billy's preference welcome as evidence. | OOS-0003 | open |

---

### OQ-001 — Location of the user-context instance
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
- **Needs from Billy:** (a) where D4 escalations and digests go (a file in the repo, GitHub
  issues on a private repo, email, or something else), and the acceptable interrupt frequency.
  (b) Confirmation that he alone merges to `main` at first (the current default).
  (c) Any additions to `reserved_for_billy` beyond the class floors.

### OQ-004 — Backend data policy
- **Needs from Billy:** for each vendor (Anthropic, OpenAI, …), whether `private` project code
  and/or user-context entries may be sent. Until he answers, `trust.data_policy_ok_for` is empty
  for vendor backends, and only public sandbox work is routable.

### OQ-005 — Budget
- **Needs from Billy:** caps per run, per day and per project for paid model usage, and whether
  a subscription versus API-billed usage changes the picture. Until he answers, any action that
  spends money is D4 (the current policy).

### OQ-006 — Implementation runtime
- Resolved in OOS-0002 by spike and ADR. Billy may state a preference, which would be recorded as
  evidence, not as a requirement.
