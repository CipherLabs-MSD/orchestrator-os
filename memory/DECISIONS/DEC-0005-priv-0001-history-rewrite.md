# DEC-0005 — PRIV-0001: rewrite unpublished history to remove private-repository text

- **Level:** D4 · **Decided by:** billy · **Date:** 2026-10-01 · **Status:** decided
- **Task:** OOS-0001 (pre-publication)

## Finding (PRIV-0001)

The pre-push manual review found that the unpublished addendum commit paraphrased the description of
a **private** repository (FinanceOS) in two docs. The text came from repository metadata the agent had
read. It was not supplied by Billy for publication. Its content is deliberately not repeated here.

## Decision

Billy chose option 1: **rewrite the unpublished commits** so that the text appears in no commit that
will be published. Rewriting was authorized because the history had never been pushed.

## What was done

| Old (local only, never published) | Replacement (published) | Change |
|---|---|---|
| `7133511` | `7133511` | unchanged |
| `b76e4ed` | `b76e4ed` | unchanged |
| `4e6744b` (addendum) | `3e8d819` | two sentences replaced with "a future finance project and candidate domain". Message, author and dates are unchanged. |
| `ff3acf9` (acceptance) | the acceptance commit on top of `3e8d819` | rebuilt from the same content, plus this resolution, the provider clarification and the DONE status |

- No replacement wording is derived from the private repository. FinanceOS is referred to generically only.
- A local recovery backup exists (`refs/backup/oos-0001-pre-priv-0001` and a bundle outside the repo).
  It is **never pushed**. Only `oos-0001/foundation` is pushed, by explicit refspec.

## Verification

Full-history automated and manual semantic review of the publishable history. Results are in HANDOFF.md.

## Lesson

LRN-0005: check a source's visibility before quoting it anywhere public.
