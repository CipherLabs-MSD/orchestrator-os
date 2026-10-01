# DEC-0001 — Stdlib-only Python validator for foundation artifacts

- **Level:** D2 (scores I/R/U/C/S/V = 1/0/0/0/0/0; class `dependency_change` floor D2)
- **Task:** OOS-0001 · **Decided by:** orchestrator · **Date:** 2026-10-01 · **Status:** decided

**Context.** The foundation needs automated consistency checks: schemas parse, registries
conform, cross-references resolve, the backlog is a DAG, and context files contain no
unsanctioned entries. The machine has Python 3.10 without `jsonschema` or `pytest`.
No implementation language has been chosen yet (that is OOS-0002).

**Options.**
1. Python stdlib only, with a minimal JSON Schema subset validator plus `unittest`.
2. Python with `jsonschema` and `pytest`. This adds dependencies and an install step before OOS-0002.
3. No automation, only manual review. That would violate ADR-0005.

**Choice.** Option 1. The schemas deliberately use only the subset the validator implements
(type, required, properties, additionalProperties, enum, pattern, items, minimum/maximum, minLength).

**Consequences.** This does not prejudge OOS-0002. OOS-0003 replaces the subset validator with a
full one in whatever runtime is chosen.

**Evidence.** `python tools/validate.py` output in HANDOFF.md.
