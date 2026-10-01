# Import Protocol — curated user context

How Billy's existing context (ChatGPT history, notes, project retrospectives) becomes
routable entries. Tooling for this is OOS-0012. Until then the protocol is run by hand.

## Preconditions

1. **The private store exists.** Per ADR-0007 the instance lives in the private `orchestrator-context` store,
   never in the public `orchestrator-os` repository. Creating it is part of OOS-0012.
2. Billy has chosen the source material and provided it. Nothing is pulled automatically.

## Steps

| # | Step | Who | Output |
|---|---|---|---|
| 1 | **Collect.** Billy supplies an export or excerpts. Raw material stays in a private, non-routed location. | Billy | raw source (never committed to a public repo) |
| 2 | **Extract.** Propose candidate entries. Each one is an atomic `statement` with a pointer to its source passage. | agent | candidates, `status: proposed` |
| 3 | **Filter.** Drop anything that would not materially change a future decision. Drop sensitive personal details that have no decision value. | agent | shortlist + list of what was dropped and why |
| 4 | **Classify.** Assign category, kind (`user_preference` / `user_fact`), scope, strength, `applies_to_capabilities`, and confidence (based on how often and how explicitly it appears). | agent | classified candidates |
| 5 | **Detect conflicts.** Link entries in tension (`conflicts`). Do not resolve them silently. | agent | conflict pairs |
| 6 | **Review.** Billy accepts, edits or rejects each entry. Rejected entries are not stored. | **Billy** | accepted entries |
| 7 | **Commit (to the private store only).** Write accepted entries with `status: active`, `learned`, `last_confirmed`, and `source` including `confirmed-by-billy`. | agent | entries in context files |
| 8 | **Validate.** Run `python tools/validate.py`. | agent | pass |

## Ongoing maintenance

- **New statements.** When Billy states a preference during work, an agent may write it as
  `status: proposed`. It becomes routable after he confirms it.
- **Re-confirmation.** Entries with `last_confirmed` older than 12 months are surfaced
  for a quick yes, no or edit at a natural checkpoint, such as a milestone review. They are not surfaced mid-task.
- **Supersession.** A changed preference gets a new entry. The old one gets
  `status: superseded` and `superseded_by`.

## What must never enter

- Credentials, financial details, health information or third-party personal data, unless
  Billy explicitly asks and it has a decision purpose.
- Speculation ("Billy probably…").
- Project decisions disguised as preferences ("Billy wants Project Y built in engine Z").
  These belong in that project's truth layer as a project claim.
