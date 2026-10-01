#!/usr/bin/env python3
"""DISPOSABLE SPIKE CODE (OOS-0002). Not production. Do not import from the kernel.

Runs both candidate runners and records sanitized results (no local paths, no user names):

    python spikes/oos-0002/run_spike.py            # node found via OOS_SPIKE_NODE or PATH
    python spikes/oos-0002/run_spike.py --no-write # print only

Output: spikes/oos-0002/results/<platform>-<date>.json
"""
import datetime
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(cmd: list[str], env: dict) -> dict:
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env, timeout=600)
    if proc.returncode != 0:
        return {"error": f"exit {proc.returncode}", "stderr_tail": proc.stderr[-400:]}
    return json.loads(proc.stdout)


def main() -> int:
    env = {**os.environ, "OOS_SPIKE_PYTHON": sys.executable}
    node = os.environ.get("OOS_SPIKE_NODE") or shutil.which("node")
    if node:
        env["OOS_SPIKE_NODE"] = node
    results = {
        "spike": "OOS-0002",
        "recorded": datetime.date.today().isoformat(),
        "environment": {"os": platform.platform(), "machine": platform.machine(),
                        "python": platform.python_version(), "node": None},
        "caveat": "Tiny synthetic workloads on one machine. Architectural evidence only, not performance data.",
        "python": run([sys.executable, str(HERE / "py_runner.py"), "all"], env),
    }
    if node:
        results["environment"]["node"] = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
        results["node"] = run([node, str(HERE / "node_runner.mjs"), "all"], env)
    else:
        results["node"] = "not run: no node executable found (set OOS_SPIKE_NODE)"
    text = json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    print(text)
    if "--no-write" not in sys.argv:
        out = HERE / "results" / f"{sys.platform}-{results['recorded']}.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {out.relative_to(HERE.parent.parent).as_posix()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
