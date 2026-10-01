# ADR-0003 — Authority separate from capability

- **Status:** accepted
- **Date:** 2026-10-01
- **Decision level:** D3
- **Decided by:** orchestrator (founding architect, OOS-0001)
- **Task:** OOS-0001

## Context
Modern coding agents can run shells, push code, call APIs and spend money. If permission
followed capability, the most capable agent would be the most dangerous one. Agents also
read untrusted text that may try to steer them.

## Options considered
1. **Trust the agent's judgment** via prompt instructions. Easy to bypass, and fails under injection.
2. **Separate authority model:** D-levels for decisions, plus enforced tool, path and
   ref permissions per role, applied by a Policy Guard outside the agent.
3. **Human approval of every action.** Safe, and defeats the purpose of autonomy.

## Decision
Option 2. Capabilities describe work. Authority (D1–D4, tool permissions, write scopes,
integration rights) is assigned per role and task and enforced outside the model. The system
cannot raise its own authority. Changes to policy files are D4.

## Consequences
- Implementation needs an enforcement layer (OOS-0008), not just prompt text.
- Some useful actions are slower because they wait for D4. Calibration (OOS-0005) tunes this.

## Rollback
Loosening is always possible through D4 policy changes. Tightening after an incident is harder, which is why we start tight.

## Revisit when
Pilot data shows escalations that Billy consistently waves through. Those classes can be lowered.
