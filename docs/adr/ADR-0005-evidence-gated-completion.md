# ADR-0005 — Evidence-gated completion

- **Status:** accepted
- **Date:** 2026-10-01
- **Decision level:** D3
- **Decided by:** orchestrator (founding architect, OOS-0001)
- **Task:** OOS-0001

## Context
Agents routinely report success that is partial, untested or wrong. Over long autonomous
runs, accepting self-reports compounds errors into a graph full of false DONEs.

## Options considered
1. **Accept agent self-reports.** Cheap, and unreliable.
2. **Uniform checks (tests pass).** Better, but blind to UI, migrations, performance and intent.
3. **Task-type-specific verification gates, with evidence collected independently and bound
   to a commit SHA.**

## Decision
Option 3. See [VERIFICATION](../VERIFICATION.md). DONE is a gate verdict, never an agent claim.
G-SCOPE applies to every task.

## Consequences
- Verification infrastructure (OOS-0009) is on the critical path.
- Some tasks need Billy (G-HUMAN). These are batched to limit interruptions.
- `inconclusive` is a first-class verdict, so flaky infrastructure becomes visible.

## Rollback
Gates can be relaxed per task type. Removing G-SCOPE or G-SECURITY is D4.

## Revisit when
Gate cost dominates cycle time without catching defects, measured per gate.
