# Domain package: finance (ILLUSTRATIVE)

> **Not operational. Not a financial policy.** This sketch exists only to prove that the
> domain-agnostic kernel can host a domain with much stricter authority, without
> finance-aware kernel code. It defines **no thresholds, no trading rules and no data
> sources**. FinanceOS is neither modified nor implemented by OOS-0001.

[`domain.json`](domain.json) has `status: illustrative` and `operational: false`. The validator
rejects any profile that tries to load it, but still checks it for tighten-only composition
and classifies its golden examples with the kernel classifier.

## What the sketch shows

| Concept | Sketch content |
|---|---|
| Capabilities | `financial_research`, `portfolio_analysis`, `quantitative_analysis`, `risk_analysis`, `onchain_analysis` (names only) |
| Authority | research, read portfolio (with a grant), scenarios and hypotheses are D1. Propose transaction is D2. Prepare, execute and change risk limits are D4. Exposing private keys is **PROHIBITED**. |
| Evidence | `portfolio_risk_check` extends `check_result`. `data_source_provenance` extends `external`. `scenario_result` extends `measurement`. |
| User context | Ceiling `decision_preference`, `working_style`. Creative context can never reach finance agents. |
| Workspace binding | undecided (research archive + proposal ledger likely) |

Full discussion: [DOMAIN_PACKAGES §5.1](../../docs/DOMAIN_PACKAGES.md#51-finance-example-why-the-separation-matters-illustrative).
Turning this into a real package is OOS-0020. It needs Billy's D4 decisions on every authority rule and threshold.
