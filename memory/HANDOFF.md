# Handoff

- **Session:** OOS-0001 owner acceptance and publication · 2026-10-01 · Claude Code (claude-opus-5-5)
- **Branch:** `oos-0001/foundation`. This commit is the publication candidate. It is pushed to
  `CipherLabs-MSD/orchestrator-os` only if every pre-publication check passes (see the session report).
  `main` does not exist. Billy creates it (below).

## Done

- **Owner acceptance** of OOS-0001 incl. the addendum: [DEC-0004](DECISIONS/DEC-0004-oos-0001-owner-acceptance.md). **OOS-0001 is DONE.**
- **Owner policy**: [ADR-0007](../docs/adr/ADR-0007-initial-owner-policy.md) / [`orchestration/owner_policy.json`](../orchestration/owner_policy.json).
  It covers:
  - private context store `orchestrator-context` (not created)
  - escalation in the active session
  - Billy-only merge
  - the Claude Code, Claude Agent SDK, Claude API and Codex data policy, clarified to grant no access to secrets
  - 0 SEK spending
  - second domain deferred
- **PRIV-0001 resolved** by rewriting the unpublished history ([DEC-0005](DECISIONS/DEC-0005-priv-0001-history-rewrite.md)).
  The two foundation commits are unchanged. The addendum is now `3e8d819`, with a generic reference only.
- A local recovery backup of the pre-rewrite history exists outside the published refs. It is not pushed.

## Verified before publication (2026-10-01)

See the session report for exact output.

- `python tools/validate.py`
- `python -m unittest discover tests`
- `python tools/mutation_check.py`
- `python tools/prepublish_check.py`
- a fresh clone validated
- a full-history search for the private text over every publishable commit, including messages
- a manual semantic review of the full publishable diff

## Owner action (Billy)

The remote had no branches before this push. GitHub normally makes the first pushed branch the default,
so check the repository's default branch after the push. To establish `main`:

1. Create `main` from the reviewed tip (this is the merge):
   `git push origin oos-0001/foundation:refs/heads/main`, or use GitHub → Branches → New branch.
2. GitHub → Settings → General → Default branch → `main`.
3. GitHub → Settings → Branches (or Rules) → protect `main`: require a pull request before merging, and block force-pushes and deletion.
4. Optional: delete `oos-0001/foundation` after `main` exists.

## Not done (by instruction)

- No merge. `main` was not created. OOS-0002 is not started. No runtime and no adapters. The private context repo
  was not created. Demon Codex and FinanceOS were not modified.

## Next step

OOS-0002: choose the runtime and language, and decide session-oriented vs. persistent execution (spike + ADR).
