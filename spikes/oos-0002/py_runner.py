#!/usr/bin/env python3
"""DISPOSABLE SPIKE CODE (OOS-0002). Not production. Do not import from the kernel.

Python candidate runner. Stdlib only. Exercises the OOS-0002 questions:

  E1 spawn latency            E4 orchestrator crash vs. orphaned workers
  E2 concurrent workers       E5 durable journal + crash recovery + resume
  E3 process-tree termination E6 paths with spaces / non-ASCII, signal pitfalls

Usage:  python spikes/oos-0002/py_runner.py [all|e1|e2|e3|e4|e5|e6] [--json]
Internal sub-commands (spawned by experiments): crash-child, journal-run.
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROVIDER = HERE / "fake_provider.py"
IS_WINDOWS = os.name == "nt"
# Spawn workers with the *base* interpreter. On Windows a venv python.exe is a launcher that
# starts the real interpreter as a child, which can be born before Job Object assignment and
# escape the tree (found in OOS-0003 under Python 3.14, LRN-0009). Production must close that
# race itself (suspended creation or a job-list attribute), see EXECUTION_RUNTIME §5.
WORKER_PY = getattr(sys, "_base_executable", None) or sys.executable

# ----------------------------------------------------------------------------- process control
if IS_WINDOWS:
    import ctypes
    from ctypes import wintypes

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _k32.CreateJobObjectW.restype = wintypes.HANDLE
    _k32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    _k32.OpenProcess.restype = wintypes.HANDLE
    _k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    _k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    _k32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    _k32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    _k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    _k32.CloseHandle.argtypes = [wintypes.HANDLE]

    class _IO(ctypes.Structure):
        _fields_ = [(n, ctypes.c_ulonglong) for n in ("r", "w", "o", "rb", "wb", "ob")]

    class _BASIC(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]

    class _EXT(ctypes.Structure):
        _fields_ = [("Basic", _BASIC), ("Io", _IO), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]


class ProcessTree:
    """Owns a worker and everything it spawns. Windows: a Job Object with KILL_ON_JOB_CLOSE,
    so the tree dies even if *this* process crashes. POSIX: a new session/process group."""

    def __init__(self) -> None:
        self.job = None
        if IS_WINDOWS:
            self.job = _k32.CreateJobObjectW(None, None)
            info = _EXT()
            info.Basic.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            ok = _k32.SetInformationJobObject(self.job, 9, ctypes.byref(info), ctypes.sizeof(info))
            if not ok:
                raise OSError(ctypes.get_last_error(), "SetInformationJobObject failed")

    @staticmethod
    def spawn_kwargs() -> dict:
        return {} if IS_WINDOWS else {"start_new_session": True}

    def adopt(self, pid: int) -> None:
        if IS_WINDOWS:
            h = _k32.OpenProcess(0x0100 | 0x0001, False, pid)  # PROCESS_SET_QUOTA | PROCESS_TERMINATE
            if not h or not _k32.AssignProcessToJobObject(self.job, h):
                raise OSError(ctypes.get_last_error(), "AssignProcessToJobObject failed")
            _k32.CloseHandle(h)

    def kill_tree(self, pid: int) -> None:
        if IS_WINDOWS:
            _k32.TerminateJobObject(self.job, 1)
        else:
            import signal
            try:
                os.killpg(os.getpgid(pid), signal.SIGKILL)
            except ProcessLookupError:
                pass


def pid_alive(pid: int) -> bool:
    """Liveness WITHOUT side effects. NB: on Windows os.kill(pid, 0) is not a probe: signal 0 is
    CTRL_C_EVENT there (measured in e6)."""
    if IS_WINDOWS:
        h = _k32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = wintypes.DWORD()
        _k32.GetExitCodeProcess(h, ctypes.byref(code))
        _k32.CloseHandle(h)
        return code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def force_kill_pid_tree(pid: int) -> None:
    """Cleanup helper for experiments that deliberately leave orphans."""
    if IS_WINDOWS:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
    else:
        import signal
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


# ----------------------------------------------------------------------------- durable journal
class Journal:
    """Append-only JSONL. Every transition is flushed + fsynced before the runner acts on it."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.seq = 0

    def append(self, **rec) -> None:
        self.seq += 1
        rec = {"seq": self.seq, "ts": time.time(), **rec}
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
            f.flush()
            os.fsync(f.fileno())

    @staticmethod
    def read(path: Path) -> tuple[list[dict], int]:
        """Return (records, torn_lines). A torn trailing line (crash mid-write) is ignored."""
        records, torn = [], 0
        if not path.exists():
            return records, torn
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                torn += 1
        return records, torn


