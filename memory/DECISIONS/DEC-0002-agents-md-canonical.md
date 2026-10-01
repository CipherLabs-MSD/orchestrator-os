# DEC-0002 — AGENTS.md is canonical; vendor files are import shims

- **Level:** D2 (scores 1/0/0/0/0/1)
- **Task:** OOS-0001 · **Decided by:** orchestrator · **Date:** 2026-10-01 · **Status:** decided

**Context.** Several agent vendors read different instruction files: `AGENTS.md` (Codex and
others) and `CLAUDE.md` (Claude Code). Keeping duplicate rule sets in sync would drift, and
it would contradict ADR-0004 (vendor neutrality).

**Options.** (1) Duplicate the rules per vendor. (2) Keep one canonical `AGENTS.md`, with
`CLAUDE.md` containing only `@AGENTS.md`. (3) Use only `AGENTS.md` and accept that Claude Code would not load it automatically.

**Choice.** Option 2.

**Consequences.** New vendors get a thin shim. Rules change in exactly one place.
