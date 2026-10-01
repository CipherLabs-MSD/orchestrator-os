#!/usr/bin/env python3
"""Consistency validator for the Orchestrator OS foundation (OOS-0001).

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
    "README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md", ".gitignore",
    "docs/VISION.md", "docs/ARCHITECTURE.md", "docs/CORE_LOOP.md", "docs/KNOWLEDGE_TAXONOMY.md",
    "docs/MEMORY_MODEL.md", "docs/PERSONAL_CONTEXT_MODEL.md", "docs/CONTEXT_ROUTER.md",
    "docs/DECISION_ENGINE.md", "docs/AGENT_MODEL.md", "docs/TASK_GRAPH.md", "docs/VERIFICATION.md",
    "docs/FAILURE_HANDLING.md", "docs/GIT_WORKFLOW.md", "docs/SECURITY_AND_TRUST.md",
    "docs/adr/README.md", "docs/adr/TEMPLATE.md",
    "context/README.md", "context/IMPORT_PROTOCOL.md",
    "memory/README.md", "memory/PROJECT_STATE.md", "memory/DECISIONS/README.md", "memory/LEARNINGS.md",
    "memory/FAILED_APPROACHES.md", "memory/OPEN_QUESTIONS.md", "memory/HANDOFF.md",
    "orchestration/README.md", "orchestration/decision_policy.json", "orchestration/capabilities.json",
    "orchestration/backends.json", "orchestration/verification_gates.json", "orchestration/context_routing.json",
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

# Directories that make up the project-agnostic core, and the only core files allowed
# to name a pilot project (as a consumer, not as architecture).
CORE_DIRS = ["docs", "schemas", "orchestration"]
PILOT_NAME_ALLOWLIST = {"docs/VISION.md"}
PILOT_NAME_PATTERN = re.compile(r"demon[\s_-]*codex", re.IGNORECASE)

SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{40,}"),
    re.compile(r"sk-(?:ant-|proj-)?[A-Za-z0-9_-]{24,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
]

SUPPORTED_SCHEMA_KEYWORDS = {
    "$schema", "$id", "title", "description", "type", "required", "properties",
    "additionalProperties", "enum", "pattern", "items", "minimum", "maximum", "minLength",
}

LEVEL_ORDER = ["D1", "D2", "D3", "D4"]


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


def check_registries() -> list[str]:
    errors = []
    pairs = [
        ("orchestration/capabilities.json", "capabilities", "capability"),
        ("orchestration/backends.json", "backends", "execution-backend"),
        ("orchestration/verification_gates.json", "gates", "verification-gate"),
        ("project/backlog.json", "items", "backlog-item"),
    ]
    for rel, key, schema_name in pairs:
        data = load_json(rel)
        schema = _schema(schema_name)
        seen = set()
        for i, item in enumerate(data.get(key, [])):
            errors.extend(f"{rel}[{i}]: {e}" for e in validate_instance(item, schema))
            if item.get("id") in seen:
                errors.append(f"{rel}: duplicate id {item.get('id')}")
            seen.add(item.get("id"))
    return errors


def check_cross_references() -> list[str]:
    errors = []
    caps = {c["id"] for c in load_json("orchestration/capabilities.json")["capabilities"]}
    gates_doc = load_json("orchestration/verification_gates.json")
    gates = {g["id"] for g in gates_doc["gates"]}
    routing = load_json("orchestration/context_routing.json")
    profiles = routing["profiles"]
    ctx_categories = set(_schema("knowledge-entry")["properties"]["category"]["enum"])

    for c in load_json("orchestration/capabilities.json")["capabilities"]:
        if c["context_profile"] not in profiles:
            errors.append(f"capability {c['id']}: unknown context_profile {c['context_profile']}")
        for g in c["default_verification_gates"]:
            if g not in gates:
                errors.append(f"capability {c['id']}: unknown gate {g}")
        for r in c.get("related", []):
            if r not in caps:
                errors.append(f"capability {c['id']}: unknown related capability {r}")
    for t, gs in gates_doc["task_type_gates"].items():
        for g in gs:
            if g not in gates:
                errors.append(f"task_type_gates.{t}: unknown gate {g}")
    if not any(g.get("implicit") for g in gates_doc["gates"]):
        errors.append("verification_gates: no implicit gate (G-SCOPE expected)")
    for name, prof in profiles.items():
        for cat in prof.get("user_context_categories", []):
            if cat not in ctx_categories:
                errors.append(f"routing profile {name}: unknown user_context category {cat}")
        for cat in prof.get("user_context_conditions", {}):
            if cat not in prof.get("user_context_categories", []):
                errors.append(f"routing profile {name}: condition for non-allowed category {cat}")
    for cat in routing.get("control_plane_user_context", {}).get("categories", []):
        if cat not in ctx_categories:
            errors.append(f"control_plane_user_context: unknown category {cat}")
    routable = {c for prof in profiles.values() for c in prof.get("user_context_categories", [])}
    routable |= set(routing.get("control_plane_user_context", {}).get("categories", []))
    for cat in sorted(ctx_categories - routable):
        errors.append(f"user_context category {cat} has no consumer in context_routing.json")
    for b in load_json("orchestration/backends.json")["backends"]:
        for s in b.get("strengths", []):
            if s not in caps:
                errors.append(f"backend {b['id']}: unknown strength capability {s}")

    open_qs = set(re.findall(r"^\| (OQ-\d{3}) \|", read("memory/OPEN_QUESTIONS.md"), re.MULTILINE))
    for item in load_json("project/backlog.json")["items"]:
        for c in item.get("capabilities", []):
            if c not in caps:
                errors.append(f"{item['id']}: unknown capability {c}")
        for g in item["gates"]:
            if g not in gates:
                errors.append(f"{item['id']}: unknown gate {g}")
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


def classify(scores: list[int], decision_class: str, policy: dict) -> str:
    """Reference classifier for docs/DECISION_ENGINE.md §3. Used to check the policy's
    golden examples; the real engine is OOS-0005."""
    dims = policy["dimensions"]
    named = dict(zip(dims, scores))
    candidates = [policy["dimension_mapping"][d][named[d]] for d in dims]
    candidates.append(policy["class_floors"][decision_class])
    for rule in policy["combination_rules"]:
        if all(named[d] >= v for d, v in rule["when"].items()):
            candidates.append(rule["level"])
    return max(candidates, key=LEVEL_ORDER.index)


def check_decision_policy() -> list[str]:
    errors = []
    policy = load_json("orchestration/decision_policy.json")
    dims = policy["dimensions"]
    if set(policy["dimension_mapping"]) != set(dims):
        errors.append("decision_policy: dimension_mapping keys differ from dimensions")
    for d, row in policy["dimension_mapping"].items():
        if len(row) != 4 or any(l not in LEVEL_ORDER for l in row):
            errors.append(f"decision_policy: mapping for {d} must be 4 levels D1-D4")
        if [LEVEL_ORDER.index(l) for l in row] != sorted(LEVEL_ORDER.index(l) for l in row):
            errors.append(f"decision_policy: mapping for {d} must be non-decreasing")
    for rule in policy["combination_rules"]:
        for d in rule["when"]:
            if d not in dims:
                errors.append(f"decision_policy: rule {rule['id']} uses unknown dimension {d}")
    for key in ("oos_policy_or_authority_change", "reserved_for_billy", "destructive_data_or_history",
                "spend_money_or_license", "production_deploy_or_infrastructure", "external_communication",
                "requirement_or_vision_change"):
        if policy["class_floors"].get(key) != "D4":
            errors.append(f"decision_policy: class floor {key} must be D4")
    if errors:
        return errors
    for ex in policy["golden_examples"]:
        if ex["class"] not in policy["class_floors"]:
            errors.append(f"golden example '{ex['title']}': unknown class {ex['class']}")
            continue
        got = classify(ex["scores"], ex["class"], policy)
        if got != ex["expected"]:
            errors.append(f"golden example '{ex['title']}': classified {got}, expected {ex['expected']}")
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
    for rel, category in CONTEXT_FILES.items():
        text = read(rel)
        errors.extend(check_context_text(rel, text, category))
        for e in parse_context_entries(text):
            if e["id"] in all_ids:
                errors.append(f"{rel}: duplicate {e['id']} (also in {all_ids[e['id']]})")
            all_ids[e["id"]] = rel
    return errors


def check_project_agnostic_core() -> list[str]:
    errors = []
    for d in CORE_DIRS:
        for p in (ROOT / d).rglob("*"):
            rel = p.relative_to(ROOT).as_posix()
            if p.is_file() and rel not in PILOT_NAME_ALLOWLIST and PILOT_NAME_PATTERN.search(p.read_text(encoding="utf-8")):
                errors.append(f"{rel}: core file names a pilot project (keep the core project-agnostic)")
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


def check_links() -> list[str]:
    """Relative Markdown links must point at existing files or directories (anchors not checked)."""
    errors = []
    for p in ROOT.rglob("*.md"):
        if ".git" in p.parts:
            continue
        text = re.sub(r"```.*?```", "", p.read_text(encoding="utf-8"), flags=re.DOTALL)
        text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
        for target in _LINK.findall(text):
            if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if path and not (p.parent / path).exists():
                errors.append(f"{p.relative_to(ROOT).as_posix()}: broken link -> {target}")
    return errors


CHECKS = [
    ("required files", check_required_files),
    ("JSON parses", check_json_parses),
    ("schemas well-formed", check_schemas),
    ("registries conform to schemas", check_registries),
    ("cross-references resolve", check_cross_references),
    ("backlog DAG + views agree", check_backlog),
    ("decision policy + golden examples", check_decision_policy),
    ("context files: placeholders / curated entries", check_context_files),
    ("core is project-agnostic", check_project_agnostic_core),
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
