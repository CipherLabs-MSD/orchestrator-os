# Vision

## The one-sentence version

Billy says *"Here is my vision and plan for this application. Build it as far as you
intelligently and safely can."* Orchestrator OS then runs a software-development
organization on his behalf, for long periods, with minimal prompting. It stops only
for decisions that exceed its authority or genuinely need his judgment.

## What it is, and what it is not

| It is | It is not |
|---|---|
| A control system: observe, plan, delegate, verify, learn, replan | A task runner that executes a fixed TODO list |
| An organization: roles assembled from capabilities, per task | A fixed trio of implementer, tester and reviewer |
| Evidence-driven: work is done when proven | Trust-driven: work is done when an agent says so |
| Bounded autonomy: explicit authority levels | Unbounded autonomy, or "ask the human about everything" |
| Model-independent: any capable execution backend | A wrapper around one vendor's agent |
| Project-agnostic: projects plug in | Shaped around its first pilot |
| One domain-agnostic kernel, specialized per domain (software, finance, game dev, research, …) | A separate orchestrator codebase per domain |

## End-to-end flow (target)

```
VISION / INTENT
 → understand context → determine desired outcomes → inspect current project state
 → plan → create/revise task graph → select agents/models → construct scoped context
 → delegate → execute → test → review → evaluate evidence
 → make permitted decisions → log decisions → learn → replan → continue
```

## Design commitments

1. **Plans are hypotheses.** The task graph is revised whenever evidence contradicts
   it. An obsolete plan is a defect, not a contract.
2. **Separate the knowledge layers.** User context, domain context, project truth, general
   knowledge and orchestrator state ([ARCHITECTURE §4](ARCHITECTURE.md#4-knowledge-layers-and-context-scopes),
   [KNOWLEDGE_TAXONOMY.md](KNOWLEDGE_TAXONOMY.md)).
3. **Maximum useful autonomy inside explicit boundaries.** The D1–D4 levels are a policy
   over impact, reversibility, uncertainty, cost, security and vision alignment
   ([DECISION_ENGINE.md](DECISION_ENGINE.md)).
4. **Failure produces information.** Retries are bounded. Dead ends are recorded so
   they are not repeated ([FAILURE_HANDLING.md](FAILURE_HANDLING.md)).
5. **Transactional safety and history.** Every autonomous change can be reviewed and
   reverted, through the domain's workspace binding (software: git, see
   [GIT_WORKFLOW](../domains/software-development/GIT_WORKFLOW.md)).
6. **Untrusted input stays data.** Retrieved text never becomes instructions
   ([SECURITY_AND_TRUST.md](SECURITY_AND_TRUST.md)).
7. **Domain-specialized orchestration.** Software Development, Finance, Game Development,
   Research and Creative Production orchestrators are *configurations* of one kernel
   ([ARCHITECTURE §1](ARCHITECTURE.md#1-core-architectural-principle-domain-specialized-orchestration)).
   FinanceOS is the motivating example of a domain that needs the same loop under much
   stricter authority. It is not an implementation target of OOS-0001.

## How we will know it works

See [`project/OKRS.md`](../project/OKRS.md). In short: a real pilot project advances
across multiple milestones, with a small, well-justified number of escalations, no
unauthorized actions, and every DONE task backed by evidence.

## First pilot

Demon Codex will be one of the first real projects driven by OOS. It is a *consumer*
of the core. Nothing in the core may assume Demon Codex's architecture, stack or
domain. Pilot integration is a separate milestone (M4).
