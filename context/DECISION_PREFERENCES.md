<!-- context-file
category: decision_preference
status: placeholder
entries: 0
-->
# Decision Preferences

> **PLACEHOLDER: NOT YET SUPPLIED.** This file contains **no information about Billy**.
> Agents must not infer or invent entries. Populate only via [IMPORT_PROTOCOL.md](IMPORT_PROTOCOL.md).

**Purpose:** Billy's default trade-offs and what he wants to decide personally, as input to the Decision Engine.

**Typical consumers:** decision engine, architecture, product_analysis. The Context Router selects individual entries by
`applies_to_capabilities` and `scope`. It never sends this whole file.

## Prompts for curation

These are the *kinds* of entries that belong here. They are questions, not answers.

- [ ] Speed vs. polish defaults; build vs. buy; novelty vs. proven tech
- [ ] Risk appetite for reversible vs. irreversible choices
- [ ] Cost sensitivity and any spending thresholds
- [ ] Categories of decisions Billy always wants escalated (candidates for reserved_for_billy)
- [ ] Categories he is happy to delegate entirely

## Entries

_None yet._

<!-- Entry format (see docs/PERSONAL_CONTEXT_MODEL.md §3):
### CTX-NNNN — <short title>
- statement:
- kind: user_preference | user_fact
- category: decision_preference
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