def recover(path: Path, task_ids: list[str]) -> dict:
    """Classify every task after an OOS crash, from the journal alone."""
    records, torn = Journal.read(path)
    state: dict[str, dict] = {t: {"status": "pending", "attempt": 0} for t in task_ids}
    for r in records:
        t = r.get("task_id")
        if t not in state:
            continue
        if r["event"] == "dispatch_intent":
            state[t].update(status="intent", attempt=r["attempt"], key=r["idempotency_key"])
        elif r["event"] == "spawned":
            state[t].update(status="running", pid=r["pid"])
        elif r["event"] == "terminal":
            state[t].update(status=r["status"], retryable=r.get("retryable"))
    out = {"torn_lines": torn, "tasks": {}}
    for t, s in state.items():
        if s["status"] == "running":
            alive = pid_alive(s["pid"])
            if alive:
                force_kill_pid_tree(s["pid"])
            s = {**s, "status": "interrupted", "orphan_was_alive": alive,
                 "action": "re-dispatch same idempotency key after workspace check"}
        elif s["status"] == "intent":
            s = {**s, "status": "never_started", "action": "dispatch"}
        elif s["status"] == "pending":
            s = {**s, "action": "dispatch"}
        else:
            s = {**s, "action": "none (terminal)"}
        out["tasks"][t] = s
    return out


# ----------------------------------------------------------------------------- worker supervision
async def run_worker(spec: dict, *, timeout_s: float, cancel_after_s: float | None = None,
                     grace_s: float = 0.5, journal: Journal | None = None, cwd: str | None = None,
                     attempt: int = 1, key: str | None = None) -> dict:
    task_id = spec["task_id"]
    key = key or f"{task_id}:{uuid.uuid4().hex[:8]}"
    t0 = time.perf_counter()
    if journal:
        journal.append(event="dispatch_intent", task_id=task_id, attempt=attempt, idempotency_key=key)
    tree = ProcessTree()
    proc = await asyncio.create_subprocess_exec(
        WORKER_PY, str(PROVIDER), stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, cwd=cwd, **tree.spawn_kwargs())
    tree.adopt(proc.pid)  # before the request is sent, so grandchildren are born inside the job
    if journal:
        journal.append(event="spawned", task_id=task_id, pid=proc.pid, attempt=attempt)
    proc.stdin.write((json.dumps(spec) + "\n").encode())
    await proc.stdin.drain()

    events: list[dict] = []
    malformed = 0
    outcome = None

    async def pump() -> None:
        nonlocal malformed
        async for raw in proc.stdout:
            try:
                events.append(json.loads(raw))
            except json.JSONDecodeError:
                malformed += 1

    async def canceller() -> None:
        nonlocal outcome
        await asyncio.sleep(cancel_after_s)
        outcome = "cancel_requested"
        proc.stdin.write(b'{"type": "cancel"}\n')
        await proc.stdin.drain()
        try:
            await asyncio.wait_for(proc.wait(), grace_s)
        except asyncio.TimeoutError:
            outcome = "cancel_forced"
            tree.kill_tree(proc.pid)

    pump_task = asyncio.create_task(pump())
    cancel_task = asyncio.create_task(canceller()) if cancel_after_s is not None else None
    try:
        await asyncio.wait_for(proc.wait(), timeout_s)
    except asyncio.TimeoutError:
        outcome = "timed_out"
        tree.kill_tree(proc.pid)
        await proc.wait()
    if cancel_task:
        cancel_task.cancel()
    # Terminal-state rule found by this spike: reap the whole tree when the worker ends.
    # Descendants inherit the stdout handle, so pipe EOF never arrives while they live.
    descendants_reaped = False
    try:
        await asyncio.wait_for(asyncio.shield(pump_task), 0.5)
    except asyncio.TimeoutError:
        tree.kill_tree(proc.pid)
        descendants_reaped = True
        await asyncio.wait_for(pump_task, 5)

    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    cancelled = any(e.get("type") == "cancelled" for e in events)
    if outcome == "timed_out":
        status, retryable = "timed_out", True
    elif outcome == "cancel_forced":
        status, retryable = "cancelled_forced", False
    elif cancelled:
        status, retryable = "cancelled", False
    elif result:
        status, retryable = result["status"], False
    else:
        status, retryable = "crashed", True
    rec = {"task_id": task_id, "status": status, "retryable": retryable, "exit_code": proc.returncode,
           "events": len(events), "malformed_events": malformed,
           "event_types": sorted({e.get("type") for e in events}),
           "descendants_reaped_after_exit": descendants_reaped,
           "grandchild_alive_after": next((pid_alive(e["pid"]) for e in events if e.get("type") == "grandchild"), None),
           "elapsed_s": round(time.perf_counter() - t0, 3)}
    if journal:
        journal.append(event="terminal", task_id=task_id, status=status, retryable=retryable, attempt=attempt)
    return rec


