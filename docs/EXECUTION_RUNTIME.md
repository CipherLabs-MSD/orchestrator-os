# Execution Runtime

> Status: **design, decided in [ADR-0008](adr/ADR-0008-runtime-and-execution-model.md)** (OOS-0002).
> Evidence: [`spikes/oos-0002/`](../spikes/oos-0002/) (disposable) and
> [`results/win32-2026-10-01.json`](../spikes/oos-0002/results/win32-2026-10-01.json).
> This document constrains OOS-0003 onwards. Nothing in it is implemented yet.

## 1. Decision in one paragraph

The control plane is written in **Python (≥ 3.12)**, stdlib-first, using `asyncio`. OOS starts
with **session-oriented runs**: something starts `oos run`, the run works through the task graph,
and it persists every transition to a durable journal before acting on it. It then finishes or pauses
(for a D4, a budget, or the circuit breaker) and exits. A later scheduler or daemon is only a
**trigger** for the same resumable run. It is not a second kernel. Providers are always separate
**worker processes** in a process tree the run owns, and they speak a UTF-8 JSON Lines event protocol.

## 2. Execution model (hybrid evolution, "Model C")

```
 trigger ──► oos run <project> [--resume RUN-ID]
 (Billy now;       │
  scheduler,       ├─ OBSERVE … REPLAN loop   (kernel, profile-composed policy)
  events later)    ├─ journal.append(transition) ─ fsync ─► then act
                   ├─ Dispatcher ──► worker process tree ──► provider (Claude Code, Codex, …, fake)
                   │                 (owned: Job Object / process group)
                   └─ exits when: done · all remaining work blocked on D4 · budget · breaker · Billy pause
```

| Stage | What is added | What does **not** change |
|---|---|---|
| **Now (M1–M4)** | `oos run` / `oos resume`; journal; recovery on start | — |
| Scheduled / event-triggered | an OS scheduler (Task Scheduler, launchd, cron) or webhook *invokes* `oos run --resume` | kernel, journal, provider protocol |
| Persistent service (if evidence demands it) | a small supervisor that keeps runs alive, queues triggers, hosts an API/UI | kernel, journal, provider protocol |
| Remote workers | the Dispatcher's transport changes from local spawn to a remote worker. Same protocol, same journal. | kernel |

**Invariant:** every run must be resumable from its journal alone. A daemon may make resuming
faster or automatic. It may never be the only holder of run state.

## 3. Provider run protocol (runtime seam; input to OOS-0007)

The kernel never imports a provider. A **provider adapter** turns one backend into this protocol.
For CLI agents it runs as a separate process. An in-process adapter (for example an SDK) must still
emit the same normalized events.

**Request** (first line on stdin, or an adapter call):

```
task_id · attempt · idempotency_key · profile_id · role_spec (stance, capabilities, D-ceiling)
context_package_ref (built_at_version) · workspace_ref (domain binding) · resource_scope
permissions / allowed action classes · timeout_s · budget (tokens, wall time; money = 0 per owner policy)
```

**Events** (stdout, one JSON object per line, **UTF-8**):

| Event | Meaning | Persisted to the journal? |
|---|---|---|
| `started` | worker alive, with its pid | yes (as `spawned`) |
| `progress` / `log` | liveness and human-readable progress | no (run log only) |
| `artifact` | an artifact ref was produced | yes |
| `change` | a ChangeSet ref was produced (software binding: commits on a task branch) | yes |
| `decision_proposed` | the agent proposes a decision (classified by the Decision Engine, never self-authorized) | yes |
| `question` | needs human input, which becomes an escalation (D4 path) | yes |
| `usage` | tokens / cost metadata where available | yes (budget) |
| `result` | `succeeded` · `failed` · `needs_input`, plus self-report (**not evidence**) | yes (as `terminal`) |
| `cancelled` | acknowledged a cancel request | yes (as `terminal`) |

**Control** (stdin): `{"type": "cancel"}` now. An answer message can come later, for a question
answered within the same attempt.

**Runner-derived terminal states** (the provider cannot report these): `timed_out`, `crashed`
(exit without a `result`), `cancelled_forced` (ignored cancel), and `interrupted` (found during recovery).

| Terminal | Retryable by default | Notes |
|---|---|---|
| succeeded | — | goes to the Verifier, never straight to DONE |
| failed | per failure class | provider-reported, e.g. tests fail |
| needs_input | no | an escalation is opened, and other tasks continue |
| cancelled / cancelled_forced | no | |
| timed_out | yes | counts as an attempt (FAILURE_HANDLING) |
| crashed | yes | torn trailing event counted, not fatal |
| interrupted | yes, after the workspace check | same idempotency key, attempt + 1 |

**Recommendation for OOS-0007.** The AGENT_MODEL adapter contract (`prepare/start/poll/collect/cancel`)
stays. Add an **event stream** (`events(run_id)`), and treat `poll` as derived from it. This refines
the contract. It does not change its intent.

## 4. Persistence: write-ahead journal

One append-only JSONL journal per run, flushed and `fsync`ed **before** the runner acts.
Orchestrator state (ADR-0001, MEMORY_MODEL §6) lives in the OOS workspace, not in project truth.

