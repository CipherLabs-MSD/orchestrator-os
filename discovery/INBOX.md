# Discovery Inbox

One human-edited entry point for resource links and ideas across the ecosystem.
Model Lab and the OOS runtime are not dependencies. Domain research registers keep
their authority; this inbox indexes them rather than replacing their decisions.

## Add a link

Ask: **“Lägg i Discovery Inbox: [link] — [optional reason]”.**
An agent updates this file under the repository workflow; this is not an automatic
capture service. Or append a row manually after reading the latest inbox.

1. Search the name, aliases and URL first (ignore trailing slash, tracking parameters
   and GitHub `.git` when comparing). Update an existing row instead of duplicating it.
   Do not merge ambiguous names without evidence. Check domain registers too.
2. Use the next unused ID: **DISC-024**. Never renumber or reuse an ID.
3. Use today's capture date, a short reason, triage `NEW`, execution `UNKNOWN`.
   For an idea use `IDEA` and `Idea — user note`; missing URLs stay `Unknown`.
   Escape literal table separators as `\|`.
4. Record provenance and scope in the notes; do not infer testing from a proposal,
   clone, installed package, or a status called TEST/SANDBOX/ADOPT.
5. Keep only public resources and non-sensitive summaries here. Preserve private
   evidence at its source. Do not install anything or create implementation tasks.

## Entries

Captured is the inbox registration date, not the original discussion or test date.
Evidence keys resolve in [HISTORICAL_IMPORT.md](HISTORICAL_IMPORT.md).
Execution describes only the cited historical evidence, not a current machine audit.