# ----------------------------------------------------------------------------- experiments
def e1_spawn_latency(n: int = 10) -> dict:
    def measure(cmd: list[str]) -> float:
        ts = []
        for _ in range(n):
            t = time.perf_counter()
            subprocess.run(cmd, check=True, capture_output=True)
            ts.append(time.perf_counter() - t)
        ts.sort()
        return round(ts[len(ts) // 2] * 1000, 1)

    out = {"n": n, "python_cold_start_ms_median": measure([WORKER_PY, "-c", "pass"])}
    node = os.environ.get("OOS_SPIKE_NODE")
    if node and Path(node).exists():
        out["node_cold_start_ms_median"] = measure([node, "-e", "0"])
    return out


def e2_concurrency() -> dict:
    async def go():
        specs = [
            ({"task_id": "A-ok-fast", "behavior": "succeed", "duration_s": 0.3}, {}),
            ({"task_id": "B-ok-slow", "behavior": "succeed", "duration_s": 1.2}, {}),
            ({"task_id": "C-hang", "behavior": "hang"}, {"timeout_s": 1.0}),
            ({"task_id": "D-cancel", "behavior": "succeed", "duration_s": 5}, {"cancel_after_s": 0.4}),
            ({"task_id": "E-crash", "behavior": "crash", "duration_s": 0.5}, {}),
            ({"task_id": "F-ask", "behavior": "ask", "duration_s": 0.3}, {}),
            ({"task_id": "G-ignores-cancel", "behavior": "ignore_cancel", "duration_s": 5}, {"cancel_after_s": 0.4}),
            ({"task_id": "H-leaves-grandchild", "behavior": "leave_grandchild", "duration_s": 0.3}, {}),
        ]
        t = time.perf_counter()
        results = await asyncio.gather(*[run_worker(s, **{"timeout_s": 4.0, **kw}) for s, kw in specs])
        return {"wall_s": round(time.perf_counter() - t, 3), "workers": results}

    return asyncio.run(go())


def e3_tree_kill() -> dict:
    """Does killing the worker also kill what it spawned?"""
    out = {}
    # (a) naive: kill only the direct child
    p = subprocess.Popen([WORKER_PY, str(PROVIDER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    p.stdin.write(json.dumps({"task_id": "naive", "behavior": "spawn_grandchild"}) + "\n")
    p.stdin.flush()
    gc = _wait_for_grandchild(p)
    p.kill()
    p.wait()
    time.sleep(0.3)
    out["naive_kill_grandchild_survived"] = pid_alive(gc)
    if pid_alive(gc):
        force_kill_pid_tree(gc)
    # (b) process-tree ownership (Job Object / process group)
    tree = ProcessTree()
    p = subprocess.Popen([WORKER_PY, str(PROVIDER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         text=True, **tree.spawn_kwargs())
    tree.adopt(p.pid)
    p.stdin.write(json.dumps({"task_id": "tree", "behavior": "spawn_grandchild"}) + "\n")
    p.stdin.flush()
    gc = _wait_for_grandchild(p)
    tree.kill_tree(p.pid)
    p.wait()
    time.sleep(0.3)
    out["tree_kill_grandchild_survived"] = pid_alive(gc)
    out["mechanism"] = "Job Object (TerminateJobObject)" if IS_WINDOWS else "process group (killpg)"
    return out


def _wait_for_grandchild(p: subprocess.Popen) -> int:
    for line in p.stdout:
        ev = json.loads(line)
        if ev.get("type") == "grandchild":
            return ev["pid"]
    raise RuntimeError("no grandchild reported")


def e4_orchestrator_crash() -> dict:
    """The OOS process itself dies (os._exit). Do its workers become orphans?"""
    out = {}
    for mode in ("no-job", "job"):
        with tempfile.TemporaryDirectory() as d:
            pidfile = Path(d) / "pids.json"
            # No pipes to the crash-child: inherited pipe handles would make us wait for the grandchild.
            t = time.perf_counter()
            subprocess.Popen([WORKER_PY, __file__, "crash-child", mode, str(pidfile)],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()
            out[mode + "_parent_exit_s"] = round(time.perf_counter() - t, 2)
            time.sleep(0.5)
            pids = json.loads(pidfile.read_text())
            alive = {k: pid_alive(v) for k, v in pids.items()}
            out[mode] = alive
            for v in pids.values():
                if pid_alive(v):
                    force_kill_pid_tree(v)
    return out


def _crash_child(mode: str, pidfile: str) -> None:
    tree = ProcessTree() if mode == "job" else None
    p = subprocess.Popen([WORKER_PY, str(PROVIDER)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                         **(tree.spawn_kwargs() if tree else {}))
    if tree:
        tree.adopt(p.pid)
    p.stdin.write(json.dumps({"task_id": "orphan-test", "behavior": "spawn_grandchild"}) + "\n")
    p.stdin.flush()
    gc = _wait_for_grandchild(p)
    Path(pidfile).write_text(json.dumps({"worker": p.pid, "grandchild": gc}))
    os._exit(1)  # simulate OOS crash: no cleanup, no finally blocks


TASKS = ["T1", "T2", "T3", "T4"]


def _journal_run(journal_path: str, crash_after: int) -> None:
    """Sub-process: run TASKS concurrently, hard-crash after `crash_after` terminals."""
    j = Journal(Path(journal_path))
    j.append(event="run_started", run_id="spike-run")
    durations = {"T1": 0.2, "T2": 0.3, "T3": 5.0, "T4": 5.0}

    async def go():
        done = 0

        async def one(t):
            nonlocal done
            rec = await run_worker({"task_id": t, "behavior": "succeed", "duration_s": durations[t]},
                                   timeout_s=30, journal=j)
            done += 1
            if done == crash_after:
                with open(journal_path, "a", encoding="utf-8") as f:
                    f.write('{"seq": 999, "event": "terminal", "task_id": "T')  # torn write
                    f.flush()
                os._exit(9)
            return rec

        await asyncio.gather(*[one(t) for t in TASKS])

    asyncio.run(go())


def e5_recovery() -> dict:
    with tempfile.TemporaryDirectory() as d:
        jp = Path(d) / "run.journal.jsonl"
        crashed = subprocess.Popen([WORKER_PY, __file__, "journal-run", str(jp), "2"],
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        crashed.wait()
        time.sleep(0.5)
        report = recover(jp, TASKS)
        # resume: dispatch only non-terminal tasks, re-using the idempotency key for interrupted ones
        j = Journal(jp)
        j.seq = 1000
        to_run = [t for t, s in report["tasks"].items() if s["action"] != "none (terminal)"]

        async def resume():
            return await asyncio.gather(*[
                run_worker({"task_id": t, "behavior": "succeed", "duration_s": 0.2}, timeout_s=10, journal=j,
                           attempt=report["tasks"][t].get("attempt", 0) + 1, key=report["tasks"][t].get("key"))
                for t in to_run])

        resumed = asyncio.run(resume())
        final, torn = Journal.read(jp)
        terminals = {}
        for r in final:
            if r.get("event") == "terminal" and r.get("status") == "succeeded":
                terminals[r["task_id"]] = terminals.get(r["task_id"], 0) + 1
        return {
            "crash_exit_code": crashed.returncode,
            "recovery": report,
            "resumed": [r["task_id"] for r in resumed],
            "succeeded_count_per_task": terminals,
            "every_task_succeeded_exactly_once": sorted(terminals) == TASKS and all(v == 1 for v in terminals.values()),
            "torn_lines_tolerated": torn,
        }


def e6_paths_and_signals() -> dict:
    out = {}
    with tempfile.TemporaryDirectory() as d:
        ws = Path(d) / "workspace with spaces ä ö å"
        ws.mkdir()
        for mode in ("utf8", "native"):
            env_backup = os.environ.get("OOS_FAKE_PROVIDER_NATIVE_ENCODING")
            if mode == "native":
                os.environ["OOS_FAKE_PROVIDER_NATIVE_ENCODING"] = "1"
            name = f"résumé ünïcode {mode}.txt"
            rec = asyncio.run(run_worker({"task_id": "P", "behavior": "write_file", "file_name": name,
                                          "duration_s": 0.1}, timeout_s=10, cwd=str(ws)))
            if env_backup is None:
                os.environ.pop("OOS_FAKE_PROVIDER_NATIVE_ENCODING", None)
            out[f"{mode}_worker_status"] = rec["status"]
            out[f"{mode}_unicode_file_created_correctly"] = (ws / name).is_file()
        out["note"] = "python runner sends ASCII-escaped JSON (json.dumps default), so both modes survive"
    if IS_WINDOWS:
        # Pitfall check: is os.kill(pid, 0) a liveness probe on Windows? (signal 0 == CTRL_C_EVENT)
        import signal
        out["windows_signal0_equals_CTRL_C_EVENT"] = getattr(signal, "CTRL_C_EVENT", None) == 0
        p = subprocess.Popen([WORKER_PY, "-c", "import time; time.sleep(30)"],
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)  # isolate from our console group
        time.sleep(0.2)
        try:
            os.kill(p.pid, 0)
            out["windows_os_kill_sig0_raised"] = False
        except OSError as e:
            out["windows_os_kill_sig0_raised"] = type(e).__name__
        time.sleep(0.2)
        out["windows_os_kill_sig0_process_still_alive"] = pid_alive(p.pid)
        p.kill()
        p.wait()
        try:
            os.kill(p.pid, 0)  # pid now dead
            out["windows_os_kill_sig0_on_dead_pid_raised"] = False
        except OSError as e:
            out["windows_os_kill_sig0_on_dead_pid_raised"] = type(e).__name__
    return out


EXPERIMENTS = {"e1": e1_spawn_latency, "e2": e2_concurrency, "e3": e3_tree_kill,
               "e4": e4_orchestrator_crash, "e5": e5_recovery, "e6": e6_paths_and_signals}


def main(argv: list[str]) -> int:
    if argv[:1] == ["crash-child"]:
        _crash_child(argv[1], argv[2])
        return 0
    if argv[:1] == ["journal-run"]:
        _journal_run(argv[1], int(argv[2]))
        return 0
    which = argv[0] if argv and argv[0] in EXPERIMENTS else "all"
    names = list(EXPERIMENTS) if which == "all" else [which]
    results = {"runtime": f"python {sys.version.split()[0]}", "platform": sys.platform}
    for n in names:
        t = time.perf_counter()
        results[n] = EXPERIMENTS[n]()
        results[n + "_runtime_s"] = round(time.perf_counter() - t, 2)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
