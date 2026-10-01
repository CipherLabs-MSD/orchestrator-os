# OOS-0002 spike: runtime and execution model (DISPOSABLE)

> **Experimental, disposable code.** It exists only to produce evidence for
> [ADR-0008](../../docs/adr/ADR-0008-runtime-and-execution-model.md). It is **not** the
> orchestrator, and no kernel or production code may import it. The validator enforces that
> isolation. Delete or archive this directory once the runtime exists (OOS-0003 onwards).

## What is here

| File | Role |
|---|---|
| `fake_provider.py` | Stand-in for Claude Code / Codex / an SDK worker. JSON Lines over stdio, with scripted behaviours: succeed, hang, crash, ignore_cancel, ask, spawn/leave grandchild, write_file. No network, no credentials. |
| `py_runner.py` | Python candidate: asyncio supervision, Windows Job Objects via stdlib `ctypes`, append-only fsynced journal, crash recovery, experiments E1–E6 |
| `node_runner.mjs` | Node candidate (plain ESM, no npm deps): the same experiments except E5. Drives the *same* fake provider. |
| `run_spike.py` | Runs both and records sanitized results |
| `results/` | Recorded results. Architectural evidence only, not benchmarks. |

## Experiments

| ID | Question |
|---|---|
| E1 | Spawn / cold-start overhead (relevant to a session-oriented CLI) |
| E2 | Eight concurrent workers: success, slow success, hang→timeout, cooperative cancel, crash mid-stream (torn event), question/escalation, ignores cancel→forced kill, success that leaves a grandchild |
| E3 | Killing a worker: is its process tree killed too? |
| E4 | The orchestrator itself crashes: do workers become orphans? |
| E5 | Durable journal, OOS crash mid-run with a torn write, recovery classification, resume (Python only; see the note in `node_runner.mjs`) |
| E6 | Workspace path with spaces and non-ASCII, UTF-8 over stdio, Windows signal pitfalls |

## Run

```sh
python spikes/oos-0002/py_runner.py all
OOS_SPIKE_PYTHON=python node spikes/oos-0002/node_runner.mjs all
OOS_SPIKE_NODE=/path/to/node python spikes/oos-0002/run_spike.py
```

`tests/test_spike_oos0002.py` runs the decisive Python experiments in the normal test suite.
It also runs the Node experiments when `OOS_SPIKE_NODE` points to a Node binary.

## Platform coverage

| Platform | Status |
|---|---|
| Windows 11 (build 26200), Python 3.10.6, Node 22.9.0 | **tested**, see `results/win32-2026-10-01.json` |
| macOS | **unverified**. POSIX code paths (process groups, `killpg`) exist but have **not** run on macOS. Run the tests there to validate them. |
| Linux | **unverified**, same POSIX paths |
