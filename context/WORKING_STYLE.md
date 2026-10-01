<!-- context-file
category: working_style
status: placeholder
entries: 0
-->
# Working Style

> **PLACEHOLDER: NOT YET SUPPLIED.** This file contains **no information about Billy**.
> Agents must not infer or invent entries. Populate only via [IMPORT_PROTOCOL.md](IMPORT_PROTOCOL.md).

**Purpose:** How Billy prefers to collaborate with AI agents and receive work.

**Typical consumers:** orchestrator escalation, release_engineering, code_review. The Context Router selects individual entries by
`applies_to_capabilities` and `scope`. It never sends this whole file.

## Prompts for curation

These are the *kinds* of entries that belong here. They are questions, not answers.

- [ ] Preferred update cadence and level of detail
- [ ] How Billy likes options presented (recommendation-first, tables, …)
- [ ] Review habits: PR size, what he reviews personally
- [ ] Tolerance for interruptions vs. batching questions
- [ ] Software-development practices he values (testing, docs, commit style)

## Entries

_None yet._

<!-- Entry format (see docs/PERSONAL_CONTEXT_MODEL.md §3):
### CTX-NNNN — <short title>
- statement:
- kind: user_preference | user_fact
- category: working_style
- scope: global | domain:<name> | project:<id>
- strength: weak | moderate | strong
- confidence: 0.0–1.0
- source:
- learned: YYYY-MM-DD
- last_confirmed: YYYY-MM-DD
- applies_to_capabilities: []
- conflicts: []
- superseded_by: null
- status: proposed | active | superseded | retired | disputed
-->
