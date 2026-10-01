# DEC-0003 — Implementation choices for the domain-specialization addendum

- **Level:** D2 (each choice reversible, inside ADR-0006, directed by Billy's OOS-0001 addendum)
- **Task:** OOS-0001 · **Decided by:** orchestrator · **Date:** 2026-10-01 · **Status:** decided

| # | Choice | Alternatives | Rationale |
|---|---|---|---|
| 1 | Finance is a **data-only sketch** inside `domains/finance/domain.json` (`operational: false`) | README only; no finance artifact at all | Lets the validator prove that the *same* classifier yields stricter finance outcomes. It sets no thresholds and cannot be loaded by a profile. |
| 2 | Add a **PROHIBITED** tier above D4 | Model "never" as D4 | D4 means "ask Billy". "Never" must not even be asked about (for example exposing private keys). |
| 3 | Rename kernel class `spend_money_or_commit_resources` → `spend_money_or_allocate_funds` | Keep it and allowlist the word | "commit" is version-control vocabulary, and the purity check should have no exceptions |
| 4 | Keep docs flat (`docs/`). Add `orchestration/kernel/`, `orchestration/profiles/`, `domains/` | Mirror the suggested `docs/architecture/`, `orchestration/{policies,routing,verification}/` tree | Smallest coherent change. Kernel vs. domain is the boundary that matters. Deeper nesting adds no checkable meaning yet. |
| 5 | Validator checks Markdown anchors, and ADR bodies allow purely editorial link repairs | Leave anchors unchecked | The addendum added many cross-links. The new check immediately found one real broken link (in ADR-0002). |
| 6 | Add `tools/mutation_check.py` | Keep mutation testing ad hoc | Makes "the checks bite" reproducible evidence rather than a claim |

**Evidence.** `python tools/validate.py` (13/13), `python -m unittest discover tests` (31 OK),
`python tools/mutation_check.py` (20/20). See HANDOFF.md.
