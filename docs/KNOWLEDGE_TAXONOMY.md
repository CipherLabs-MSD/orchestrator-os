# Knowledge Taxonomy

> Answers the design question: *how does the orchestrator avoid confusing a
> user preference with a project requirement, a hard constraint, an assumption or
> an experiment?*

## 1. Why this matters

The most dangerous failure mode of a context-heavy autonomous system is
**category drift**. A soft signal ("Billy tends to like dark UIs") gets repeated through
prompts until it behaves like a hard rule ("the app must be dark-mode only"). Nobody
ever decided that. The reverse also happens: a real constraint gets treated as a
mere preference and is traded away.

So every claim the orchestrator acts on has an explicit **kind**. The kind controls
who may create the claim, how strongly it binds, and what it takes to change it.

## 2. The six kinds

*All examples in this document are hypothetical. None of them is a fact about Billy or about any real project.*

| Kind | Example | Layer | Who may create it | Binding force | How it changes |
|---|---|---|---|---|---|
| **User preference** | "Billy prefers small, reviewable PRs." | User context | Billy, or curated import with provenance | **Evidence.** Weighted input to decisions. Never binding by itself. | New evidence, Billy's confirmation, or supersession. Preferences evolve. |
| **Project preference** | "Project Y prefers Postgres over SQLite unless there is a reason not to." | Project truth | A D2/D3 decision in that project, or Billy | **Default.** Followed unless a logged reason justifies deviating | D2 log (with rationale) or ADR |
| **Project requirement** | "Project Y must support offline play." | Project truth | Billy (or an accepted product spec) | **Binding** inside the project. Violating it fails verification. | Billy only (D4). Requirements encode product intent. |
| **Hard constraint** | "Never commit secrets." "Budget cap is 0 USD for paid APIs without approval." "Target platform is Windows." | Project truth, or OOS global policy | Billy, or OOS security policy | **Inviolable.** Enforced by the Policy Guard where possible, not just requested in prompts | Billy only (D4), and recorded explicitly |
| **Current assumption** | "We assume the save format will not need migrations before v1." | Project truth (with an expiry/review trigger) | Planner or any agent, logged | **Provisional.** Acted on, but must be stated and monitored | Invalidated by evidence, which triggers a replan |
| **Experimental hypothesis** | "Hypothesis: an ECS architecture will keep frame time under 16 ms with 10k entities." | Project truth (experiment record) | Planner (D2/D3 depending on cost) | **Under test.** Must not be built on until it is confirmed | Confirmed (becomes an assumption, preference or decision), refuted (recorded in FAILED_APPROACHES), or abandoned |

## 3. Promotion rules (how one kind becomes another)

Promotion is never implicit. Every promotion is a logged decision with a cited source.

```
user preference ──(cited as evidence in a D2/D3 decision)──► project preference
project preference ──(Billy accepts as product intent, D4)──► project requirement
experimental hypothesis ──(evidence passes gate)──► current assumption / project preference
current assumption ──(evidence contradicts)──► REPLAN  (+ FAILED_APPROACHES if acted on)
anything ──(Billy declares)──► hard constraint
```

Forbidden shortcuts:

- ✗ user preference → project requirement (skips Billy's product judgment)
- ✗ user preference → hard constraint
- ✗ assumption → requirement (an assumption that is "always true" should be confirmed or turned into an ADR)
- ✗ an agent's output → any binding kind (agent output is untrusted; see [SECURITY_AND_TRUST](SECURITY_AND_TRUST.md))

## 4. Worked example

> USER_PROFILE says Billy prefers TypeScript (confidence 0.8, scope `global`, strength `moderate`).
> Project Y is a game prototype where the team must pick a language.

1. The Context Router includes that entry for the *architecture* agent only. It does not
   include it for the test-writing agent.
2. The architecture agent proposes TypeScript and cites the preference as **one piece
   of evidence**, alongside ecosystem fit, performance needs and the existing code.
3. The Decision Engine scores it: language choice for a new project has high impact and
   is only moderately reversible once code exists, so it is **D3**. It is decided autonomously
   and an ADR is written, *if* no project requirement conflicts. If Project Y's spec says
   "must run on console X" and TypeScript is unfit for that, the requirement wins. If the
   conflict cannot be resolved inside existing intent, it becomes **D4**.
4. The ADR records "TypeScript (project decision)". The preference stays a preference.
   Project Z still starts with a clean slate.

## 5. Representation

Every durable claim carries `kind` explicitly. See:

- [`schemas/knowledge-entry.schema.json`](../schemas/knowledge-entry.schema.json): user context entries (always `kind: user_preference` or `user_fact`)
- [`schemas/project-claim.schema.json`](../schemas/project-claim.schema.json): project preferences, requirements, constraints, assumptions and hypotheses
- [`schemas/decision-record.schema.json`](../schemas/decision-record.schema.json): decisions cite evidence by reference and state their kind

`user_fact` is a neutral factual entry, for example "Billy works on Windows". It is
still evidence only, and it never binds a project unless a project claim adopts it.

## 6. Conflict resolution order

When claims disagree, apply this order. A conflict that cannot be resolved by it is D4.

1. Hard constraint
2. Project requirement
3. Explicit, recent instruction from Billy for this project
4. Accepted ADR / project decision
5. Project preference
6. Current assumption (if not yet invalidated)
7. User preference, weighted by confidence × strength × scope match × recency
8. General knowledge / best practice
