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
