# context/ — User Context Layer (Billy)

**Layer:** user context ([KNOWLEDGE_TAXONOMY](../docs/KNOWLEDGE_TAXONOMY.md)).
**Model:** [PERSONAL_CONTEXT_MODEL](../docs/PERSONAL_CONTEXT_MODEL.md).
**Schema:** [`schemas/knowledge-entry.schema.json`](../schemas/knowledge-entry.schema.json).

> ⚠️ **PLACEHOLDERS ONLY.** Nothing in this directory is a fact about Billy yet.
> No agent may infer, invent or "fill in" entries. Entries arrive only through
> [IMPORT_PROTOCOL.md](IMPORT_PROTOCOL.md), with Billy's acceptance.
>
> ⚠️ **This repository is public. Billy's actual personal context never lives here.**
> Owner decision ([ADR-0007](../docs/adr/ADR-0007-initial-owner-policy.md) §1): real entries live in a separate
> **private** store, working name `orchestrator-context` (not yet created; OOS-0012). This directory
> holds only the file structure, placeholders and fictional examples. It is the template the private store follows.

## Rules

- Everything here is **evidence**, never a project requirement.
- Agents receive individual entries selected by the Context Router, never whole files.
- Only `status: active` entries are routable.
- Each file starts with a `context-file:` status block that the validator checks.

| File | Category |
|---|---|
| [USER_PROFILE.md](USER_PROFILE.md) | `profile` |
| [CREATIVE_DNA.md](CREATIVE_DNA.md) | `creative` |
| [WORKING_STYLE.md](WORKING_STYLE.md) | `working_style` |
| [DECISION_PREFERENCES.md](DECISION_PREFERENCES.md) | `decision_preference` |
| [LONG_TERM_VISION.md](LONG_TERM_VISION.md) | `long_term_vision` |
