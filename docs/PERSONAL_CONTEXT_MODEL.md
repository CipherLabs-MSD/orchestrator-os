# Personal Context Model

> How Billy-specific knowledge enters the system, stays correct over time, and
> reaches only the agents that need it.

## 1. Goals and non-goals

**Goals**

- Better decisions. Personal context exists only to the extent that it improves
  orchestrator decisions: naming, aesthetics, trade-off defaults, collaboration style,
  and what Billy will want escalated.
- **Provenance.** Every entry says where it came from and when.
- **Evolution.** Preferences change. Entries are confirmed, weakened, superseded or retired.
- **Selective retrieval.** A naming agent may get creative DNA. A migration agent gets none of it.

**Non-goals**

- Surveillance, or a complete biography.
- Storing raw chat history. Raw exports are *source material*, curated offline and never
  loaded into agent context.
- Inferring traits Billy has not stated or confirmed.

## 2. Files

The canonical files are listed below. During OOS-0001 they contain **placeholders only**.

| File | Holds | Typical consumers (capabilities) |
|---|---|---|
| `context/USER_PROFILE.md` | Stable neutral facts: environment, roles, constraints on Billy's time | most planners, escalation |
| `context/CREATIVE_DNA.md` | Aesthetic, tone, naming, worldbuilding and design sensibilities | ux, frontend, game_development, product_analysis |
| `context/WORKING_STYLE.md` | How Billy likes to collaborate: update cadence, verbosity, review habits | escalation, release_engineering, orchestrator itself |
| `context/DECISION_PREFERENCES.md` | Trade-off defaults (speed vs. polish, build vs. buy), risk appetite, what he wants to be asked about | decision engine, architecture, product_analysis |
| `context/LONG_TERM_VISION.md` | Long-horizon ambitions that should shape cross-project choices | intake, product_analysis, architecture (only at milestone planning) |

## 3. Entry model

Each file contains entries that conform to
[`schemas/knowledge-entry.schema.json`](../schemas/knowledge-entry.schema.json).
They are written in Markdown as follows. *The entry below is illustrative only. It is not a fact about Billy.*

```markdown
### CTX-0001 — (EXAMPLE) Prefers small, reviewable PRs
- statement: (EXAMPLE) Billy prefers small, reviewable pull requests over large batched ones.
- kind: user_preference
- category: working_style
- scope: global                # global | domain:<name> | project:<id>
- strength: strong             # weak | moderate | strong
- confidence: 0.9              # how sure we are that this is true of Billy (0–1)
- source: example-only (a real entry cites e.g. chatgpt-export/<date>/<conversation> + confirmed-by-billy)
- learned: 2026-10-05
- last_confirmed: 2026-10-05
- applies_to_capabilities: [release_engineering, code_review]
- conflicts: []
- superseded_by: null
- status: active               # active | superseded | retired | disputed
```

### Field semantics

| Field | Meaning | Why it exists |
|---|---|---|
| `statement` | One falsifiable sentence, written about Billy rather than about a project | Forces an atomic, checkable claim |
| `kind` | `user_preference` or `user_fact` | Keeps the [taxonomy](KNOWLEDGE_TAXONOMY.md) explicit. Both kinds are evidence only. |
| `category` | Which file or theme it belongs to | Routing |
| `scope` | Where it plausibly applies | Stops a game-art preference from steering a CLI tool |
| `strength` | How much Billy cares | Weight in trade-offs |
| `confidence` | How sure we are that it is true | Separates "said once, offhand" from "repeated and confirmed" |
| `source` | Provenance: export file, conversation, date, or `stated-directly` | Auditability. Lets Billy correct the root. |
| `learned` / `last_confirmed` | When it entered, and when it was last validated | Recency decay. Triggers re-confirmation of old entries. |
| `applies_to_capabilities` | Capability tags that may receive it | Primary routing key for the [Context Router](CONTEXT_ROUTER.md) |
| `conflicts` | IDs of entries in tension with this one | Conflicts are made visible, not silently resolved |
| `superseded_by` | Replacement entry | Evolution without losing history |
| `status` | Lifecycle | Only `active` entries are routable |

### Effective weight (used by the Decision Engine)

```
weight = confidence × strength_factor × scope_match × recency_factor
  strength_factor: weak 0.3 · moderate 0.6 · strong 1.0
  scope_match:     exact project 1.0 · matching domain 0.8 · global 0.6 · mismatched 0 (not routed)
  recency_factor:  1.0 if confirmed ≤ 12 months, then decays toward 0.5
```

These constants are starting hypotheses. OOS-0005 calibrates them. A preference's
weight never exceeds a project claim's. See the conflict order in
[KNOWLEDGE_TAXONOMY §6](KNOWLEDGE_TAXONOMY.md#6-conflict-resolution-order).

## 4. Import pipeline (later; designed now)

See [`context/IMPORT_PROTOCOL.md`](../context/IMPORT_PROTOCOL.md) for the operational steps.

```
ChatGPT export / notes (raw, private, never routed)
   → extraction: candidate entries, each with a source quote pointer
   → filter: "does this materially improve a future decision?"; drop if not
   → Billy review: accept / edit / reject   ← mandatory for every entry
   → write entry with provenance + status=active
   → validator: schema, unique IDs, no orphan conflicts
```

No entry becomes `active` without Billy's acceptance. An agent may *propose* a context
entry, for example after Billy states a preference in conversation. The proposal lands as
`status: proposed` and is not routable until he confirms it.

## 5. Contamination controls

0. **Domain ceiling first.** Each domain package declares which user-context categories may
   ever reach its agents (`user_context_ceiling`). The finance sketch, for example, excludes
   `creative` entirely. See the relevance pipeline in [CONTEXT_ROUTER §6](CONTEXT_ROUTER.md#6-user-context-relevance-pipeline).

1. **Routing by tag, not by file.** Agents never receive "all of CREATIVE_DNA". They
   receive the entries whose `applies_to_capabilities` and `scope` match the task.
2. **Citation on use.** When a preference influences a decision, the decision record
   cites the entry ID. That makes the influence auditable and reversible.
3. **No back-writing.** Project outcomes never edit user context automatically.
   "Project Y chose Postgres" is not evidence that Billy likes Postgres.
4. **Privacy.** The user-context *instance* lives in the private store `orchestrator-context`
   (owner decision, ADR-0007). The public repo's `context/` holds schemas, placeholders and
   fictional examples only.
5. **Provider clearance.** Only backends cleared by owner policy (`trust.user_context_ok`) may
   receive entries, and only the task-relevant ones the router selects. They never get the full profile by default.
