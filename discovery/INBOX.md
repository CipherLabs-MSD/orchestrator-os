# Discovery Inbox

Capture links, articles, repositories and ideas across the system ecosystem. This
human-edited inbox works immediately; Model Lab and the OOS runtime are not dependencies.

## Add an entry

Append a row using the next unused `DISC-NNN` ID (next: `DISC-002`). Use today's
date as `YYYY-MM-DD`, one sentence explaining why it is interesting, and status `NEW`.
For an idea without a URL, write `Idea — user note` as the source. Category and
related systems may be `Unclassified` and `Unknown`; capture first, refine later.
Keep IDs stable and never reuse them. Check the latest inbox before assigning an ID.
Escape any literal table separator as `\|`.

| ID | Name | Kind | URL / source | Short description | Captured | Category | Related systems | Status |
|---|---|---|---|---|---|---|---|---|
| DISC-001 | Ruflo | CANDIDATE | [GitHub](https://github.com/ruvnet/ruflo) · [MCP Market](https://mcpmarket.com/server/ruflo) | Agent orchestration framework to investigate for reusable coordination patterns; capabilities are not yet evaluated here. | 2026-10-14 | AI / Agents | Orchestrator-OS, FinanceOS | NEW |

Copy this row for the next entry:

```text
| DISC-002 | Name | CANDIDATE | URL or source | Why it is interesting | YYYY-MM-DD | Unclassified | Unknown | NEW |
```

## Meaning and boundaries

`IDEA` is a raw thought. `CANDIDATE` is an identified resource worth considering.
Neither is an approved `TASK`. This inbox is separate from the OOS task backlog
in [project/BACKLOG.md](../project/BACKLOG.md).

| Status | Meaning |
|---|---|
| NEW | Captured; not evaluated |
| PARKED | Saved for later |
| RESEARCH | Being investigated |
| EXPERIMENT | Selected for a bounded experiment |
| REFERENCE | Useful as reference material |
| ADOPT | Owner has explicitly decided to adopt; record the decision link below |
| REJECT | Decided against; retain the entry and reason |

Statuses describe triage, not execution permission. No row or status automatically
creates tasks, installs software, runs experiments or implements anything.
Research, experiments and implementation require a separately authorized task in
the relevant system, with scope and verification. Link that task back to its DISC ID.
Record decision reasons and task links below when they exist; do not invent them.

This repository is public. Store only public resources and non-sensitive ideas here;
private sources belong in an appropriate private repository.

## Notes and decisions

- DISC-001: Registered by user request. No evaluation or adoption decision yet.
