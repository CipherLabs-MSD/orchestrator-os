# ADR-0002 — Four-layer knowledge separation

- **Status:** accepted
- **Date:** 2026-10-01
- **Decision level:** D3
- **Decided by:** orchestrator (founding architect, OOS-0001)
- **Task:** OOS-0001

## Context
Agents perform worse, and leak information, when given one giant prompt that mixes
Billy's personal preferences, project facts, general knowledge and orchestrator
bookkeeping. Worse, soft preferences drift into acting as hard requirements.

## Options considered
1. **Single shared context document.** Simple. Causes category drift and leakage, and does not scale.
2. **Four layers (user context, project truth, general knowledge, orchestrator state),
   separated by storage location and routed selectively.**
3. **Per-agent hand-written prompts.** Flexible. Unmaintainable and inconsistent.

## Decision
Option 2. Each layer has its own location, owner and lifetime
([ARCHITECTURE §3](../ARCHITECTURE.md#3-the-four-knowledge-layers-and-where-they-live)).
Information crosses layers only through explicit, logged steps, for example a decision
record citing a CTX entry as evidence. Every claim carries an explicit kind
([KNOWLEDGE_TAXONOMY](../KNOWLEDGE_TAXONOMY.md)).

## Consequences
- The Context Router becomes a required component.
- User context can be kept private and separate from public project repos.
- More structure is needed at write time, since entries need a kind, scope and provenance.

## Rollback
Layers can be concatenated if separation proves useless. The reverse would be much harder.

## Revisit when
Routing overhead clearly exceeds the benefit, measured by run outcomes compared with and without scoped packages.
