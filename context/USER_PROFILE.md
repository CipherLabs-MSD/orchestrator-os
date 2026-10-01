<!-- context-file
category: profile
status: placeholder
entries: 0
-->
# User Profile

> **PLACEHOLDER: NOT YET SUPPLIED.** This file contains **no information about Billy**.
> Agents must not infer or invent entries. Populate only via [IMPORT_PROTOCOL.md](IMPORT_PROTOCOL.md).

**Purpose:** Stable, neutral facts about Billy that affect how work should be planned or communicated.

**Typical consumers:** intake, escalation, most planners. The Context Router selects individual entries by
`applies_to_capabilities` and `scope`. It never sends this whole file.

## Prompts for curation

These are the *kinds* of entries that belong here. They are questions, not answers.

- [ ] Working environment(s): OS, hardware constraints, tools in daily use
- [ ] Roles Billy plays across projects (owner, designer, reviewer, …)
- [ ] Availability and response-time expectations for escalations
- [ ] Languages Billy prefers for communication
- [ ] Organizations or brands work is published under (only if decision-relevant)

## Entries

_None yet._

<!-- Entry format (see docs/PERSONAL_CONTEXT_MODEL.md §3):
### CTX-NNNN — <short title>
- statement:
- kind: user_preference | user_fact
- category: profile
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
