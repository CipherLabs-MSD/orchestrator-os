#!/usr/bin/env python3
"""Sabotage check for the record substrate (OOS-0003): break one durable guarantee at a time in a
temporary copy of the repo and confirm the store/log tests catch it. Evidence that the tests bite.

    python tools/store_sabotage_check.py

Known, documented gap: removing fsync is NOT caught. Power-loss durability cannot be observed
by unit tests (docs/RECORD_STORE.md §4).
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
EXPECTED_UNCATCHABLE = {"no fsync on records"}
# (file, old, new) replaces; (file, None, text) appends
SABOTAGE = {
    "no digest check": ("oos/records/store.py", "if canonical.digest(env) != body_digest:", "if False:"),
    "create may overwrite": ("oos/records/_platform.py",
                             "            os.rename(tmp, final)  # MoveFileEx without REPLACE_EXISTING: atomic and create-only",
                             "            os.replace(tmp, final)"),
    "lock is a no-op": ("oos/records/_platform.py", None,
                        "\nFileLock.__enter__ = lambda self: self\nFileLock.__exit__ = lambda self, *exc: None\n"),
    "torn log tail not truncated": ("oos/records/log.py", "            if torn:\n                self._truncate_torn_tail()",
                                    "            if False:\n                pass"),
    "no log hash chain check": ("oos/records/log.py", 'if entry["prev"] != (prev["check"] if prev else None):', "if False:"),
    "no fsync on records": ("oos/records/_platform.py", "        f.flush()\n        os.fsync(f.fileno())\n    return tmp",
                            "        f.flush()\n    return tmp"),
}


def main() -> int:
    missed = []
    for name, (rel, old, new) in SABOTAGE.items():
        work = Path(tempfile.mkdtemp(prefix="oos-sab-")) / "repo"
        try:
            shutil.copytree(SRC, work, ignore=shutil.ignore_patterns(".git", "__pycache__", ".venv"))
            p = work / rel
            s = p.read_text(encoding="utf-8")
            if old is None:
                s += new
            else:
                assert old in s, f"sabotage target not found for {name!r}"
                s = s.replace(old, new, 1)
            p.write_text(s, encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_record_store", "tests.test_append_log"],
                               cwd=work, capture_output=True, text=True, timeout=900)
        finally:
            shutil.rmtree(work.parent, ignore_errors=True)
        failing = sorted({line.split(" (")[0].split(": ", 1)[-1]
                          for line in r.stderr.splitlines() if line.startswith(("FAIL:", "ERROR:"))})
        if not r.returncode:
            missed.append(name)
        print(f"{'CAUGHT' if r.returncode else 'MISSED'}  {name:28s} {failing[:3]}")
    unexpected = [m for m in missed if m not in EXPECTED_UNCATCHABLE]
    print(f"\n{len(SABOTAGE) - len(missed)}/{len(SABOTAGE)} sabotages caught; "
          f"expected uncatchable: {sorted(EXPECTED_UNCATCHABLE)}; unexpected misses: {unexpected}")
    return 1 if unexpected else 0


if __name__ == "__main__":
    sys.exit(main())
