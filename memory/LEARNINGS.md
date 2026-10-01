# Learnings

Validated, reusable insights for work on Orchestrator OS. Format: [MEMORY_MODEL §4](../docs/MEMORY_MODEL.md#4-entry-anatomy).

### LRN-0001 — The OOS repository is public
- **Evidence:** `gh repo view CipherLabs-MSD/orchestrator-os` reported `visibility: PUBLIC` (2026-10-01)
- **Scope:** project · **Confidence:** high · **Learned:** 2026-10-01 · **Status:** active
- **Applies to capabilities:** all

Nothing private may be committed here: no user-context entries, no secrets, no private
project details. This is the reason OQ-001 exists.

### LRN-0002 — Dev environment: Windows, Python 3.10 stdlib, no Node
- **Evidence:** `python --version` gave 3.10.6. `jsonschema`, `pytest` and `node` are unavailable (2026-10-01).
- **Scope:** project · **Confidence:** high · **Learned:** 2026-10-01 · **Status:** active
- **Applies to capabilities:** devops, testing, architecture

Tooling must run on Windows. Use stdlib-only scripts until OOS-0002 chooses a runtime (DEC-0001).

### LRN-0003 — "General" designs drift toward the first domain
- **Evidence:** OOS-0001 addendum audit (2026-10-01). The nominally general first draft had 14/14
  software capabilities, software-only gates and task types, software class floors in the generic
  Decision Engine, and git terms in kernel schemas (`commit_sha`, `built_at_sha`, `implementing_commits`, `worktree`).
- **Scope:** project · **Confidence:** high · **Learned:** 2026-10-01 · **Status:** active
- **Applies to capabilities:** architecture, code_review

Writing "domain-agnostic" in a doc does not make a design domain-agnostic. Run the kernel-purity
check, and ask "kernel or domain?" for every concept. See ADR-0006 and AGENTS.md §3a.

### LRN-0004 — Regex `\b` does not split snake_case
- **Evidence:** `test_vocabulary_in_keys_is_detected` failed: `\bcommit\b` does not match `commit_sha`,
  because `_` is a word character. The fix was to treat `_` as a break before matching.
- **Scope:** project · **Confidence:** high · **Learned:** 2026-10-01 · **Status:** active
- **Applies to capabilities:** testing, code_review

A purity or vocabulary check over identifiers must normalize separators first, or it silently
misses exactly the contamination it targets. Mutation-test such checks (tools/mutation_check.py).

### LRN-0005 — Check source visibility before quoting another repository
- **Evidence:** The pre-push review (2026-10-01) found that the unpublished addendum commit paraphrased a **private**
  repository's GitHub description in two public docs. It was resolved by rewriting the unpublished history (DEC-0005). The text came from repository metadata the
  agent had read, not from anything Billy supplied for publication.
- **Scope:** global · **Confidence:** high · **Learned:** 2026-10-01 · **Status:** active
- **Applies to capabilities:** all

Before putting anything about another project into a public repository, check that project's
visibility. Prefer what the owner wrote for this purpose. Private metadata (descriptions, names,
strategy) counts as private content. Run `tools/prepublish_check.py` and a manual review before every push.
