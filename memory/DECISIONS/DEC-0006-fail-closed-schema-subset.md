# DEC-0006 — Keep a fail-closed JSON Schema subset; one validator implementation

- **Level:** D2 (scores 1/1/0/0/0/0; class `dependency_change` considered: no dependency added)
- **Task:** OOS-0003 · **Decided by:** orchestrator · **Date:** 2026-10-02 · **Status:** decided
- **Revises:** the expectation in DEC-0001 that "OOS-0003 replaces the subset validator with a full one"

**Context.** DEC-0001 introduced a stdlib subset validator for the foundation and expected a full JSON Schema
validator in the chosen runtime. ADR-0008 then chose Python, stdlib-first, where any dependency is a D2 decision.
All 16 schemas use only the subset (type, required, properties, additionalProperties, enum, pattern, items,
minimum, maximum, minLength).

**Options.**
1. Adopt the `jsonschema` package: full spec, one more dependency and an install step.
2. Keep the subset, move it into the runtime library (`oos.records.schema`), make it the **only** implementation
   (the validator tool imports it), return structured issues, and **reject at load** any schema that uses a keyword
   outside the subset.
3. Keep two implementations (tool + runtime): drift risk.

**Choice.** Option 2. A partial validator is dangerous only when it *silently ignores* rules. Failing closed at
schema load removes that risk without a dependency.

**Revisit when.** A schema genuinely needs `$ref`, `oneOf`, formats and the like. Then either extend the subset
(with tests) or adopt `jsonschema` as a D2 decision.
