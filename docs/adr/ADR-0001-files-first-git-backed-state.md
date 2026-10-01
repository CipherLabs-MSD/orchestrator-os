# ADR-0001 — Files-first, git-backed durable state

- **Status:** accepted
- **Date:** 2026-10-01
- **Decision level:** D3
- **Decided by:** orchestrator (founding architect, OOS-0001)
- **Task:** OOS-0001

## Context
OOS needs durable memory, decision logs, a task graph and policy. They must be inspectable
by Billy, diffable, revertible, and readable by any agent from any vendor. The volume of
data is small at first. The access patterns are not yet known.

## Options considered
1. **Plain Markdown/JSON files in git, validated by JSON Schema.** Transparent, diffable,
   free history, works with every agent. Weak at concurrent writes and queries.
2. **Embedded database (SQLite).** Good queries and transactions. Opaque diffs, and harder for
   humans and agents to review.
3. **External service (DB, vector store).** Scales. Adds infrastructure, cost and secrets, and is premature.

## Decision
Option 1. Markdown for human-primary records and JSON for machine-primary records. Every
record type has a schema in `schemas/`. A stdlib-only validator enforces consistency.

## Consequences
- Every change to beliefs, decisions or policy is a reviewable commit.
- Concurrent writers need coordination (leases in orchestrator state). Orchestrator state
  may use a different store, since it is operational rather than durable truth.
- Queries are file scans. That is acceptable at the current scale.

## Rollback
Schemas make a later migration to a database mechanical: load the files and insert them.

## Revisit when
File scans become a measurable bottleneck, or concurrent-write conflicts recur across runs.
