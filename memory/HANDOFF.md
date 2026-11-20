# OOS-0021 delivery · 2026-10-14

- Separate checkout, branch `oos-0021/discovery-inbox`, base `109a3dc`. Existing local repos and worktrees untouched.
- Added `discovery/INBOX.md`, DISC-001 Ruflo, all requested fields/statuses and add-row instructions.
- D1: reversible documentation implementing the direct user request. No kernel or policy changes.
- Location choice: Orchestrator-OS is the requested execution control plane. UniversalSystems indexes Idea-Explorations as an older raw OS-spark inbox feeding BusinessSync; it does not provide this resource-candidate register. System-Builder-OS holds principles, not resource intake.
- No evaluation, installation, automatic tasks, Model Lab dependency, publication or merge.
- Verification: validator 15/15 PASS; foundation tests 31/31 PASS; full suite ran 33 tests, one runtime-spike setup error (TimeoutError), one Node skip (OOS_SPIKE_NODE unset). Same runtime error reproduced on untouched main `109a3dc` in a temporary archive. Full suite is not green; no runtime files changed.
- Diff reviewed; whitespace check clean. Mutation check skipped (no validator or policy changes); prepublish check skipped (no push). Owner review pending; local commit only.
- Next: review this branch; next captured resource gets DISC-002. Recheck remote state before publication.

## Previous handoff (retained)

# Handoff

- **Session:** OOS-0002 runtime and execution spike · 2026-10-01 · Claude Code (claude-opus-5-5)
- **Branch:** `oos-0002/runtime-spike` from `main` @ `7e01119`. Pushed for review. **Not merged** (Billy merges).

## Done

- Ran executable spikes for the Python and Node runtimes against one fake provider (`spikes/oos-0002/`, **disposable**):
  E1 cold start, E2 eight concurrent workers, E3 tree kill, E4 orphan behaviour on an OOS crash,
  E5 journal + crash recovery + resume (Python), E6 Unicode paths, stdio encoding and signal pitfalls.
- Decision: [ADR-0008](../docs/adr/ADR-0008-runtime-and-execution-model.md). **Python ≥ 3.12** with a **hybrid model**
  (session-oriented resumable runs; a daemon later only as a trigger).
- Durable design for later tasks: [`docs/EXECUTION_RUNTIME.md`](../docs/EXECUTION_RUNTIME.md). It covers the provider
  protocol, the journal transitions, recovery rules, supervision rules and the platform matrix.
- Validator: a new check that spike code is labelled and isolated. Two new mutations.
- Evidence tests: `tests/test_spike_oos0002.py`. The Node part runs when `OOS_SPIKE_NODE` is set.
- Learnings LRN-0006 to LRN-0008. FAILED-0002.

## Verified

- Windows 11 only (Python 3.10.6, Node 22.9.0). See the session report for exact command output.
- **macOS: unverified.** POSIX code paths exist but have not run on a Mac.

## Not done (by instruction)

- No production runtime, adapters, daemon, factory or remote workers. FinanceOS and Demon Codex untouched.
  The private context repo was not created. No real credentials anywhere.

## Next step

1. Billy reviews and merges the OOS-0002 PR (G-REVIEW). OOS-0002 becomes DONE.
2. Billy installs Python 3.12+ (ADR-0008).
3. **OOS-0003**: record store and schema validation library.
