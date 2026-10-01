#!/usr/bin/env python3
"""Pre-publication check: run before pushing anything to a public remote.

    python tools/prepublish_check.py [branch]

Checks the commits that would be published (those not yet on any remote):
  1. working tree is clean
  2. no secret-shaped strings in any added line of those commits
  3. no personal identifiers in added lines (e-mail addresses other than no-reply, local user paths)
  4. no user-context entries in any committed version of context/*.md
  5. commit author/committer e-mails are no-reply addresses
  6. tools/validate.py passes on the working tree

It cannot recognise *meaning*. Content copied from private sources (for example another
repository's description) still needs a human/agent review of the full diff (LRN-0005).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import validate as v  # noqa: E402

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
LOCAL_PATH = re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+|/c/Users/[^/\s]+|/home/[a-z][a-z0-9_-]*/|/Users/[A-Za-z][^/\s]*/")
ALLOWED_EMAIL = re.compile(r"(noreply|no-reply)[A-Za-z0-9.+-]*@|@users\.noreply\.github\.com$|@anthropic\.com$")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout


def main() -> int:
    branch = sys.argv[1] if len(sys.argv) > 1 else git("rev-parse", "--abbrev-ref", "HEAD").strip()
    findings: list[str] = []

    if git("status", "--porcelain").strip():
        findings.append("working tree is not clean")

    commits = git("rev-list", branch, "--not", "--remotes").split()
    print(f"commits to publish from {branch}: {len(commits)}")

    for c in commits:
        for line in git("show", "--format=", "--unified=0", c).splitlines():
            if not line.startswith("+") or line.startswith("+++"):
                continue
            added = line[1:]
            if "re.compile(" in added or "SECRET_PATTERNS" in added:
                continue  # the scanners' own pattern definitions
            for pat in v.scan_secrets(added):
                findings.append(f"{c[:7]}: secret-shaped string ({pat}): {added.strip()[:80]}")
            for e in EMAIL.findall(added):
                if not ALLOWED_EMAIL.search(e) and not e.endswith("example.com"):
                    findings.append(f"{c[:7]}: e-mail address in content: {e}")
            if LOCAL_PATH.search(added):
                findings.append(f"{c[:7]}: local user path in content: {added.strip()[:80]}")
        for path in git("ls-tree", "-r", "--name-only", c, "context/").split():
            if path.endswith(".md"):
                entries = v.parse_context_entries(git("show", f"{c}:{path}"))
                if entries:
                    findings.append(f"{c[:7]}: {path} contains user-context entries {[e['id'] for e in entries]}")

    for ident in set(git("log", "--format=%ae%n%ce", branch, "--not", "--remotes").split()):
        if not ALLOWED_EMAIL.search(ident):
            findings.append(f"commit identity is not a no-reply address: {ident}")

    failed_checks = [name for name, fn in v.CHECKS if fn()]
    if failed_checks:
        findings.append(f"tools/validate.py checks failing: {failed_checks}")

    for f in findings:
        print(f"FINDING  {f}")
    print(f"\n{'PASS' if not findings else 'FAIL'}: {len(findings)} finding(s). Manual review of the full diff is still required.")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
