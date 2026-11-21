# ADR-0008 — Runtime language and initial execution model

- **Status:** accepted (D3, orchestrator) · owner-reviewed and merged (PR #1, 2026-10-02)
- **Date:** 2026-10-01
- **Decision level:** D3. Meaningful, reversible, inside accepted intent. It resolves OQ-006.
- **Decided by:** orchestrator (OOS-0002 spike)
- **Task:** OOS-0002
- **Evidence:** [`spikes/oos-0002/`](../../spikes/oos-0002/), [`results/win32-2026-10-01.json`](../../spikes/oos-0002/results/win32-2026-10-01.json),
  `tests/test_spike_oos0002.py`. Design: [EXECUTION_RUNTIME](../EXECUTION_RUNTIME.md).

## Context

OOS-0003 onwards needs a language and an execution model. The control plane is mostly **process
supervision and durable state**. It launches agent CLIs and SDK workers as subprocesses, streams
their events, enforces timeouts, cancels, contains failures, survives its own crashes, and resumes
long work. All of this happens under a kernel that stays domain-, vendor- and VCS-neutral (ADR-0004,
ADR-0006) and inside least-privilege owner policy (ADR-0007). Windows and macOS are first-class targets.
The development machine is Windows 11.

## Candidates

- **Python** (evaluated by executable spike, stdlib only)
- **TypeScript / Node.js** (evaluated by executable spike in plain ESM with no npm deps, so it runs
  without a build step. TypeScript adds compile-time types, not runtime behaviour.)
- Go / Rust were considered and not spiked. They give strong single-binary process control. But
  first-party agent SDKs are offered for Python and TypeScript, and a compiled toolchain slows the
  edit-test loop of AI coding agents on a design-stage system. This is reasoned, not measured.

Execution models: **A** session-oriented CLI, **B** persistent daemon, **C** hybrid (A now, with
durable state and seams for B later).

## Evidence (Windows 11, Python 3.10.6, Node 22.9.0; see EXECUTION_RUNTIME §8)

| # | Experiment | Python | Node |
|---|---|---|---|
| E2 | 8 concurrent workers: success, slow, timeout, cancel, crash, question, forced cancel, leaked grandchild | all correct; wall 1.28 s | all correct; wall 1.82 s |
| E3 | Kill a worker's tree | Job Object: tree dead | `taskkill /T`: tree dead (parent must still exist) |
| E2-H | Worker succeeds but leaves a grandchild | reaped | **grandchild survived** (`taskkill /T` cannot find it after the parent exits) |
| E4 | OOS process crashes | with Job Object: worker and grandchild die. Without: both survive. | worker dies (libuv, inferred), **grandchild survives**. No per-worker tree ownership without a native addon. |
| E5 | Journal + crash with torn write + recovery + resume | each task succeeded exactly once | not duplicated: equivalent file I/O, non-discriminating |
| E6 | Non-ASCII/space paths, stdio encoding | correct (json.dumps ASCII-escapes) | raw UTF-8 mangled by a cp1252-decoding child unless the protocol mandates UTF-8 |
| E1 | Cold start | 21 ms | 29 ms (both negligible for a session CLI) |

Pitfalls found by measurement rather than assumption:
- Descendants keep stdio pipes open, so EOF is not completion.
- `os.kill(pid, 0)` on Windows is `CTRL_C_EVENT`, not a probe.
- Windows piped stdio defaults to the locale code page.

## Trade-offs

| Factor | Python | TypeScript/Node |
|---|---|---|
| Process-tree ownership on Windows | **stdlib** (`ctypes` Job Objects): per-worker kill and no orphans on crash | external `taskkill` per kill. Descendants escape. Full parity needs a native addon or helper. |
| Async / streaming | `asyncio` (Proactor on Windows): adequate. Transport `ResourceWarning`s seen. | native event loop: excellent |
| Static typing | gradual (hints + a checker, to be adopted) | strong (TypeScript) |
| JSON Schema / records | `jsonschema` (mature), dataclasses/pydantic | `ajv` (mature), zod |
| Existing OOS tooling | validator, tests and mutation/prepublish tools are already Python stdlib | rewrite needed |
| Provider SDKs | first-party agent SDK available | first-party agent SDK available. Claude Code and Codex CLIs are Node apps, but OOS drives them as processes either way. |
| Packaging / install | needs Python ≥ 3.12 (pipx/uv) | needs Node (npm, or single-executable apps) |
| AI-agent maintainability | very good (simple, explicit, huge corpus) | very good (types help refactors) |

## Decision

1. **Runtime: Python ≥ 3.12, stdlib-first, `asyncio`.** Third-party dependencies are D2 decisions
   (dependency floor), for example `jsonschema` in OOS-0003. Platform-specific process control lives
   in one small module (Job Objects on Windows, process groups on POSIX), never in kernel logic.
   Python 3.10 reaches end of life this month, and 3.12 is supported until 2028.
2. **Execution model: C (hybrid).** Session-oriented `oos run` / `--resume` now, with a write-ahead
   journal and recovery on start. A scheduler or daemon is added later as a *trigger* for the same
   resumable run, only when scheduled or event-driven work actually exists.
3. **Provider seam:** separate worker processes in run-owned process trees, speaking a UTF-8 JSONL
   event protocol (EXECUTION_RUNTIME §3). Adapters normalize every backend (CLI or SDK) to it.

## Consequences

- OOS-0003 builds the record store in Python ≥ 3.12. The foundation tooling stays 3.10-compatible
  until the development environment is upgraded (owner action: install Python 3.12+).
- OOS-0007 adopts the event-stream refinement of the adapter contract (`events(run_id)`, with `poll` derived from it).
- OOS-0008 implements process-tree ownership, reap-on-terminal, protocol cancellation and
  side-effect-free liveness. It also collects the first macOS evidence.
- The journal is orchestrator state (ADR-0001) and follows MEMORY_MODEL §6.
- No kernel change: Git stays the software binding (ADR-0006), and providers stay adapters (ADR-0004).

## Rejected alternatives

- **TypeScript/Node as control plane.** Its strengths (types, event loop) are real. But the decisive
  Windows requirement, owning and reliably reaping worker trees including on OOS crash, needs native
  code or an external helper in Node, and it is stdlib in Python. Revisit if that changes.
- **Model B (daemon first).** It adds per-OS service installation, a long-lived credential holder and
  harder debugging. Crash recovery is needed anyway, and nothing yet requires continuous operation.
- **Model A without durable seams.** It cannot evolve to sustained autonomy without a rewrite.
- **Go / Rust.** Not justified at this stage (reasoned above, not measured).

## Migration / evolution path

Session CLI → OS-scheduled resumes → optional supervisor service (API/UI) → remote workers over the
same protocol. Each step adds a trigger or transport. The kernel, journal and protocol stay.

## Unresolved risks

- **macOS is unverified.** There are no Job Objects or `PR_SET_PDEATHSIG`, so orphan cleanup after an
  OOS crash relies on recovery killing recorded process groups. OOS-0008 must test this on a Mac.
- asyncio on Windows: transport `ResourceWarning`s at shutdown. Production needs careful process/loop lifecycle.
- Job Object assignment races if a worker spawns before assignment. The spike sends the request only
  after assignment. Production may need suspended creation.
- Nested job behaviour if OOS itself runs inside a job (some terminals/CI do). Untested.
- Python packaging for non-developer installs is unproven.
- Typing discipline must be enforced by tooling (a checker adoption is a D2 decision).

## Revisit when

- A required provider capability exists only in-process in a TypeScript SDK and cannot be wrapped as a worker.
- macOS supervision cannot meet the no-orphan requirement in Python.
- Scheduled or event-triggered work or multi-run concurrency appears. That triggers the daemon/supervisor step, not a language change.
- Distribution to non-developers makes Python packaging the dominant cost.