| Transition (in order) | Recorded before… | Fields |
|---|---|---|
| `run_started` | any work | run id, profile, trigger |
| `dispatch_intent` | spawning a worker | task, attempt, idempotency key, context package ref, workspace ref |
| `spawned` | sending the request | pid / process-tree id |
| `artifact` / `change` / `question` / `decision_proposed` / `usage` | acting on them | refs only, never secret material |
| `terminal` | the Verifier or the Planner use the outcome | status, retryable, evidence refs |
| `escalation_opened` / `_closed` | waiting or continuing | ESC id |
| `run_paused` / `run_finished` | exit | reason |

**Recovery on start** (`oos run --resume` or any start that finds an unfinished journal):

| Journal state for a task | Classification | Action |
|---|---|---|
| `terminal` present | terminal | none, never re-run |
| `dispatch_intent` without `spawned` | never_started | dispatch |
| `spawned` without `terminal` | **interrupted** | kill any surviving recorded tree, then do a **workspace check** (domain binding: the software binding inspects the task worktree). Re-dispatch with the same idempotency key, attempt + 1. |
| nothing | pending | dispatch when ready |
| torn trailing line | ignored and counted | — |

Evidence: E5 (a hard crash after 2 of 4 tasks, with a torn write) recovered to T1/T2 terminal and T3/T4
interrupted, and resumed so that every task succeeded **exactly once**.

## 5. Process supervision rules (from spike evidence)

1. **Own the whole process tree of every worker.**
   - Windows: a Job Object with `KILL_ON_JOB_CLOSE`, created by the run and assigned *before* the
     request is sent. The tree then dies even if OOS itself crashes (E4).
   - POSIX: a new session and process group (`killpg`). Orphans after an OOS crash are killed by
     recovery, from the recorded process-group ids.
2. **Reap at every terminal state.** Descendants inherit stdio handles. While they live, pipe EOF
   never arrives (E2-H; the first E4 run stalled for 60 s). Never treat EOF as "worker finished".
3. **Cancellation is a protocol message**, then a grace period, then a hard tree kill. Do not rely on
   POSIX signals: Windows has no SIGTERM-equivalent for arbitrary processes.
4. **Liveness without side effects.** On Windows `os.kill(pid, 0)` is not a probe: signal 0 is
   `CTRL_C_EVENT`, and it returned silently for both live and dead processes (E6). Use
   `OpenProcess` + `GetExitCodeProcess` on Windows, and `kill(pid, 0)` on POSIX only.
5. **UTF-8 on both ends, explicitly.** Windows decoded piped stdin as `cp1252` (E6). The protocol
   mandates UTF-8, and producers should ASCII-escape JSON.
6. **argv lists only.** No `shell=True`, no shell-syntax assumptions. Use `pathlib` paths. Workspaces
   with spaces and non-ASCII names were tested (E6).
7. **Least privilege for workers.** The environment is constructed per task: no inherited secrets,
   and credentials are injected per task only (SECURITY_AND_TRUST §5, owner policy).

## 6. Concurrency

`asyncio` supervision: one coroutine per worker, workers in separate processes. The task graph decides
what may run in parallel (TASK_GRAPH §4). E2 ran 8 workers concurrently: success, slow success,
timeout, cooperative cancel, crash, question, forced cancel and a leaked grandchild. Each reached the
correct terminal state, and one failing did not disturb the others. Production code uses structured
concurrency (`asyncio.TaskGroup`, Python ≥ 3.11) and a bounded worker pool.

## 7. Cross-platform matrix

| Concern | Windows 11 | macOS | Linux |
|---|---|---|---|
| Spawn, stream events, timeout, cancel, crash classification | **tested** (Python + Node) | inferred (POSIX paths written, not run) | inferred |
| Process-tree kill | **tested**: Job Object (Python, stdlib ctypes); `taskkill /T` (Node) | inferred: process group / `killpg` | inferred |
| No orphans after an OOS crash | **tested**: Job Object kills the tree; without it the worker and grandchild survive | **open risk**: no Job Objects, no `PR_SET_PDEATHSIG`. Recovery must kill recorded groups. | documented option: `PR_SET_PDEATHSIG` / cgroups (unverified) |
| Durable journal + recovery | **tested** (Python) | inferred (same stdlib calls) | inferred |
| Non-ASCII / space paths, UTF-8 stdio | **tested** | inferred (UTF-8 is the default there) | inferred |
| Background execution | documented: Task Scheduler / service (not needed yet) | documented: launchd (not needed yet) | documented: systemd / cron |

**macOS is unverified.** Running `python -m unittest discover tests` on a Mac exercises the POSIX
branches of the spike, and is the first macOS evidence to collect (OOS-0008).

## 8. Measurements (architectural evidence only)

One Windows 11 machine, tiny synthetic workloads, 10 samples, medians. **Not** performance data.

| Measure | Python 3.10.6 | Node 22.9.0 |
|---|---|---|
| Runtime cold start (`-c pass` / `-e 0`) | 21.4 ms | 29–30 ms |
| Spawning the Python fake provider (process creation) | — | 21.9 ms |
| Timeout 1.0 s → worker tree dead | 1.03 s (Job Object) | 1.37 s (async `taskkill`) |
| Ignored cancel (grace 0.5 s) → forced kill | 0.90 s | 1.29 s |
| Leaked grandchild after a successful worker | reaped (Job Object) | **survived**. `taskkill /T` cannot find it after its parent exits. |
| OOS crash → worker / grandchild | both die (Job Object) | worker dies (libuv job, inferred), **grandchild survives** |
| Third-party dependencies used by the spike | none | none |
