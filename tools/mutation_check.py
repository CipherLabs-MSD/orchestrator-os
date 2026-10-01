#!/usr/bin/env python3
"""Mutation check for tools/validate.py: plant known defects in a temporary copy of the
repo and confirm each one makes the validator fail. Evidence that the checks bite.

    python tools/mutation_check.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent

SW_POL = "domains/software-development/policy.json"
SW_VER = "domains/software-development/verification.json"
SW_ROUTE = "domains/software-development/context_routing.json"
FIN = "domains/finance/domain.json"
PROFILE = "orchestration/profiles/software-development.json"
KPOL = "orchestration/kernel/decision_policy.json"


def jedit(root, rel, fn):
    p = root / rel
    d = json.loads(p.read_text(encoding="utf-8"))
    fn(d)
    p.write_text(json.dumps(d, indent=2), encoding="utf-8")


def tedit(root, rel, fn):
    p = root / rel
    p.write_text(fn(p.read_text(encoding="utf-8")), encoding="utf-8")


MUTATIONS = {
    "domain loosens kernel floor": lambda r: jedit(r, SW_POL, lambda d: d["class_floors"].__setitem__("live_external_effect", "D1")),
    "domain loosens mapping cell": lambda r: jedit(r, SW_POL, lambda d: d["dimension_mapping_overrides"].__setitem__("cost", ["D1", "D1", "D1", "D1"])),
    "domain turns prohibition into floor": lambda r: jedit(r, SW_POL, lambda d: d["class_floors"].__setitem__("expose_or_transmit_secrets", "D4")),
    "specialization looser than kernel": lambda r: jedit(r, SW_POL, lambda d: d["class_floors"].__setitem__("production_deploy", "D2")),
    "finance golden example wrong": lambda r: jedit(r, FIN, lambda d: d["policy_sketch"]["golden_examples"][2].__setitem__("expected", "D2")),
    "profile loads illustrative finance": lambda r: jedit(r, PROFILE, lambda d: d["domains"].append("finance")),
    "profile allows unknown backend": lambda r: jedit(r, PROFILE, lambda d: d["backends_allowed"].append("mystery-model")),
    "profile override loosens": lambda r: jedit(r, PROFILE, lambda d: d["policy_overrides"]["class_floors"].__setitem__("production_deploy", "D1")),
    "trading vocabulary in kernel": lambda r: jedit(r, KPOL, lambda d: d["class_descriptions"].__setitem__("general", "routine trading work")),
    "original commit_sha contamination": lambda r: jedit(r, "schemas/evidence.schema.json", lambda d: d["properties"].__setitem__("commit_sha", {"type": "string"})),
    "routing profile above domain ceiling": lambda r: jedit(r, SW_ROUTE, lambda d: d.__setitem__("user_context_ceiling", ["decision_preference"])),
    "domain redefines kernel gate": lambda r: jedit(r, SW_VER, lambda d: d["gates"].append({"id": "G-REVIEW", "name": "x", "passes_when": "x", "evidence_types": ["review"]})),
    "domain gate unknown evidence type": lambda r: jedit(r, SW_VER, lambda d: d["gates"][0].__setitem__("evidence_types", ["vibes"])),
    "backlog capability outside profile": lambda r: jedit(r, "project/backlog.json", lambda d: d["items"][3]["capabilities"].append("risk_analysis")),
    "kernel D4 floor weakened": lambda r: jedit(r, KPOL, lambda d: d["class_floors"].__setitem__("live_external_effect", "D3")),
    "kernel prohibition removed": lambda r: jedit(r, KPOL, lambda d: d["prohibited_classes"].pop("bypass_policy_guard")),
    "project name in core doc": lambda r: tedit(r, "docs/CORE_LOOP.md", lambda s: s + "\nFinanceOS uses this loop.\n"),
    "broken anchor": lambda r: tedit(r, "docs/CORE_LOOP.md", lambda s: s + "\n[x](ARCHITECTURE.md#no-such-section)\n"),
    "invented user context": lambda r: tedit(r, "context/CREATIVE_DNA.md", lambda s: s.replace("_None yet._", "### CTX-0001 — Likes neon\n- statement: Billy likes neon\n")),
    "backend cleared without owner approval": lambda r: jedit(r, "orchestration/backends.json", lambda d: d["backends"].append(dict(d["backends"][3], id="other-llm", vendor="Other"))),
    "AI backend cleared for secret": lambda r: jedit(r, "orchestration/backends.json", lambda d: d["backends"][0]["trust"]["data_policy_ok_for"].append("secret")),
    "public context file marked curated": lambda r: tedit(r, "context/WORKING_STYLE.md", lambda s: s.replace("status: placeholder", "status: curated", 1)),
    "deferred second domain made operational": lambda r: jedit(r, FIN, lambda d: d.__setitem__("operational", True)),
    "backlog cycle": lambda r: jedit(r, "project/backlog.json", lambda d: d["items"][1]["depends_on"].append("OOS-0019")),
}


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="oos-mutation-"))
    work = tmp / "repo"
    results = []
    try:
        for name, mutate in MUTATIONS.items():
            if work.exists():
                shutil.rmtree(work)
            shutil.copytree(SRC, work, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            mutate(work)
            proc = subprocess.run([sys.executable, "tools/validate.py"], cwd=work,
                                  capture_output=True, text=True, encoding="utf-8")
            first = next((l.strip() for l in proc.stdout.splitlines() if l.strip().startswith("- ")), "")
            results.append((name, proc.returncode, first))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    caught = sum(1 for _, rc, _ in results if rc != 0)
    for name, rc, first in results:
        print(f"{'CAUGHT' if rc else 'MISSED'}  {name:40s} {first[:110]}")
    print(f"\n{caught}/{len(results)} mutations caught")
    return 0 if caught == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
