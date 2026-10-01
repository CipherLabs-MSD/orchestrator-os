# Git Workflow: transactional safety and historical memory

Git provides two things for Orchestrator OS:

1. **Transactions.** Every autonomous change is isolated, reviewable and revertible.
2. **History.** Commits, PRs and ADRs are the durable record of what was done and why.

## 1. Branches

| Branch | Purpose | Who writes |
|---|---|---|
| `main` | canonical, **protected** | merge via reviewed PR only. Billy is the default merge authority ([DECISION_ENGINE §6](DECISION_ENGINE.md#6-integration-authority-is-separate-from-decision-authority)) |
| `oos-NNNN/<slug>` | work for one backlog item (this repo) | agents/humans |
| `task/<task-id>/<slug>` | one orchestrated task in a managed project | one agent run (lease-protected) |
| `integrate/<milestone-or-epic>` | optional staging of several verified task branches before a PR to `main` | orchestrator |
| `spike/<task-id>/<slug>` | experiments. **Never merged**, only harvested into findings. | agents |
| `wip/<run-id>` | rescue snapshot of a dirty or interrupted worktree | orchestrator |

## 2. Worktrees

- Each concurrently running task gets its **own worktree** on its own branch. Agents never
  share a working directory.
- Worktrees live outside the canonical checkout, in the OOS workspace (location set in OOS-0008).
- The canonical checkout is **read-only to agents**. It may contain Billy's
  uncommitted work.
- Worktrees are deleted only after their branch is merged, harvested (spike) or snapshotted (`wip/`).

## 3. Commits

- Small, single-purpose commits, each with a passing build where practical.
- Message: `<TASK-ID>: <imperative summary>`. The body states *why* and references DEC/ADR/EVD IDs.
- Commit trailer `Orchestrated-By: <backend>/<run-id>` on autonomous commits, so the
  history can be filtered by producer and reverted cleanly.

## 4. Acceptance into `main`

```
task branch ─► gates pass at HEAD SHA (evidence bound to SHA)
           ─► rebase on target, re-run gates if target moved
           ─► PR with: task ID, D-level, decisions, evidence links, rollback note
           ─► merge authority approves (Billy, or orchestrator for granted D1/D2 classes)
           ─► squash or merge per project setting; tag milestone completions
```

## 5. Reverting bad autonomous decisions

- Every autonomous merge is a single revertible unit (a squash commit or a merge commit).
- A decision record lists the commits that implement it, so *"undo DEC-0042"* maps to a
  concrete `git revert` set.
- Reverting is D1 if the change is unreleased and has no dependents. It is D2/D3 otherwise.
  Rewriting history is D4.

## 6. Forbidden for agents

- Direct commits or pushes to `main` or any protected branch
- `push --force` to shared branches, and history rewrites of published commits
- Deleting branches they did not create
- Changing branch protection, CI secrets or repository settings
- `git clean -fdx` or `reset --hard` on the canonical checkout
