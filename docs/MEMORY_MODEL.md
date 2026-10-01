# Memory Model

## 1. Principles

1. **Point, don't copy.** Memory indexes and summarizes authoritative artifacts: change history,
   reviews, ADRs, check results and specs (software: commits, PRs, test results). It does not duplicate them. A copy goes stale.
   A pointer can be checked.
2. **Version history is the backbone.** Memory is versioned with the project's `ProjectStore`,
   so its history is the history of what the system believed and when (software binding:
   `git log -p memory/`).
3. **Every entry is attributable.** Who or what wrote it, when, and on what evidence.
4. **Memory is not a transcript.** Only information that changes future behaviour
   is kept.
5. **Freshness is explicit.** Volatile state carries an `as_of` (artifact version and date;
   software: commit SHA). The Observer treats state older than the current version as possibly stale.

## 2. Sources of truth, in order of authority

| Rank | Source | Example | Memory's relationship |
|---|---|---|---|
| 1 | Canonical content at an artifact version | software: code + tests at `main@abc123` | Memory points to it |
| 2 | Verified evidence | gate verdicts and their evidence (software: test logs, build output) | Memory references evidence IDs |
| 3 | Accepted ADRs | `docs/adr/ADR-0003-*.md` | Memory lists and links them |
| 4 | Change history and reviews | software: commit messages, PR threads | Memory cites change and review IDs (software: SHAs, PR numbers) |
| 5 | Project memory files | `PROJECT_STATE.md`, `LEARNINGS.md`, … | Summaries and indexes **derived** from 1–4 |
| 6 | Agent self-reports | "I fixed the bug" | **Never authoritative.** Input to verification only. |

If memory contradicts a higher-ranked source, the higher source wins, and the memory
entry is a defect to fix.

## 3. Files (per project)

Each managed project gets this structure. This repo dogfoods it in [`memory/`](../memory/).
Managed projects keep it in their `ProjectStore` (repository-backed projects: `.oos/memory/`, see OQ-002).
Domain packages may add **memory record types** (`memory_record_types` in the manifest), for
example a finance hypothesis journal or a data-source provenance log. The six files below are
the kernel minimum in every domain.

| File | Purpose | Write policy | Volatility |
|---|---|---|---|
| `PROJECT_STATE.md` | Current milestone, active tasks, health, known blockers. Derived and regenerable. | Overwritten each loop iteration. Carries `as_of`. | High |
| `DECISIONS/` | D2 decision log entries (`DEC-NNNN-*.md`) plus an index. D3 decisions live as ADRs in the project's ADR dir and are indexed here. | Append-only. Supersede, never edit the decision. | Low |
| `LEARNINGS.md` | Validated, reusable insights ("the test suite needs `--runInBand` on Windows") | Append. Prune when superseded. | Medium |
| `FAILED_APPROACHES.md` | What was tried, why it failed, the evidence, and *when it might be worth retrying* | Append-only | Low |
| `OPEN_QUESTIONS.md` | Unresolved questions, each tagged with who must answer (agent research / Billy) and what is blocked | Append. Close with a resolution pointer. | Medium |
| `HANDOFF.md` | What the next session or agent needs to resume: last actions, verified vs. unverified, next step | Overwritten at session end | High |

## 4. Entry anatomy

Each entry in `LEARNINGS.md`, `FAILED_APPROACHES.md` and `OPEN_QUESTIONS.md` is a Markdown
section with a small metadata line, so it reads well for humans and parses for machines:

```markdown
### LRN-0007 — Windows test runner needs serial mode (software example)
- **Evidence:** EVD-0123 (CI log), commit 4f2a9c1
- **Scope:** project · **Confidence:** high · **Learned:** 2026-10-01 · **Status:** active
- **Applies to capabilities:** testing, devops

Running the suite in parallel on Windows causes file-lock flakes...
```

Machine-readable equivalents are defined in [`schemas/`](../schemas/): `decision-record`,
`failed-approach` and `evidence`. Until a record store exists (OOS-0003), Markdown is the
canonical form.

## 5. Lifecycle

```
run result ──► Verifier ──► evidence (EVD) ──► Memory Manager
                                   │
         ┌─────────────┬───────────┼────────────┬──────────────┐
         ▼             ▼           ▼            ▼              ▼
   decision log   LEARNINGS   FAILED_APPROACHES  OPEN_QUESTIONS  PROJECT_STATE / HANDOFF
```

- **Supersession, not deletion.** A wrong learning is marked `superseded_by: LRN-00NN`
  or `status: refuted`. The record of having believed it is itself useful.
- **Compaction.** When a file grows past a threshold (set in OOS-0011), the Memory
  Manager writes a summary section and moves old entries to `memory/archive/`. The
  summary keeps the IDs so links never break.
- **Staleness check.** At OBSERVE, the Observer compares `PROJECT_STATE.as_of` with
  HEAD. If they differ, state is regenerated before planning. The orchestrator never
  plans from a stale snapshot.

## 6. What memory is *not*

- It is not user context. Billy's preferences never get written into project memory
  except as a **cited reference** inside a decision (`evidence: CTX-0012`).
- It is not orchestrator state. Retry counters, leases and run logs live in the OOS
  workspace. Only their *conclusions* reach project memory.
- It is not general knowledge. "React 19 supports X" belongs in a learning only if it
  was verified *in this project* and changes what agents should do here.
