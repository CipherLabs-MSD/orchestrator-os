# Historical import — 2026-10-28

## Scope and authority

Continuation of OOS-0021 by direct owner request. D1: reversible documentation,
outside the kernel, with no policy/runtime/schema/dependency changes. Revert this
commit to undo the import without removing the original Ruflo capture.

Existing inbox found at `discovery/INBOX.md`, local commit `573af75`, branch
`oos-0021/discovery-inbox`; reused without a new repo, checkout or competing inbox.
GitHub default-branch contents lookup returned 404 for this path, and branch search
returned main, oos-0001/foundation and oos-0003/record-store (no discovery branch).
The previous inbox is a local delivery, not a merged upstream feature. The original
handoff already records the UniversalSystems/Idea-Explorations location comparison.

FinanceOS has an existing curated domain research register. It remains authoritative
for its evaluation details, rejections and holds. The inbox contains only a thin index
and historical summaries; it must not become a second evaluation engine. No new
domain resource register is created. No Model Lab dependency is introduced.

## Evidence ledger

These are inspected source records, not fresh upstream product evaluations. Private
source documents remain at their source: no full reports, user context, credentials,
study results or raw datasets are copied. Logical repo-relative locators and hashes
allow an authorized reader to find and verify the inspected versions. No claim that
private locators are public links. No external candidate links are synthesized.

| Key | Source locator | SHA-256 of inspected file |
|---|---|---|
| F | FinanceOS: `docs/external-resource-intelligence-registry.json` | `582a3d402661854eadf445d11520f8239f7dc85a5580f4026d246e04e2347f8e` |
| K | FinanceOS: `docs/kronos-model-lab-discovery.md` | `e6a41826eeedbc0291ad178cdb29bfa0e2dd3f26a6c2ec4cebbc780b615a43c6` |
| D | FinanceOS: `financeos/market/llama.py` | `2b5b6d7e8788fe310b3db7d90b759acac4db5ee625e6672bb4889ef328804b32` |
| B | Bill-OS local report: `DISCOVERY-2026-10-16.md` | `e87acdcb9b2c5eebfc01413693b22afab1a4cbb9954724e44211568309d0bff8` |
| I | System-Builder-OS local inventory: `REPOSITORY-INVENTORY.md` | `91841214a38375d42b6aba01df337b84552978e29b9f0eb07eaf940d5bd67b10` |

`F:<resource_id>` means the exact resource object in F, not a claim about all
resources from that organization. F is dated 2026-08-15. K is dated 2026-08-15;
it explicitly says nothing implemented, model not run or scored. D contains the
actual fetcher implementation; ingestion/tests elsewhere were not rerun in this
task, and no live API was queried. B is dated 2026-10-16, tables in sections 2 and 4
record browser use and Frida limitations. I's frida inventory row supplies the
upstream source-checkout URL. Local evidence is a snapshot, not a current machine
installation inventory. FinanceOS source checkout HEAD at inspection:
`918050fbe3a8b10b2d976feef76a1c92ecfa2869`; F, K and D had no working-tree changes.

- R1: Existing inbox commit `573af75` plus the supplied source conversation:
  Ruflo links and original registration confirmed; no new technical claims added.
- U: Direct owner request, 2026-10-28, supplies the names Kha-Ching, PennyLane and
  Qiskit. The accessible source-conversation page contains Ruflo discussion only.
  Earlier messages behind content-reference placeholders could not be recovered.
  Searches of the relevant local FinanceOS/worktrees, ModelSync, UniversalSystems,
  System-Builder-OS and Idea Explorations documentation did not establish earlier
  discussion for these three. An incidental Qiskit-named third-party project in a
  raw discovery corpus does not establish Qiskit evaluation. Keep these captures
  explicitly unresolved rather than assigning a familiar product URL by guesswork.

## Import controls and result

- 23 entries total: original Ruflo, seven further requested names, fifteen further curated
  resources from F. Kronos appears in F but is imported once as DISC-002.
- 20 entries have historical evidence; the three U entries are name-only captures,
  **not verified historical imports**. No claim of exhaustive conversation recovery.
- All 16 resources in F are represented once. Raw discovery sweeps and unrelated
  third-party model forks are excluded; Kronos checkpoint variants are not new IDs.
- F's exact status and `verified.runtime_executed=false` were inspected per row.
  TEST is intended comparison use; SANDBOX is isolation intent. Neither proves a run.
- EGO Lite is TESTED for documented browser use. DefiLlama is IMPLEMENTED for its
  fetcher only. No candidate is newly adopted, tested, installed or implemented.
- Existing REJECT decisions are scoped to FinanceOS; they are not general product
  verdicts. The original reasons stay in F. CONTAMINATION_HOLD is retained without
  opening upstream result-bearing material.
- URLs copied exactly from existing source records (including the historically
  rejected openclaw URL), not asserted currently reachable. Unknown URLs stay unknown.
- No candidate-generated tasks, integrations, installations or automated jobs.

## Adding the next resource

Use the instructions and next unused ID in [INBOX.md](INBOX.md). Check name, aliases,
canonical URL and domain register before appending. Update the evidence and existing
row when a missing identity or execution status is resolved. Do not create another
inbox or convert a source's proposed TEST into evidence of completed testing.
