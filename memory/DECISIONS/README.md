# Decision log

D2 decisions are recorded here as `DEC-NNNN-<slug>.md`. D3 and D4 decisions are ADRs in
[`docs/adr/`](../../docs/adr/) and are indexed below. Schema:
[`schemas/decision-record.schema.json`](../../schemas/decision-record.schema.json).

## D2 decisions

| ID | Title | Task | Date |
|---|---|---|---|
| [DEC-0001](DEC-0001-stdlib-python-validator.md) | Stdlib-only Python validator for foundation artifacts | OOS-0001 | 2026-10-01 |
| [DEC-0002](DEC-0002-agents-md-canonical.md) | AGENTS.md is canonical; vendor files are import shims | OOS-0001 | 2026-10-01 |
| [DEC-0003](DEC-0003-addendum-implementation-choices.md) | Implementation choices for the domain-specialization addendum | OOS-0001 | 2026-10-01 |

## ADR index (D3/D4)

| ADR | Title | Level |
|---|---|---|
| [ADR-0001](../../docs/adr/ADR-0001-files-first-git-backed-state.md) | Files-first, git-backed durable state | D3 |
| [ADR-0002](../../docs/adr/ADR-0002-four-layer-knowledge-separation.md) | Four-layer knowledge separation | D3 |
| [ADR-0003](../../docs/adr/ADR-0003-authority-separate-from-capability.md) | Authority separate from capability | D3 |
| [ADR-0004](../../docs/adr/ADR-0004-execution-backend-abstraction.md) | Vendor-neutral execution backend abstraction | D3 |
| [ADR-0005](../../docs/adr/ADR-0005-evidence-gated-completion.md) | Evidence-gated completion | D3 |
| [ADR-0006](../../docs/adr/ADR-0006-domain-agnostic-kernel.md) | One domain-agnostic kernel plus domain specialization | D3 |