| ID | Name | Kind | URL / source | Short description | Captured | Category | Related systems | Triage | Execution | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| DISC-001 | Ruflo | CANDIDATE | [GitHub](https://github.com/ruvnet/ruflo) · [MCP Market](https://mcpmarket.com/server/ruflo) | Coordination patterns to investigate; no evaluation evidenced. | 2026-10-14 | AI / Agents | Orchestrator-OS, FinanceOS | NEW | UNKNOWN | R1 |
| DISC-002 | Kronos | CANDIDATE | https://github.com/shiyu-coder/Kronos | Discovery completed; model not run or scored in the cited record. | 2026-10-28 | Models | FinanceOS | RESEARCH | NOT_RUN | F:kronos; K |
| DISC-003 | Kha-Ching | CANDIDATE | Unknown — name supplied in current request | Identity and earlier discussion not independently recovered; do not infer a product URL. | 2026-10-28 | Unclassified | Unknown | PARKED | UNKNOWN | U |
| DISC-004 | EGO Lite | CANDIDATE | Unknown — prior local discovery report B | Browser use documented; no claim of integration into an OS. | 2026-10-28 | Software / Tools | Unknown | REFERENCE | TESTED | B |
| DISC-005 | DefiLlama | CANDIDATE | Source: FinanceOS financeos/market/llama.py | Fetcher implemented; adoption scope is the fetcher, not every data product or MCP/SDK. | 2026-10-28 | Finance / Data | FinanceOS | REFERENCE | IMPLEMENTED | D |
| DISC-006 | Frida | CANDIDATE | https://github.com/frida/frida · https://frida.re/docs/examples/macos/ | Source checkout documented; executable installation and instrumentation not verified. | 2026-10-28 | Software / Tools | Unknown | PARKED | NOT_RUN | B; I |
| DISC-007 | PennyLane | CANDIDATE | Unknown — name supplied in current request | Earlier discussion, exact resource identity and evaluation status not independently recovered. | 2026-10-28 | Unclassified | Unknown | PARKED | UNKNOWN | U |
| DISC-008 | Qiskit | CANDIDATE | Unknown — name supplied in current request | Earlier discussion and evaluation status not independently recovered; incidental third-party project excluded. | 2026-10-28 | Unclassified | Unknown | PARKED | UNKNOWN | U |
| DISC-009 | Feast | CANDIDATE | https://github.com/feast-dev/feast | Point-in-time join comparison; source TEST means intended use, not completed runtime testing. | 2026-10-28 | Research / Tools | FinanceOS | REFERENCE | NOT_RUN | F:feast |
| DISC-010 | ForecastBench | CANDIDATE | https://github.com/forecastingresearch/forecastbench | Forecast evaluation reference; not deployed. | 2026-10-28 | Research / Tools | FinanceOS | REFERENCE | NOT_RUN | F:forecastbench |
| DISC-011 | MISP admiralty-scale taxonomy v5 | CANDIDATE | https://github.com/MISP/misp-taxonomies | Two-axis source/claim vocabulary reference; license not established in source. | 2026-10-28 | Research / Tools | FinanceOS | REFERENCE | NOT_RUN | F:misp-taxonomies |
| DISC-012 | STIX 2.1 (OASIS) | CANDIDATE | https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html | Threat-intelligence specification reference; not an installed integration. | 2026-10-28 | Research / Tools | FinanceOS | REFERENCE | NOT_RUN | F:stix21 |
| DISC-013 | W3C PROV-O | CANDIDATE | https://www.w3.org/TR/prov-o/ | Provenance vocabulary reference; full standard not adopted. | 2026-10-28 | Research / Tools | FinanceOS | REFERENCE | NOT_RUN | F:w3c-prov |
| DISC-014 | RO-Crate / Workflow Run RO-Crate | CANDIDATE | https://www.researchobject.org/ro-crate/ | Rejected for the documented FinanceOS use case; retain source decision. | 2026-10-28 | Research / Tools | FinanceOS | REJECT | NOT_RUN | F:ro-crate |
| DISC-015 | edgartools | CANDIDATE | https://github.com/dgunning/edgartools | Filing and amendment semantics reference; not an installed dependency. | 2026-10-28 | Research / Tools | FinanceOS | REFERENCE | NOT_RUN | F:edgartools |
| DISC-016 | SkillsBench | CANDIDATE | https://github.com/benchflow-ai/skillsbench | Evaluation gate reference; runtime not executed in source. | 2026-10-28 | Research / Tools | FinanceOS | REFERENCE | NOT_RUN | F:skillsbench |
| DISC-017 | tradermonty/claude-trading-skills | CANDIDATE | https://github.com/tradermonty/claude-trading-skills | Trading-skills source review; no runtime execution evidenced. | 2026-10-28 | Research / Tools | FinanceOS | REFERENCE | NOT_RUN | F:tradermonty |
| DISC-018 | Look-Ahead-Bench | CANDIDATE | https://arxiv.org/abs/2601.13770 | Paper reference only; code repository not established in source. | 2026-10-28 | Research / Tools | FinanceOS | PARKED | NOT_RUN | F:lookaheadbench |
| DISC-019 | prediction-market-analysis | CANDIDATE | https://github.com/Jon-Becker/prediction-market-analysis | CONTAMINATION_HOLD in source; retain metadata only, do not read results. | 2026-10-28 | Research / Tools | FinanceOS | PARKED | NOT_RUN | F:pm-analysis |
| DISC-020 | dedupe | CANDIDATE | https://github.com/dedupeio/dedupe | Rejected for the documented FinanceOS use case; retain source decision. | 2026-10-28 | Research / Tools | FinanceOS | REJECT | NOT_RUN | F:dedupe |
| DISC-021 | Zingg | CANDIDATE | https://github.com/zinggAI/zingg | Rejected for the documented FinanceOS use case; retain source decision. | 2026-10-28 | Research / Tools | FinanceOS | REJECT | NOT_RUN | F:zingg |
| DISC-022 | anthropics/skills | CANDIDATE | https://github.com/anthropics/skills | Watch only; reuse terms unresolved in the historical source. | 2026-10-28 | Research / Tools | FinanceOS | PARKED | NOT_RUN | F:anthropics-skills |
| DISC-023 | openclaw/skills | CANDIDATE | https://github.com/openclaw/skills | Rejected listing; source recorded repository 404, not a fresh availability check. | 2026-10-28 | Research / Tools | FinanceOS | REJECT | NOT_RUN | F:openclaw-skills |

Copy this row for the next entry:

```text
| DISC-024 | Name | CANDIDATE | URL or source | Why interesting | YYYY-MM-DD | Unclassified | Unknown | NEW | UNKNOWN | Source note |
```

## Meaning and boundaries

`IDEA` is a raw thought; `CANDIDATE` identifies a resource for consideration (including
name-only captures awaiting identification). Neither is an approved `TASK`.
The authorized OOS backlog remains [project/BACKLOG.md](../project/BACKLOG.md).

| Triage | Meaning |
|---|---|
| NEW | Captured; not evaluated here |
| PARKED | Saved for later or awaiting evidence; preserve any source hold |
| RESEARCH | Discovery/research documented; does not authorize further work |
| EXPERIMENT | Selected for a bounded experiment; not evidence it ran |
| REFERENCE | Useful reference, or index to an existing implementation |
| ADOPT | Explicit adoption decision; requires decision evidence, not proof of implementation |
| REJECT | Rejected for a stated scope and reason; keep the entry |

| Execution | Meaning |
|---|---|
| UNKNOWN | No sufficient evidence about execution or implementation |
| NOT_RUN | Cited record explicitly says runtime was not executed; source inspection may exist |
| TESTED | Actual use/test documented; scope and limits in the evidence |
| IMPLEMENTED | Concrete integration code exists; does not imply live deployment or profitability |

Triage and execution are independent. A rejected candidate can have been tested;
an adopted idea can remain unimplemented. No status grants permission, starts
an experiment, installs software, creates a task or implements anything. Further
work requires a separately authorized task linked to the DISC ID. Refresh source
evidence before relying on a historical status. Preserve source-specific holds.

## Notes and decisions

- DISC-001: Existing Ruflo entry retained, including capture date and URLs; no evaluation found.
- DISC-002: Source `SANDBOX` is a proposed isolation requirement, not a completed run.
  Kronos mini/small/base and tokenizer variants remain part of this one resource.
- DISC-003, DISC-007, DISC-008: Name-only captures from this request. Historical
  import is **unverified** for these three; no upstream URL or use history inferred.
- DISC-004: Browser use in a prior discovery report supports TESTED only.
- DISC-005: Implemented FinanceOS fetcher; no inference that its MCP server or SDK was adopted.
- DISC-006: Source checkout is not a working Frida runtime; no instrumentation evidenced.
- Source `TEST` is not mapped to TESTED, and source `REFERENCE` is not mapped to IMPLEMENTED.
- Source `CONTAMINATION_HOLD` remains a hold; no upstream results were opened during import.

- DISC-014 (ro-crate): F rejects unnecessary interchange/schema maintenance for
  its use case. Historical FinanceOS decision, not an ecosystem-wide ban.
- DISC-020 (dedupe): F rejects probabilistic entity matching where a deterministic
  identifier exists. Historical FinanceOS decision, not an ecosystem-wide ban.
- DISC-021 (zingg): F records licensing concerns plus the same matching objection.
  This preserves the source decision; it is not a new license assessment.
- DISC-023 (openclaw-skills): F rejects an unresolved repository listing with
  unverified authorship/license. Its historical 404 was not rechecked in this import.
