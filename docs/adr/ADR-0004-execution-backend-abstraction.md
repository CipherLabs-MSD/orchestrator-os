# ADR-0004 — Vendor-neutral execution backend abstraction

- **Status:** accepted
- **Date:** 2026-10-01
- **Decision level:** D3
- **Decided by:** orchestrator (founding architect, OOS-0001)
- **Task:** OOS-0001

## Context
OOS must not depend fundamentally on one model vendor. Claude Code, Codex and future agents
differ in strengths, cost, context size and tooling. The best choice varies by task and over time.

## Options considered
1. **Build on one vendor's agent SDK.** Fastest start. Creates lock-in, and makes the core
   shaped like the vendor.
2. **Backend contract (descriptor + adapter interface) with selection by capability, cost,
   context and risk.**
3. **A generic LLM API only, with OOS building its own tool loop.** Maximum control, at the cost
   of discarding mature agent harnesses.

## Decision
Option 2. Backends are described in `orchestration/backends.json` and integrated through
adapters implementing prepare/start/poll/collect/cancel ([AGENT_MODEL §3](../AGENT_MODEL.md#3-execution-backend-abstraction)).
Option 3 remains possible as just another backend kind (`api_model`).

## Consequences
- The core speaks only in role specs, context packages and run results.
- Vendor-specific files (`CLAUDE.md`, Codex config) are thin shims onto vendor-neutral
  sources such as `AGENTS.md`.
- The first adapter (OOS-0007) must avoid leaking vendor concepts into the contract.

## Rollback
Collapse to one adapter. The contract stays and costs little.

## Revisit when
Adapters repeatedly need contract changes for one vendor's features, which would mean the contract is wrong.
