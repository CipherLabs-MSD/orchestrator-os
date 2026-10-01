# Task Graph

> A flat TODO list cannot express *why* work exists, what it depends on, what can run
> in parallel, or what to throw away when an assumption breaks. The task graph can.

Schema: [`schemas/task-node.schema.json`](../schemas/task-node.schema.json).

## 1. Node hierarchy

```
GOAL         why: the change in the world Billy wants        ("Players can play a full run")
 └ OUTCOME   measurable result that shows the goal is met    ("A new player completes run 1 in < 20 min")
    └ MILESTONE  coherent, demonstrable increment             ("M2: playable vertical slice")
       └ EPIC    a body of work inside a milestone             ("Combat system")
          └ TASK one agent run's worth of work, verifiable     ("Implement damage resolution")
             └ VALIDATION  how the task (or outcome) is proven ("unit tests G-TEST + playtest G-HUMAN")
```

- GOAL and OUTCOME come from Intake. Changing them is D4 (vision).
- MILESTONE and EPIC belong to the Planner. Restructuring them is D2/D3, depending on scope.
- A TASK must fit in one agent run. If it does not, the Planner splits it.
- VALIDATION nodes attach to TASKs **and** to OUTCOMEs. An outcome is met only when its
  own validation passes, even if every task underneath is DONE.

## 2. Edges

| Edge | Meaning | Effect |
|---|---|---|
| `parent` | hierarchy | roll-up of status and progress |
| `depends_on` | hard prerequisite | node is not READY until all targets are DONE |
| `validates` | VALIDATION → TASK/OUTCOME | target cannot be DONE until the validation passes |
| `assumes` | node → assumption (project claim) | if the assumption is invalidated, the node is marked `needs_replan` |
| `informs` | soft relation (spike → decision) | context routing hint only, never blocking |

`depends_on` must form a DAG. The validator enforces this for the OOS backlog.

## 3. Task states

```
proposed ──► ready ──► in_progress ──► verifying ──► done
   │           │            │              │
   │           ▼            ▼              ▼
   │        blocked ◄── failed ◄────── rejected (gate failed → back to ready with findings)
   ▼
cancelled / superseded   (terminal; superseded_by points to the replacement)
```

- `ready` is **computed**: every `depends_on` is done, no open D4 blocks it, and it has an owner capability.
- `done` requires a passing gate verdict that references evidence. An agent cannot set it.
- `failed` carries an attempt count. The retry budget is in [FAILURE_HANDLING](FAILURE_HANDLING.md).
- `needs_replan` is a flag, not a state. It can be set on any non-terminal node.

## 4. Parallelism

```
ready_set   = {t ∈ TASK | state=ready}
parallel_ok = pairs with disjoint resource_scope (software: files/dirs; other domains: datasets, documents, ledgers)
              ∧ no shared exclusive resource (software: DB migration, lockfile, schema)
```

Each parallel task runs in its own isolated Workspace (software binding: a worktree, see
[GIT_WORKFLOW](../domains/software-development/GIT_WORKFLOW.md)). Tasks with overlapping
resource scope are serialized, or the Planner refactors the split. A
lease (stored in orchestrator state) prevents two runs from claiming the same task.

## 5. Revision: plans are hypotheses

The graph is **revised, not just executed**. Every structural change is a revision record:

```
REV-NNNN
  trigger:    evidence | failed_approach | assumption_invalidated | billy_instruction | scope_discovery
  evidence:   [EVD-…, FAILED-…]
  changes:    add/remove/split/merge/reparent/re-dependency nodes
  level:      D-level of the revision itself
  rationale:
```

Replanning triggers (checked each loop at ORIENT):

1. An assumption a node `assumes` is invalidated.
2. A task fails beyond its retry budget, or a validation reveals a wrong premise.
3. Observed project state contradicts the graph (code exists that the graph says is not built, or the reverse).
4. Billy changes intent (GOAL/OUTCOME edits).
5. Scope discovery: a task reveals required work that is not in the graph.

Cancelled or superseded nodes are kept. That history explains why the graph looks
the way it does.

## 6. Storage

- v0 (OOS-0001): the OOS project's own backlog is `project/backlog.json` (a DAG of
  TASK-level items with milestone tags) plus `project/BACKLOG.md` as the human view.
- Managed projects (from OOS-0004 on): in the project's `ProjectStore`. For repository-backed
  projects that means `.oos/graph/`, one file per node or a single JSON document. That choice belongs to OOS-0004.
- Task types and their gates come from the profile's composed verification (kernel + domains).
