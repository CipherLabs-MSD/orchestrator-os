#!/usr/bin/env python3
"""Consistency validator for the Orchestrator OS foundation (OOS-0001, incl. the
domain-specialized orchestration addendum).

Stdlib only (DEC-0001). Run from anywhere:

    python tools/validate.py

Exit code 0 when every check passes. Each check returns a list of error strings,
so tests can call checks individually.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", ".gitignore", ".gitattributes",
    "docs/VISION.md", "docs/ARCHITECTURE.md", "docs/DOMAIN_PACKAGES.md", "docs/CORE_LOOP.md",
    "docs/KNOWLEDGE_TAXONOMY.md", "docs/MEMORY_MODEL.md", "docs/PERSONAL_CONTEXT_MODEL.md",
    "docs/CONTEXT_ROUTER.md", "docs/DECISION_ENGINE.md", "docs/AGENT_MODEL.md", "docs/TASK_GRAPH.md",
    "docs/VERIFICATION.md", "docs/FAILURE_HANDLING.md", "docs/SECURITY_AND_TRUST.md", "docs/EXECUTION_RUNTIME.md",
    "docs/adr/ADR-0008-runtime-and-execution-model.md", "spikes/oos-0002/README.md",
    "docs/adr/README.md", "docs/adr/TEMPLATE.md", "docs/adr/ADR-0006-domain-agnostic-kernel.md",
    "context/README.md", "context/IMPORT_PROTOCOL.md",
    "memory/README.md", "memory/PROJECT_STATE.md", "memory/DECISIONS/README.md", "memory/LEARNINGS.md",
    "memory/FAILED_APPROACHES.md", "memory/OPEN_QUESTIONS.md", "memory/HANDOFF.md",
    "orchestration/README.md", "orchestration/backends.json", "orchestration/owner_policy.json",
    "docs/adr/ADR-0007-initial-owner-policy.md", "memory/DECISIONS/DEC-0004-oos-0001-owner-acceptance.md",
    "orchestration/kernel/decision_policy.json", "orchestration/kernel/verification.json",
    "orchestration/kernel/context_routing.json", "orchestration/profiles/software-development.json",
    "domains/README.md", "domains/software-development/README.md", "domains/software-development/domain.json",
    "domains/software-development/GIT_WORKFLOW.md", "domains/finance/README.md", "domains/finance/domain.json",
    "project/MILESTONES.md", "project/OKRS.md", "project/BACKLOG.md", "project/backlog.json",
]

# Context file -> category it must declare.
CONTEXT_FILES = {
    "context/USER_PROFILE.md": "profile",
    "context/CREATIVE_DNA.md": "creative",
    "context/WORKING_STYLE.md": "working_style",
    "context/DECISION_PREFERENCES.md": "decision_preference",
    "context/LONG_TERM_VISION.md": "long_term_vision",
}

KERNEL_DIR = "orchestration/kernel"
COMPONENTS = ("capabilities", "policy", "verification", "context_routing")

# Kernel purity (invariant I-1, docs/ARCHITECTURE.md §1.4).
# (a) Core files may name real projects only where they are explicitly motivating examples.
CORE_DIRS = ["docs", "schemas", "orchestration"]
PROJECT_NAME_ALLOWLIST = {"docs/VISION.md", "docs/DOMAIN_PACKAGES.md", "docs/adr/ADR-0006-domain-agnostic-kernel.md",
                          "docs/adr/ADR-0007-initial-owner-policy.md"}
PROJECT_NAME_PATTERN = re.compile(r"demon[\s_-]*codex|finance\s*os\b", re.IGNORECASE)
# (b) Kernel machine-readable files must not contain domain vocabulary at all.
KERNEL_JSON_GLOBS = ["orchestration/kernel/*.json", "orchestration/backends.json", "schemas/*.json"]
DOMAIN_VOCABULARY = re.compile(
    r"\b(git|github|gitlab|commits?|branch(?:es)?|worktrees?|pull requests?|unit tests?|ci/cd|"
    r"trad(?:e|es|ing)(?!-offs?)|portfolios?|brokers?|stocks?|unity|godot|unreal)\b", re.IGNORECASE)

SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{40,}"),
    re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{24,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
]

SUPPORTED_SCHEMA_KEYWORDS = {
    "$schema", "$id", "title", "description", "type", "required", "properties",
    "additionalProperties", "enum", "pattern", "items", "minimum", "maximum", "minLength",
}

LEVEL_ORDER = ["D1", "D2", "D3", "D4", "PROHIBITED"]


# --------------------------------------------------------------------------- helpers

def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load_json(rel: str):
    return json.loads(read(rel))


def tracked_text_files() -> list[Path]:
    skip_dirs = {".git", "__pycache__", ".venv", "node_modules"}
    out = []
    for p in ROOT.rglob("*"):
        if p.is_file() and not (set(p.relative_to(ROOT).parts) & skip_dirs):
            if p.suffix.lower() in {".md", ".json", ".py", ".txt", ".toml", ".yml", ".yaml", ""}:
                out.append(p)
    return out


# --------------------------------------------------------------------------- mini JSON Schema

_TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool, "null": type(None),
}


def _type_ok(value, t: str) -> bool:
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def validate_instance(instance, schema: dict, path: str = "$") -> list[str]:
    """Validate against the JSON Schema subset in SUPPORTED_SCHEMA_KEYWORDS."""
    errors: list[str] = []
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(instance, t) for t in types):
            return [f"{path}: expected type {types}, got {type(instance).__name__}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in {schema['enum']}")
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match /{schema['pattern']}/")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']}")
    if _type_ok(instance, "number"):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")
    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required '{key}'")
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: unexpected property '{key}'")
        for key, sub in props.items():
            if key in instance:
                errors.extend(validate_instance(instance[key], sub, f"{path}.{key}"))
    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            errors.extend(validate_instance(item, schema["items"], f"{path}[{i}]"))
    return errors


def _schema_keywords(schema, path="$") -> list[str]:
    errors = []
    if isinstance(schema, dict):
        for k, v in schema.items():
            if k not in SUPPORTED_SCHEMA_KEYWORDS:
                errors.append(f"{path}: unsupported keyword '{k}'")
            if k == "properties":
                for pk, pv in v.items():
                    errors.extend(_schema_keywords(pv, f"{path}.properties.{pk}"))
            elif k == "items":
                errors.extend(_schema_keywords(v, f"{path}.items"))
    return errors


# --------------------------------------------------------------------------- checks

def check_required_files() -> list[str]:
    return [f"missing required file: {f}" for f in REQUIRED_FILES + list(CONTEXT_FILES)
            if not (ROOT / f).is_file()]


def check_json_parses() -> list[str]:
    errors = []
    for p in ROOT.rglob("*.json"):
        if ".git" in p.parts:
            continue
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{p.relative_to(ROOT).as_posix()}: invalid JSON ({e})")
    return errors


def check_schemas() -> list[str]:
    errors = []
    files = sorted((ROOT / "schemas").glob("*.schema.json"))
    if not files:
        errors.append("schemas/: no schema files found")
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        schema = json.loads(p.read_text(encoding="utf-8"))
        for key in ("$schema", "$id", "title", "type"):
            if key not in schema:
                errors.append(f"{rel}: missing '{key}'")
        if not schema.get("$id", "").endswith(p.name):
            errors.append(f"{rel}: $id should end with file name")
        errors.extend(f"{rel}: {e}" for e in _schema_keywords(schema))
    return errors


def _schema(name: str) -> dict:
    return load_json(f"schemas/{name}.schema.json")


def kernel(name: str) -> dict:
    return load_json(f"{KERNEL_DIR}/{name}.json")


def load_domains() -> dict[str, dict]:
    """Load every domains/<id>/ package into one normalized shape. Illustrative packages
    supply sketches instead of component files."""
    out: dict[str, dict] = {}
    for mpath in sorted((ROOT / "domains").glob("*/domain.json")):
        m = json.loads(mpath.read_text(encoding="utf-8"))
        base = mpath.parent.relative_to(ROOT).as_posix()
        comp = m.get("components", {})
        pkg: dict = {"dir": base, "manifest": m}
        if m.get("operational"):
            def part(key: str) -> dict:
                return load_json(f"{base}/{comp[key]}") if key in comp else {}
            pkg["capabilities"] = part("capabilities").get("capabilities", [])
            pkg["policy"] = part("policy")
            pkg["verification"] = part("verification")
            pkg["routing"] = part("context_routing")
            pkg["ceiling"] = pkg["routing"].get("user_context_ceiling", [])
        else:
            pkg["capabilities"] = [{"id": c} for c in m.get("capability_sketch", [])]
            pkg["policy"] = m.get("policy_sketch", {})
            pkg["verification"] = {"evidence_types": m.get("evidence_sketch", {}), "gates": [], "task_type_gates": {}}
            pkg["routing"] = {"profiles": {}}
            pkg["ceiling"] = m.get("user_context_ceiling", [])
        out[m["id"]] = pkg
    return out


def load_profiles() -> dict[str, dict]:
    profiles = {}
    for p in sorted((ROOT / "orchestration/profiles").glob("*.json")):
        prof = json.loads(p.read_text(encoding="utf-8"))
        prof["_file"] = p.relative_to(ROOT).as_posix()
        profiles[prof["id"]] = prof
    return profiles


def check_registries() -> list[str]:
    errors = []

    def conform(rel: str, items: list, schema_name: str) -> None:
        schema = _schema(schema_name)
        seen = set()
        for i, item in enumerate(items):
            errors.extend(f"{rel}[{i}]: {e}" for e in validate_instance(item, schema))
            if item.get("id") in seen:
                errors.append(f"{rel}: duplicate id {item.get('id')}")
            seen.add(item.get("id"))

    conform("orchestration/backends.json", load_json("orchestration/backends.json")["backends"], "execution-backend")
    errors.extend(f"orchestration/owner_policy.json: {e}"
                  for e in validate_instance(load_json("orchestration/owner_policy.json"), _schema("owner-policy")))
    conform(f"{KERNEL_DIR}/verification.json", kernel("verification")["gates"], "verification-gate")
    conform("project/backlog.json", load_json("project/backlog.json")["items"], "backlog-item")
    for pid, prof in load_profiles().items():
        body = {k: v for k, v in prof.items() if k != "_file"}
        errors.extend(f"{prof['_file']}: {e}" for e in validate_instance(body, _schema("orchestrator-profile")))
    for did, pkg in load_domains().items():
        m = pkg["manifest"]
        errors.extend(f"{pkg['dir']}/domain.json: {e}" for e in validate_instance(m, _schema("domain-package")))
        if pkg["dir"].split("/")[-1] != did:
            errors.append(f"{pkg['dir']}/domain.json: id {did!r} must equal its directory name")
        if m.get("operational"):
            missing = [c for c in COMPONENTS if c not in m.get("components", {})]
            if missing:
                errors.append(f"{pkg['dir']}: operational package lacks components {missing}")
                continue
            conform(f"{pkg['dir']}/capabilities.json", pkg["capabilities"], "capability")
            conform(f"{pkg['dir']}/verification.json", pkg["verification"].get("gates", []), "verification-gate")
        elif m.get("status") not in ("illustrative", "deprecated"):
            errors.append(f"{pkg['dir']}: non-operational package must be 'illustrative' or 'deprecated'")
    return errors


def check_cross_references() -> list[str]:
    """Kernel-internal references, backends, and the OOS backlog against its profile."""
    errors = []
    kver = kernel("verification")
    base_types = set(kver["evidence_base_types"])
    kgates = {g["id"] for g in kver["gates"]}
    for g in kver["gates"]:
        for e in g["evidence_types"]:
            if e not in base_types:
                errors.append(f"kernel gate {g['id']}: evidence type {e} is not a kernel base type")
    for t, gs in kver["task_type_gates"].items():
        for g in gs:
            if g not in kgates:
                errors.append(f"kernel task type {t}: unknown kernel gate {g}")
    if not any(g.get("implicit") for g in kver["gates"]):
        errors.append("kernel verification: no implicit gate (G-SCOPE expected)")

    ctx_categories = set(_schema("knowledge-entry")["properties"]["category"]["enum"])
    routing = kernel("context_routing")
    control = set(routing.get("control_plane_user_context", {}).get("categories", []))
    for cat in sorted(control - ctx_categories):
        errors.append(f"kernel control_plane_user_context: unknown category {cat}")
    domains = load_domains()
    consumed = set(control)
    for pkg in domains.values():
        if pkg["manifest"].get("operational"):
            for prof in pkg["routing"].get("profiles", {}).values():
                consumed |= set(prof.get("user_context_categories", []))
    for cat in sorted(ctx_categories - consumed):
        errors.append(f"user_context category {cat} has no consumer (no domain profile or control plane)")

    for b in load_json("orchestration/backends.json")["backends"]:
        for s in b.get("strengths", []):
            dom, _, cap = s.partition("/")
            if dom not in domains or cap not in {c["id"] for c in domains[dom]["capabilities"]}:
                errors.append(f"backend {b['id']}: unknown strength {s}")

    backlog = load_json("project/backlog.json")
    profiles = load_profiles()
    prof = profiles.get(backlog.get("profile", ""))
    if not prof:
        return errors + [f"project/backlog.json: unknown profile {backlog.get('profile')!r}"]
    pdomains = [domains[d] for d in prof["domains"] if d in domains]
    caps = {c["id"] for d in pdomains for c in d["capabilities"]}
    gates = kgates | {g["id"] for d in pdomains for g in d["verification"].get("gates", [])}
    open_qs = set(re.findall(r"^\| (OQ-\d{3}) \|", read("memory/OPEN_QUESTIONS.md"), re.MULTILINE))
    for item in backlog["items"]:
        for c in item.get("capabilities", []):
            if c not in caps:
                errors.append(f"{item['id']}: capability {c} not provided by profile {prof['id']}")
        for g in item["gates"]:
            if g not in gates:
                errors.append(f"{item['id']}: gate {g} not provided by profile {prof['id']}")
        for q in item.get("blocked_by_questions", []):
            if q not in open_qs:
                errors.append(f"{item['id']}: unknown open question {q}")
    return errors


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    """Return one dependency cycle as a list of node ids, or None if the graph is a DAG."""
    WHITE, GREY, BLACK = 0, 1, 2
    color = {n: WHITE for n in graph}
    stack: list[str] = []

    def visit(n: str):
        color[n] = GREY
        stack.append(n)
        for m in graph.get(n, []):
            if color.get(m) == GREY:
                return stack[stack.index(m):] + [m]
            if color.get(m) == WHITE:
                found = visit(m)
                if found:
                    return found
        stack.pop()
        color[n] = BLACK
        return None

    for n in graph:
        if color[n] == WHITE:
            found = visit(n)
            if found:
                return found
    return None


def waves(graph: dict[str, list[str]]) -> dict[str, int]:
    """Topological wave index: 0 for roots, else 1 + max(wave of dependencies)."""
    memo: dict[str, int] = {}

    def w(n: str) -> int:
        if n not in memo:
            memo[n] = 1 + max((w(d) for d in graph[n]), default=-1)
        return memo[n]

    return {n: w(n) for n in graph}


def check_backlog() -> list[str]:
    errors = []
    items = load_json("project/backlog.json")["items"]
    graph = {i["id"]: i["depends_on"] for i in items}
    milestones = set(re.findall(r"^\| \*\*(M\d+)\*\* \|", read("project/MILESTONES.md"), re.MULTILINE))
    for i in items:
        for d in i["depends_on"]:
            if d not in graph:
                errors.append(f"{i['id']}: depends on unknown {d}")
        if i["milestone"] not in milestones:
            errors.append(f"{i['id']}: milestone {i['milestone']} not in MILESTONES.md")
    if errors:
        return errors
    cycle = find_cycle(graph)
    if cycle:
        return [f"backlog dependency cycle: {' -> '.join(cycle)}"]

    # Markdown index must agree with backlog.json.
    md = read("project/BACKLOG.md")
    rows = re.findall(r"^\| (OOS-\d{4}) \| (.+?) \| (M\d+) \| (\w+) \| (.+?) \| (.+?) \| (D\d) \|$", md, re.MULTILINE)
    md_by_id = {r[0]: r for r in rows}
    if set(md_by_id) != set(graph):
        errors.append(f"BACKLOG.md index ids differ from backlog.json: "
                      f"only_md={sorted(set(md_by_id) - set(graph))} only_json={sorted(set(graph) - set(md_by_id))}")
    def ids(cell: str) -> set[str]:
        return set(re.findall(r"OOS-\d{4}|OQ-\d{3}", cell))
    for i in items:
        r = md_by_id.get(i["id"])
        if not r:
            continue
        _, title, ms, status, deps, blocked, level = r
        if title != i["title"]:
            errors.append(f"{i['id']}: title differs between BACKLOG.md and backlog.json")
        if ms != i["milestone"] or status != i["status"] or level != i.get("expected_level"):
            errors.append(f"{i['id']}: milestone/status/level differ between BACKLOG.md and backlog.json")
        if ids(deps) != set(i["depends_on"]):
            errors.append(f"{i['id']}: depends_on differs between BACKLOG.md and backlog.json")
        if ids(blocked) != set(i.get("blocked_by_questions", [])):
            errors.append(f"{i['id']}: blocked_by_questions differ between BACKLOG.md and backlog.json")

    # Wave table must match the computed topological waves.
    computed = waves(graph)
    wave_rows = re.findall(r"^\| (\d+) \| ((?:OOS-\d{4}(?: · )?)+) \|", md, re.MULTILINE)
    documented = {oid: int(w) for w, cell in wave_rows for oid in re.findall(r"OOS-\d{4}", cell)}
    if documented != computed:
        errors.append(f"BACKLOG.md wave table differs from computed waves: {computed}")
    return errors


def _hi(a: str, b: str) -> str:
    return max(a, b, key=LEVEL_ORDER.index)


def compose_policy(kernel_policy: dict, *domain_policies: dict) -> dict:
    """kernel ⊕ domains, tighten-only by construction: every level is the max of its contributors.
    (check_domain_packages separately reports any *attempt* to loosen, which is a defect.)"""
    p = {
        "dimensions": kernel_policy["dimensions"],
        "dimension_mapping": {d: list(r) for d, r in kernel_policy["dimension_mapping"].items()},
        "class_floors": dict(kernel_policy["class_floors"]),
        "combination_rules": list(kernel_policy["combination_rules"]),
        "prohibited_classes": dict(kernel_policy["prohibited_classes"]),
    }
    for dp in domain_policies:
        for d, row in dp.get("dimension_mapping_overrides", {}).items():
            p["dimension_mapping"][d] = [_hi(a, b) for a, b in zip(p["dimension_mapping"][d], row)]
        for c, lvl in dp.get("class_floors", {}).items():
            p["class_floors"][c] = _hi(p["class_floors"].get(c, "D1"), lvl)
        p["combination_rules"] += dp.get("combination_rules", [])
        p["prohibited_classes"].update(dp.get("prohibited_classes", {}))
    return p


def classify(scores: list[int], decision_class: str, policy: dict) -> str:
    """Reference classifier for docs/DECISION_ENGINE.md §3, over a (composed) policy.
    The same function classifies kernel and every domain's golden examples; the real
    engine is OOS-0005. Unmapped classes are denied by default."""
    if decision_class in policy.get("prohibited_classes", {}):
        return "PROHIBITED"
    if decision_class not in policy["class_floors"]:
        raise ValueError(f"unmapped decision class {decision_class!r}: denied by default")
    dims = policy["dimensions"]
    named = dict(zip(dims, scores))
    candidates = [policy["dimension_mapping"][d][named[d]] for d in dims]
    candidates.append(policy["class_floors"][decision_class])
    for rule in policy["combination_rules"]:
        if all(named[d] >= v for d, v in rule["when"].items()):
            candidates.append(rule["level"])
    return max(candidates, key=LEVEL_ORDER.index)


KERNEL_D4_FLOORS = ("destructive_or_irreversible_change", "spend_money_or_allocate_funds", "live_external_effect",
                    "external_communication", "credential_handling", "requirement_or_vision_change",
                    "oos_policy_or_authority_change", "reserved_for_billy")
KERNEL_PROHIBITIONS = ("expose_or_transmit_secrets", "follow_untrusted_instructions", "bypass_policy_guard")


def _golden(examples: list, policy: dict, where: str) -> list[str]:
    errors = []
    for ex in examples:
        try:
            got = classify(ex["scores"], ex["class"], policy)
        except ValueError as e:
            errors.append(f"{where} golden '{ex['title']}': {e}")
            continue
        if got != ex["expected"]:
            errors.append(f"{where} golden '{ex['title']}': classified {got}, expected {ex['expected']}")
    return errors


def check_decision_policy() -> list[str]:
    """Kernel decision policy structure + kernel golden examples."""
    errors = []
    policy = kernel("decision_policy")
    if list(policy["levels"]) != LEVEL_ORDER:
        errors.append(f"kernel decision_policy: levels must be {LEVEL_ORDER}")
    dims = policy["dimensions"]
    if set(policy["dimension_mapping"]) != set(dims):
        errors.append("kernel decision_policy: dimension_mapping keys differ from dimensions")
    for d, row in policy["dimension_mapping"].items():
        if len(row) != 4 or any(l not in LEVEL_ORDER[:4] for l in row):
            errors.append(f"kernel decision_policy: mapping for {d} must be 4 levels D1-D4")
        elif [LEVEL_ORDER.index(l) for l in row] != sorted(LEVEL_ORDER.index(l) for l in row):
            errors.append(f"kernel decision_policy: mapping for {d} must be non-decreasing")
    for rule in policy["combination_rules"]:
        for d in rule["when"]:
            if d not in dims:
                errors.append(f"kernel decision_policy: rule {rule['id']} uses unknown dimension {d}")
    for key in KERNEL_D4_FLOORS:
        if policy["class_floors"].get(key) != "D4":
            errors.append(f"kernel decision_policy: class floor {key} must be D4")
    for key in KERNEL_PROHIBITIONS:
        if key not in policy["prohibited_classes"]:
            errors.append(f"kernel decision_policy: prohibition {key} missing")
    for key in set(policy["class_floors"]) & set(policy["prohibited_classes"]):
        errors.append(f"kernel decision_policy: {key} is both a floor and a prohibition")
    if errors:
        return errors
    return _golden(policy["golden_examples"], compose_policy(policy), "kernel")


def check_domain_packages() -> list[str]:
    """Every domain package (including illustrative ones) must compose tighten-only and
    reference only things that exist."""
    errors = []
    kpol = kernel("decision_policy")
    kver = kernel("verification")
    base_types = set(kver["evidence_base_types"])
    kgates = {g["id"] for g in kver["gates"]}
    ktasks = set(kver["task_type_gates"])
    ctx_categories = set(_schema("knowledge-entry")["properties"]["category"]["enum"])
    for did, pkg in load_domains().items():
        where = f"domain {did}"
        dp = pkg["policy"]
        # --- tighten-only policy
        for d, row in dp.get("dimension_mapping_overrides", {}).items():
            if d not in kpol["dimension_mapping"]:
                errors.append(f"{where}: override for unknown dimension {d}")
                continue
            for i, (k, v) in enumerate(zip(kpol["dimension_mapping"][d], row)):
                if v not in LEVEL_ORDER[:4] or LEVEL_ORDER.index(v) < LEVEL_ORDER.index(k):
                    errors.append(f"{where}: mapping {d}[{i}]={v} loosens kernel {k}")
        for c, lvl in dp.get("class_floors", {}).items():
            if lvl not in LEVEL_ORDER[:4]:
                errors.append(f"{where}: floor {c}={lvl} invalid (use prohibited_classes for PROHIBITED)")
            elif c in kpol["prohibited_classes"]:
                errors.append(f"{where}: {c} is a kernel prohibition and cannot become a floor")
            elif c in kpol["class_floors"] and LEVEL_ORDER.index(lvl) < LEVEL_ORDER.index(kpol["class_floors"][c]):
                errors.append(f"{where}: floor {c}={lvl} loosens kernel {kpol['class_floors'][c]}")
        for c, target in dp.get("class_specializes", {}).items():
            if target in kpol["prohibited_classes"]:
                if c not in dp.get("prohibited_classes", {}):
                    errors.append(f"{where}: {c} specializes prohibition {target} and must be prohibited")
            elif target not in kpol["class_floors"]:
                errors.append(f"{where}: {c} specializes unknown kernel class {target}")
            elif c in dp.get("class_floors", {}) and \
                    LEVEL_ORDER.index(dp["class_floors"][c]) < LEVEL_ORDER.index(kpol["class_floors"][target]):
                errors.append(f"{where}: {c} is looser than the kernel class it specializes ({target})")
        for rule in dp.get("combination_rules", []):
            if any(d not in kpol["dimensions"] for d in rule.get("when", {})) or rule.get("level") not in LEVEL_ORDER[:4]:
                errors.append(f"{where}: invalid combination rule {rule.get('id')}")
        errors.extend(_golden(dp.get("golden_examples", []), compose_policy(kpol, dp), where))
        # --- verification
        ver = pkg["verification"]
        dtypes = ver.get("evidence_types", {})
        for t, base in dtypes.items():
            if base not in base_types:
                errors.append(f"{where}: evidence type {t} extends unknown base {base}")
        dgates = {g["id"] for g in ver.get("gates", [])}
        for g in sorted(dgates & kgates):
            errors.append(f"{where}: gate {g} redefines a kernel gate")
        for g in ver.get("gates", []):
            for e in g.get("evidence_types", []):
                if e not in base_types and e not in dtypes:
                    errors.append(f"{where}: gate {g['id']} uses unknown evidence type {e}")
        for t, gs in ver.get("task_type_gates", {}).items():
            if t in ktasks:
                errors.append(f"{where}: task type {t} redefines a kernel task type")
            for g in gs:
                if g not in kgates | dgates:
                    errors.append(f"{where}: task type {t} uses unknown gate {g}")
        # --- context routing
        ceiling = set(pkg["ceiling"])
        for cat in sorted(ceiling - ctx_categories):
            errors.append(f"{where}: ceiling has unknown category {cat}")
        profiles = pkg["routing"].get("profiles", {})
        for name, prof in profiles.items():
            allowed = set(prof.get("user_context_categories", []))
            for cat in sorted(allowed - ceiling):
                errors.append(f"{where}: profile {name} allows {cat} above the domain ceiling")
            for cat in prof.get("user_context_conditions", {}):
                if cat not in allowed:
                    errors.append(f"{where}: profile {name} has a condition for non-allowed category {cat}")
        # --- capabilities (operational packages only carry full records)
        if pkg["manifest"].get("operational"):
            caps = {c["id"] for c in pkg["capabilities"]}
            for c in pkg["capabilities"]:
                if c["context_profile"] not in profiles:
                    errors.append(f"{where}: capability {c['id']} has unknown context_profile {c['context_profile']}")
                for g in c["default_verification_gates"]:
                    if g not in kgates | dgates:
                        errors.append(f"{where}: capability {c['id']} uses unknown gate {g}")
                for r in c.get("related", []):
                    if r not in caps:
                        errors.append(f"{where}: capability {c['id']} has unknown related {r}")
    return errors


def check_owner_policy() -> list[str]:
    """Owner policy (ADR-0007) is the ceiling for installation-level authority: the backend
    registry may never grant more than it, and kernel policy must stay consistent with it."""
    errors = []
    owner = load_json("orchestration/owner_policy.json")
    backends = {b["id"]: b for b in load_json("orchestration/backends.json")["backends"]}
    dp = owner["ai_provider_data_policy"]
    for bid in dp["approved_backends"]:
        if bid not in backends:
            errors.append(f"owner policy: approved backend {bid} is not in the registry")
    for bid, b in backends.items():
        trust = b["trust"]
        if b["kind"] == "human":
            continue
        if "secret" in trust["data_policy_ok_for"]:
            errors.append(f"backend {bid}: AI backends may never be cleared for 'secret'")
        elevated = "private" in trust["data_policy_ok_for"] or trust.get("user_context_ok")
        if elevated and bid not in dp["approved_backends"]:
            errors.append(f"backend {bid}: cleared for private data/user context without owner approval")
        if elevated and trust.get("approved_by") != owner["record"]:
            errors.append(f"backend {bid}: elevated clearance must cite owner record {owner['record']}")
        if trust.get("user_context_ok") and "approved_user_context" not in dp["may_receive"]:
            errors.append(f"backend {bid}: user_context_ok but owner policy grants no user context")
    kpol = kernel("decision_policy")
    if owner["spending"]["autonomous_limit"]["amount"] == 0:
        if kpol["class_floors"].get("spend_money_or_allocate_funds") != "D4" or kpol["dimension_mapping"]["cost"][3] != "D4":
            errors.append("owner policy: 0 spending limit requires spend floor D4 and cost[3] = D4 in the kernel")
    if owner["integration_authority"]["merge_to_protected_canonical"] == "billy_only" and \
            kpol["integration_authority"].get("default") != "billy":
        errors.append("owner policy: Billy-only merge requires kernel integration_authority.default = billy")
    if not any(c["status"] == "active" for c in owner["escalation"]["channels"]):
        errors.append("owner policy: at least one active escalation channel is required")
    second = owner.get("second_operational_domain", {})
    if second.get("status") == "deferred":
        if second.get("selected") is not None:
            errors.append("owner policy: second domain is deferred but a selection is recorded")
        for did, pkg in load_domains().items():
            if did in second.get("candidates", []) and pkg["manifest"].get("operational"):
                errors.append(f"domain {did}: operational while the owner has deferred the second-domain decision")
    return errors


def check_profiles() -> list[str]:
    """A profile = kernel + operational domains + declared backends + tighten-only overrides."""
    errors = []
    domains = load_domains()
    backends = {b["id"] for b in load_json("orchestration/backends.json")["backends"]}
    kpol = kernel("decision_policy")
    kgates = {g["id"] for g in kernel("verification")["gates"]}
    profiles = load_profiles()
    if not profiles:
        errors.append("orchestration/profiles: no orchestrator profile defined")
    for pid, prof in profiles.items():
        where = prof["_file"]
        loaded = []
        for d in prof["domains"]:
            if d not in domains:
                errors.append(f"{where}: unknown domain {d}")
            elif not domains[d]["manifest"].get("operational"):
                errors.append(f"{where}: domain {d} is not operational and cannot be loaded")
            else:
                loaded.append(domains[d])
        for b in prof["backends_allowed"]:
            if b not in backends:
                errors.append(f"{where}: unknown backend {b}")
        seen_caps: dict[str, str] = {}
        seen_gates: dict[str, str] = {}
        for pkg in loaded:
            did = pkg["manifest"]["id"]
            for c in pkg["capabilities"]:
                if c["id"] in seen_caps:
                    errors.append(f"{where}: capability {c['id']} collides ({seen_caps[c['id']]}, {did}); qualify ids")
                seen_caps[c["id"]] = did
            for g in pkg["verification"].get("gates", []):
                if g["id"] in seen_gates or g["id"] in kgates:
                    errors.append(f"{where}: gate {g['id']} collides across loaded packages")
                seen_gates[g["id"]] = did
        composed = compose_policy(kpol, *[pkg["policy"] for pkg in loaded])
        for c, lvl in prof["policy_overrides"].get("class_floors", {}).items():
            if c not in composed["class_floors"]:
                errors.append(f"{where}: override for unknown class {c}")
            elif LEVEL_ORDER.index(lvl) < LEVEL_ORDER.index(composed["class_floors"][c]):
                errors.append(f"{where}: override {c}={lvl} loosens composed {composed['class_floors'][c]}")
    return errors


_HEADER = re.compile(r"\A<!-- context-file\n(.*?)\n-->", re.DOTALL)
_ENTRY = re.compile(r"^### (CTX-\d{4}) — .*?$\n((?:^- .*$\n?)+)", re.MULTILINE)


def parse_context_entries(text: str) -> list[dict]:
    """Parse '### CTX-NNNN — title' entries with '- key: value' lines into dicts."""
    entries = []
    for m in _ENTRY.finditer(re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)):
        entry: dict = {"id": m.group(1)}
        for line in m.group(2).splitlines():
            k, _, v = line[2:].partition(":")
            v = v.split("  #")[0].strip()
            if v.startswith("[") and v.endswith("]"):
                entry[k.strip()] = [x.strip() for x in v[1:-1].split(",") if x.strip()]
            elif v == "null":
                entry[k.strip()] = None
            elif re.fullmatch(r"\d+(\.\d+)?", v):
                entry[k.strip()] = float(v)
            else:
                entry[k.strip()] = v
        entries.append(entry)
    return entries


def check_context_text(rel: str, text: str, category: str) -> list[str]:
    errors = []
    m = _HEADER.match(text)
    if not m:
        return [f"{rel}: missing '<!-- context-file ... -->' header"]
    header = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    header = {k.strip(): v.strip() for k, v in header.items()}
    if header.get("category") != category:
        errors.append(f"{rel}: header category {header.get('category')!r}, expected {category!r}")
    entries = parse_context_entries(text)
    if header.get("status") == "placeholder":
        if entries:
            errors.append(f"{rel}: marked placeholder but contains entries {[e['id'] for e in entries]}")
        if "PLACEHOLDER" not in text:
            errors.append(f"{rel}: placeholder file lacks visible PLACEHOLDER banner")
    elif header.get("status") != "curated":
        errors.append(f"{rel}: header status must be 'placeholder' or 'curated'")
    if header.get("entries") != str(len(entries)):
        errors.append(f"{rel}: header entries={header.get('entries')} but found {len(entries)}")
    schema = _schema("knowledge-entry")
    for e in entries:
        errors.extend(f"{rel} {e['id']}: {err}" for err in validate_instance(e, schema))
        if e.get("category") != category:
            errors.append(f"{rel} {e['id']}: category {e.get('category')} belongs in another file")
    return errors


def check_context_files() -> list[str]:
    errors = []
    all_ids: dict[str, str] = {}
    private_store = load_json("orchestration/owner_policy.json")["user_context_store"]["location"] != "public_repository"
    for rel, category in CONTEXT_FILES.items():
        text = read(rel)
        errors.extend(check_context_text(rel, text, category))
        if private_store and "status: placeholder" not in text.split("-->", 1)[0]:
            errors.append(f"{rel}: owner policy keeps user context in a private store; public files must stay placeholders")
        for e in parse_context_entries(text):
            if e["id"] in all_ids:
                errors.append(f"{rel}: duplicate {e['id']} (also in {all_ids[e['id']]})")
            all_ids[e["id"]] = rel
    return errors


def kernel_vocabulary_hits(obj, path: str = "$") -> list[str]:
    """Find domain vocabulary in a kernel JSON document (keys and string values;
    $id/$schema URLs excluded). Underscores count as word breaks, so snake_case
    identifiers such as commit_sha are caught."""
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("$id", "$schema"):
                continue
            if DOMAIN_VOCABULARY.search(k.replace("_", " ")):
                hits.append(f"{path}.{k} (key)")
            hits.extend(kernel_vocabulary_hits(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(kernel_vocabulary_hits(v, f"{path}[{i}]"))
    elif isinstance(obj, str):
        m = DOMAIN_VOCABULARY.search(obj.replace("_", " "))
        if m:
            hits.append(f"{path}: '{m.group(0)}'")
    return hits


def check_kernel_purity() -> list[str]:
    """Invariant I-1: no project names in core files (outside designated example docs), and
    no domain vocabulary in kernel machine-readable files."""
    errors = []
    for d in CORE_DIRS:
        for p in (ROOT / d).rglob("*"):
            rel = p.relative_to(ROOT).as_posix()
            if p.is_file() and rel not in PROJECT_NAME_ALLOWLIST and PROJECT_NAME_PATTERN.search(p.read_text(encoding="utf-8")):
                errors.append(f"{rel}: core file names a real project (allowed only in designated example docs)")
    for pattern in KERNEL_JSON_GLOBS:
        for p in sorted(ROOT.glob(pattern)):
            rel = p.relative_to(ROOT).as_posix()
            for hit in kernel_vocabulary_hits(json.loads(p.read_text(encoding="utf-8"))):
                errors.append(f"{rel}: domain vocabulary in kernel file at {hit}")
    return errors


SPIKE_LABEL = "DISPOSABLE SPIKE CODE"
# Kernel and domain packages must never depend on spikes (meta-tools in tools/ may name them to check them).
NO_SPIKE_REFERENCE_DIRS = ["orchestration", "schemas", "domains"]


def check_spike_isolation() -> list[str]:
    """Experimental code stays experimental: every spike source carries the DISPOSABLE label,
    and nothing in the kernel or domain packages references spikes/."""
    errors = []
    spikes = ROOT / "spikes"
    if spikes.is_dir():
        for p in spikes.rglob("*"):
            if p.is_file() and p.suffix in (".py", ".mjs", ".js", ".ts") and SPIKE_LABEL not in p.read_text(encoding="utf-8"):
                errors.append(f"{p.relative_to(ROOT).as_posix()}: spike source lacks the '{SPIKE_LABEL}' label")
            if p.is_dir() and p.parent == spikes and not (p / "README.md").is_file():
                errors.append(f"{p.relative_to(ROOT).as_posix()}: spike directory lacks a README")
    for d in NO_SPIKE_REFERENCE_DIRS:
        for p in (ROOT / d).rglob("*"):
            if p.is_file() and p.suffix in (".py", ".json", ".md", ".mjs") and \
                    re.search(r"spikes[/\\.]|import py_runner|from spikes", p.read_text(encoding="utf-8")):
                errors.append(f"{p.relative_to(ROOT).as_posix()}: references spike code (spikes are not dependencies)")
    return errors


def scan_secrets(text: str) -> list[str]:
    return [pat.pattern for pat in SECRET_PATTERNS if pat.search(text)]


def check_no_secrets() -> list[str]:
    errors = []
    for p in tracked_text_files():
        try:
            hits = scan_secrets(p.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
        if hits:
            errors.append(f"{p.relative_to(ROOT).as_posix()}: possible secret matching {hits}")
    return errors


_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def github_slug(heading: str) -> str:
    """GitHub-style heading anchor: lowercase, drop punctuation/symbols, spaces -> '-'."""
    text = re.sub(r"[`*_]", lambda m: "_" if m.group(0) == "_" else "", heading.strip().lower())
    text = "".join(ch for ch in text if ch.isalnum() or ch in " -_")
    return text.replace(" ", "-")


def anchors_of(path: Path) -> set[str]:
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    for h in _HEADING.findall(text):
        slug = github_slug(h)
        n = counts.get(slug, 0)
        slugs.add(slug if n == 0 else f"{slug}-{n}")
        counts[slug] = n + 1
    return slugs


def check_links() -> list[str]:
    """Relative Markdown links must point at existing files, and #anchors at existing headings."""
    errors = []
    for p in ROOT.rglob("*.md"):
        if ".git" in p.parts:
            continue
        text = re.sub(r"```.*?```", "", p.read_text(encoding="utf-8"), flags=re.DOTALL)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`\n]*`", "", text)
        for target in _LINK.findall(text):
            if re.match(r"^[a-z]+:", target):
                continue
            path, _, anchor = target.partition("#")
            dest = (p.parent / path) if path else p
            rel = p.relative_to(ROOT).as_posix()
            if not dest.exists():
                errors.append(f"{rel}: broken link -> {target}")
            elif anchor and dest.is_file() and dest.suffix == ".md" and anchor not in anchors_of(dest):
                errors.append(f"{rel}: broken anchor -> {target}")
    return errors


CHECKS = [
    ("required files", check_required_files),
    ("JSON parses", check_json_parses),
    ("schemas well-formed", check_schemas),
    ("registries conform to schemas", check_registries),
    ("cross-references resolve", check_cross_references),
    ("backlog DAG + views agree", check_backlog),
    ("kernel decision policy + golden examples", check_decision_policy),
    ("domain packages compose tighten-only", check_domain_packages),
    ("orchestrator profiles", check_profiles),
    ("owner policy enforced", check_owner_policy),
    ("context files: placeholders / curated entries", check_context_files),
    ("kernel purity (no domain contamination)", check_kernel_purity),
    ("spike code isolated and labelled", check_spike_isolation),
    ("no secrets", check_no_secrets),
    ("internal links resolve", check_links),
]


def main() -> int:
    failed = 0
    for name, fn in CHECKS:
        try:
            errors = fn()
        except Exception as e:  # a crashing check is a failing check
            errors = [f"check crashed: {type(e).__name__}: {e}"]
        status = "PASS" if not errors else "FAIL"
        print(f"[{status}] {name}")
        for err in errors:
            print(f"       - {err}")
        failed += bool(errors)
    print(f"\n{len(CHECKS) - failed}/{len(CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
