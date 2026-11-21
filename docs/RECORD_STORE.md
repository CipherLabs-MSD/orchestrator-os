# Record Store and Schema Validation

> Status: **implemented** in OOS-0003 (`oos/records/`). Decision: [ADR-0009](adr/ADR-0009-record-store.md).
> Validator policy: [DEC-0006](../memory/DECISIONS/DEC-0006-fail-closed-schema-subset.md).
> This is the domain-neutral persistence substrate. The task graph, Decision Engine, Context Router,
> run journals and memory build on it. It knows record *types*, never record *meaning*.

## 1. What it is (and is not)

```
 Orchestrator components (task graph, decisions, evidence, journals, …)
                │
                ▼
     oos.records  ── SchemaRegistry (schemas/*.schema.json: the only source of truth for shape)
                │  ── RecordStore   (one canonical JSON file per record, in an envelope)
                │  ── AppendLog     (hash-chained JSON Lines for journals/history)
                ▼
        durable files under a store root chosen by the caller
```

| It is | It is not |
|---|---|
| validate-then-persist for any registered type | a database, a query engine, an ORM |
| append-only by default, with supersession instead of destruction | a place for domain logic or business rules |
| deterministic, inspectable, diff-friendly files (ADR-0001) | git-aware: putting a store root inside a repository is a *workspace binding* decision |
| the substrate for orchestrator state *and* project-truth records | the `ProjectStore` itself (that kernel interface is bound per domain) |

## 2. Record model: the envelope

Every stored record is `records/<type>/<id>.json` ([`schemas/record-envelope.schema.json`](../schemas/record-envelope.schema.json)):

| Field | Purpose | Architectural basis |
|---|---|---|
| `oos_record` | envelope format version (1) | record evolution |
| `type`, `id` | record type name and stable id (equals `body.id`) | stable ids already defined per schema (`DEC-`, `EVD-`, …) |
| `schema`, `schema_version` | `$id` and `x-oos-schema-version` of the body schema at write time | record evolution |
| `revision` | 1, or higher for mutable types | task-node state changes |
| `created_at`, `written_at` | UTC timestamps | MEMORY_MODEL: attributable, freshness |
| `provenance` | `actor` (required), `authority`, `run_id`, `evidence[]`, `source` | MEMORY_MODEL "every entry is attributable"; audit questions who/under what authority/on what evidence |
| `supersedes` | same-type record this one replaces | "supersede, never edit" (decision log, ADRs) |
| `previous_digest` | digest of the prior revision (mutable types) | per-record hash chain: what was replaced |
| `extensions` | reserved, empty in format 1 | seam for future audit metadata |
| `body` | the record, validated against its type's schema | schemas/ |
| `digest` | sha256 of the canonical envelope without itself | corruption and out-of-band edit detection |

**Record types** are declared in [`orchestration/kernel/record_types.json`](../orchestration/kernel/record_types.json):
schema plus mutability. Registered now: decision-record, evidence, failed-approach, claim and
knowledge-entry (all immutable), and task-node (mutable). `context-package` waits for OOS-0006,
because its id field is `package_id`. Domain packages may register more types later. The store has
no type-specific code.

**Supersession.** A new record names the old one in `supersedes`. The old file is never touched, and
`superseded_by` is *derived* by the store. Bodies may not set `superseded_by` themselves (it would be a
second, conflicting truth). A record can be superseded at most once.

**Mutable types** (task-node) are written with `replace(..., expected_revision=n)`. On a stale revision
the call raises `ConcurrencyConflict`. The prior revision's exact bytes are kept in `history/<type>/<id>/<rev>.json`.

## 3. Identifiers

- Portable only: `^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$`. There are no separators, no Unicode, no trailing dot and no
  Windows device names (`CON`, `NUL`, `COM1`, …).
- Unique **case-insensitively**, because Windows and macOS file systems usually fold case.
- Each schema's own `id` pattern still applies (for example `^DEC-[0-9]{4}$`).

## 4. Durability: what is actually guaranteed

