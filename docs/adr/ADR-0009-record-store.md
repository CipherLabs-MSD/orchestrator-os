# ADR-0009 — Record store: files-first canonical JSON with envelopes, plus append-only logs

- **Status:** accepted (D3, orchestrator) · pending owner review via the OOS-0003 pull request
- **Date:** 2026-10-02
- **Decision level:** D3. Persistence format for long-lived OOS state. Reversible, inside ADR-0001 and ADR-0008.
- **Decided by:** orchestrator (OOS-0003)
- **Task:** OOS-0003
- **Refines:** ADR-0001 (files-first) · **Builds on:** ADR-0008 (Python, stdlib-first), EXECUTION_RUNTIME §4 (journal)
- **Evidence:** `tests/test_record_store.py`, `tests/test_append_log.py`, `tools/store_sabotage_check.py`. Design: [RECORD_STORE](../RECORD_STORE.md).

## Context

From OOS-0004 on, components need to persist structured records durably: task nodes, decisions,
evidence, journals and memory entries. ADR-0001 already chose plain files in git, validated by schemas,
"no database until a need is proven". It deferred concurrent-writer coordination. ADR-0008 chose Python,
stdlib-first, with a write-ahead journal. Windows and macOS are first-class targets. The substrate must stay
domain-neutral (I-1).

## Candidates

| Option | Crash safety | Concurrency | Inspectable / diffable | Portability | Fit with ADR-0001 |
|---|---|---|---|---|---|
| **One canonical JSON file per record + JSONL logs** | atomic temp + install, digest | OS-released file lock | yes: one file per record, deterministic bytes | stdlib, all OSes | direct |
| SQLite (stdlib) | excellent (WAL, transactions) | excellent locally | no: opaque binary, unreviewable diffs | stdlib; network-FS caveats | contradicts "no database until needed"; breaks reviewable project truth |
| One JSON document per collection | rewrite-whole-file risk | coarse | partly | stdlib | worse diffs, larger blast radius per write |
| External DB/server | strong | strong | no | adds infrastructure and secrets | rejected by ADR-0001 |

## Decision

1. **Storage:** one canonical JSON file per record (`records/<type>/<id>.json`) wrapped in a domain-neutral
   **envelope**: type, id, schema id and version, revision, timestamps, provenance, supersedes,
   previous_digest, extensions, digest. History is an **append-only, hash-chained JSONL log**. Root
   placement is the caller's (workspace binding).
2. **Validation:** JSON Schema files in `schemas/` remain the single source of truth. One Python
   validator (`oos.records.schema`) implements a **fail-closed subset**: schemas using unsupported keywords
   are rejected at load (DEC-0006). `tools/validate.py` now uses the same implementation.
3. **Mutability per type** (`orchestration/kernel/record_types.json`): immutable types (default) change only by
   supersession. Mutable types (task-node) use optimistic revisions and keep every prior revision.
4. **Evolution:** every schema declares `x-oos-schema-version`. Newer records are refused. Older records need
   registered step migrations and are migrated on read, without being rewritten.
5. **Concurrency:** one OS-released writer lock per store (and per log). Lock-free readers over atomic installs.

## Consequences

- Records are reviewable in diffs, and git (where a store root sits in a repository) adds history for free.
- Queries are directory scans. Fine now, and an index or SQLite cache can be added *behind* the same API if
  needed. The files stay canonical.
- Every schema change now carries a version number. Incompatible changes need a migration.
- `superseded_by` in record bodies is not used by the store (it is derived), which avoids two truths.
- `context-package` cannot be stored until its id field is reconciled (OOS-0006).

## Rejected alternatives

- **SQLite as the canonical store.** Technically strong, but it trades away ADR-0001's reviewable,
  diffable project truth with no proven need. Kept as a possible *derived* index later.
- **Full JSON Schema via the `jsonschema` package.** It adds a dependency (D2), and our schemas need only the
  subset. Fail-closed loading prevents silent partial support (DEC-0006).
- **Pydantic/dataclass models as the record definitions.** They would be a second, conflicting source of truth for shape.

## Unresolved risks

- Power-loss durability is not testable here (fsync is called; tool-confirmed as untested).
- POSIX (macOS/Linux) code paths are untested. Network and cloud-synced folders are unverified, so do not place store roots there.
- O(n) scans for duplicate and supersession checks. Revisit at thousands of records per type.
- One writer lock per store serializes all writers. This is fine locally and would limit a future multi-worker service.

## Revisit when

- Write throughput or record counts make scans or the global lock measurable bottlenecks.
- Multiple machines must share a store (needs a server, or a different coordination model).
- Schemas need keywords outside the subset (`$ref`, `oneOf`): extend the validator, or adopt `jsonschema` (D2).
