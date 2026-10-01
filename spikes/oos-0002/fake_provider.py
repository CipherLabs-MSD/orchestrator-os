#!/usr/bin/env python3
"""DISPOSABLE SPIKE CODE (OOS-0002). Not production. Do not import from the kernel.

A fake agent provider standing in for Claude Code / Codex / an SDK worker. It speaks the
candidate provider-process protocol: JSON Lines over stdio.

  stdin  line 1 : the task request  {"task_id", "behavior", "duration_s", ...}
  stdin  later  : control messages  {"type": "cancel"}
  stdout        : events            {"type": "started" | "progress" | "question" | "result" |
                                     "cancelled" | "grandchild", ...}

Behaviors: succeed, hang, crash, ignore_cancel, ask, spawn_grandchild, leave_grandchild, write_file.
No network, no credentials, no real model.
"""
import json
import os
import subprocess
import sys
import threading
import time

cancel = threading.Event()


def emit(event: dict) -> None:
    sys.stdout.write(json.dumps(event) + "\n")
    sys.stdout.flush()


def watch_stdin() -> None:
    for line in sys.stdin:
        try:
            if json.loads(line).get("type") == "cancel":
                cancel.set()
        except json.JSONDecodeError:
            pass


def main() -> int:
    # Protocol rule found by this spike: stdio is UTF-8, declared explicitly. On Windows a piped
    # stdin otherwise decodes with the locale code page (cp1252 here) and mangles non-ASCII.
    # OOS_FAKE_PROVIDER_NATIVE_ENCODING=1 reproduces the failure.
    if os.environ.get("OOS_FAKE_PROVIDER_NATIVE_ENCODING") != "1":
        sys.stdin.reconfigure(encoding="utf-8")
        sys.stdout.reconfigure(encoding="utf-8")
    request = json.loads(sys.stdin.readline())
    threading.Thread(target=watch_stdin, daemon=True).start()
    behavior = request.get("behavior", "succeed")
    duration = float(request.get("duration_s", 0.3))
    emit({"type": "started", "task_id": request["task_id"], "pid": os.getpid()})

    if behavior in ("spawn_grandchild", "leave_grandchild"):
        # The grandchild inherits this process's stdout handle, like real tool sub-processes do.
        gc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        emit({"type": "grandchild", "pid": gc.pid})
        if behavior == "spawn_grandchild":
            duration = max(duration, 60)

    if behavior == "write_file":
        name = request.get("file_name", "output.txt")
        with open(name, "w", encoding="utf-8") as f:
            f.write("artifact from fake provider\n")
        emit({"type": "progress", "note": "wrote file", "file": name, "cwd_ok": os.path.isfile(name)})

    steps = 10
    for i in range(steps):
        if cancel.is_set() and behavior != "ignore_cancel":
            emit({"type": "cancelled", "task_id": request["task_id"], "at_step": i})
            return 0
        if behavior == "crash" and i == 3:
            sys.stdout.write('{"type": "progress", "partial": tru')  # torn event, then die
            sys.stdout.flush()
            os._exit(3)
        emit({"type": "progress", "step": i + 1, "of": steps})
        if behavior == "hang":
            time.sleep(3600)
        time.sleep(duration / steps)

    if behavior == "ask":
        emit({"type": "question", "task_id": request["task_id"],
              "question": "Two plausible readings of intent; which one?", "options": ["A", "B"]})
        emit({"type": "result", "status": "needs_input", "task_id": request["task_id"]})
        return 0

    emit({"type": "result", "status": "succeeded", "task_id": request["task_id"],
          "changes": [f"change-for-{request['task_id']}"], "artifacts": [],
          "self_report": "done (not evidence)", "usage": {"input_tokens": 0, "output_tokens": 0}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