| Guarantee | Mechanism | Evidence |
|---|---|---|
| A record is either fully present or absent | temp file → `fsync` → atomic install (`os.rename`, which is create-only on Windows; `os.link` on POSIX; `os.replace` for revisions) | the child process dies after the temp write: no record, temp reported by `verify()` and removable |
| Creation never overwrites | the duplicate pre-check **and** create-only installation | sabotage: the pre-check bypassed, still refused |
| Invalid records are never persisted | validation before any write | tests: nothing written on a schema error |
| Corruption is detected, not served | strict parse + envelope schema + digest + location check | truncation, edits, duplicate keys, NaN, deep nesting, non-UTF-8, moved files |
| A crashed writer cannot wedge the store | OS-released locks (msvcrt / flock) | the child dies holding the lock, and the next writer proceeds |
| Log appends are atomic per line, ordered and tamper-evident | lock, single `write`, `fsync`, seq + hash chain | concurrent appenders; torn tail; edited, removed and forged lines |

**Not guaranteed or not tested:**
- **Power-loss durability.** `fsync` is called, but unit tests cannot observe whether the OS or disk honours it.
  Removing `fsync` is not caught (`tools/store_sabotage_check.py`).
- Directory-entry durability after rename on Windows. NTFS journals metadata, but Windows cannot `fsync` a directory.
- Network file systems (SMB/NFS) and cloud-synced folders (OneDrive, iCloud, Dropbox). Locking and rename
  semantics there are **unverified**. Do not place a store root in a synced folder until this is tested.
- macOS and Linux: POSIX paths (`os.link`, `flock`, directory `fsync`) are written but **untested**.

## 5. Concurrency (local runtime phase)

- **Writers** (create, replace, append) serialize on one store-level lock (or one per log). That is correct
  across processes and threads on one machine, and released by the OS if the holder dies.
- **Readers** do not lock. Files only ever appear through atomic installs, so a reader sees an old or a new
  complete version, never a partial one.
- Tested: 5 processes × 20 creates; 6 processes racing for one id (one winner); 4 processes racing to
  replace one revision (one winner, one history entry); 4 processes × 25 log appends (contiguous seq, valid chain).
- **Not designed for:** many machines sharing one store, or high write throughput (scans are O(n) per write, which ADR-0001 accepts at this scale).

## 6. Schema evolution

- Every schema declares `x-oos-schema-version` (integer). Every record stores the version it was written with.
- **Newer than supported** → `UnsupportedSchemaVersion` (upgrade OOS). Never silently read.
- **Older** → read only if migrations are registered for each step `(schema, v) → v+1`. The migrated body is
  validated against the current schema and returned with `migrated_from`. **The file is not rewritten** on read.
  Rewriting old records is a separate, explicit operation (future work, not built).
- Changing a schema incompatibly means bumping its version and providing a migration. A schema change is a
  reviewed change like any other kernel change.

## 7. Security and trust

- Records are **data**. Loading uses `json` only (never pickle or eval). Strings that look like code stay strings.
- Fail-closed parsing: duplicate keys, NaN/Infinity, depth > 64, non-UTF-8 and oversize files (checked
  *before* reading) are all rejected.
- Size limits: 1 MiB per record, 256 KiB per log line (`record_types.json`), configurable per type.
- Ids cannot address paths outside the store (no separators, no `..`).
- The store does not judge content. Secrets must not be written (SECURITY_AND_TRUST §5): provenance and evidence
  hold *references*, never secret material. Secret scanning of change sets remains G-SCOPE's job.

## 8. Using it

```python
from oos.records import RecordStore, SchemaRegistry, load_record_types
schemas = SchemaRegistry("schemas")
store = RecordStore(root, schemas, load_record_types("orchestration/kernel/record_types.json"))
store.create("decision-record", body, provenance={"actor": "decision-engine", "authority": "D2"})
store.get("decision-record", "DEC-0007")
```

Where a store root lives (OOS workspace for orchestrator state; `.oos/` in a project for project truth) is decided
by the workspace binding and by OOS-0004 (OQ-002), not by the store.
