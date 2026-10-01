# Initial OKRs / Outcomes

> Targets marked *(proposed)* are starting hypotheses for Billy to adjust. They are
> not commitments he has made.

## O1: A foundation that implementation can build on without redesign (M0)

| KR | Measure | Target |
|---|---|---|
| KR1.1 | Every subsystem in VISION has a design doc and, where it has records, a schema | 100% |
| KR1.2 | Policy files cross-validate (gates, profiles and capabilities resolve. Golden decision examples classify as documented.) | validator passes |
| KR1.3 | Backlog items trace to milestones and form a DAG | validator passes |
| KR1.4 | Invented facts about Billy in `context/` | 0 |
| KR1.5 | Domain vocabulary or project names in kernel JSON/schemas. Domain packages that loosen kernel policy. | 0 (validator) |

## O2: Evidence-gated autonomy works for one task (M1)

| KR | Measure | Target |
|---|---|---|
| KR2.1 | Tasks reaching DONE without a gate verdict bound to their artifact version | 0 |
| KR2.2 | Policy Guard denials of seeded forbidden actions (push to main, write outside scope, secret in diff) | 100% denied |
| KR2.3 | Seeded D4 scenarios that produce a complete escalation package | 100% |

## O3: Right context, not maximum context (M2–M3)

| KR | Measure | Target |
|---|---|---|
| KR3.1 | User-context entries routed to a profile that disallows their category (golden tests) | 0 |
| KR3.2 | Median context package size vs. naive "everything relevant to the project" | ≤ 25% *(proposed)* |
| KR3.3 | Runs reporting insufficient context that needed more than one re-route | ≤ 10% *(proposed)* |

## O4: Real progress with justified escalation (M4)

| KR | Measure | Target |
|---|---|---|
| KR4.1 | Pilot milestones completed with exit evidence | ≥ 1 |
| KR4.2 | DONE tasks reopened within 2 weeks | ≤ 10% *(proposed)* |
| KR4.3 | Escalations Billy rates as "rightly escalated" | ≥ 80% *(proposed)* |
| KR4.4 | Unauthorized actions (D4 classes taken without approval) | 0 |

## O5: One kernel, many domains (M5)

| KR | Measure | Target |
|---|---|---|
| KR5.1 | Kernel lines changed to onboard the second domain, excluding ADR-approved general mechanisms | 0 |
| KR5.2 | Authority rules in a factory-drafted package activated without Billy's approval | 0 |
