"""Schema validation for OOS records.

The JSON Schema files in `schemas/` are the **only** source of truth for record shape. This module
interprets them. It defines no record shapes of its own.

Fail-closed subset (DEC-0006): the validator implements a deliberate subset of JSON Schema
(SUPPORTED_SCHEMA_KEYWORDS). A schema that uses any other keyword is rejected when it is loaded,
so no rule can be silently ignored.

Every schema declares `x-oos-schema-version` (a positive integer). Records carry the version they
were written with (record evolution, docs/RECORD_STORE.md §6).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from . import canonical
from .errors import SchemaError, ValidationIssue

SUPPORTED_SCHEMA_KEYWORDS = frozenset({
    "$schema", "$id", "title", "description", "type", "required", "properties",
    "additionalProperties", "enum", "pattern", "items", "minimum", "maximum", "minLength",
    "x-oos-schema-version",
})
VERSION_KEY = "x-oos-schema-version"

_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _type_ok(value: Any, t: str) -> bool:
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def validate(instance: Any, schema: dict, path: str = "$") -> list[ValidationIssue]:
    """Validate `instance` against `schema` (the supported subset). Returns all issues found."""
    issues: list[ValidationIssue] = []
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(instance, t) for t in types):
            return [ValidationIssue(path, "type", f"expected type {types}, got {type(instance).__name__}")]
    if "enum" in schema and instance not in schema["enum"]:
        issues.append(ValidationIssue(path, "enum", f"{instance!r} not in {schema['enum']}"))
    if isinstance(instance, str):
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            issues.append(ValidationIssue(path, "pattern", f"{instance!r} does not match /{schema['pattern']}/"))
        if "minLength" in schema and len(instance) < schema["minLength"]:
            issues.append(ValidationIssue(path, "minLength", f"shorter than {schema['minLength']}"))
    if _type_ok(instance, "number"):
        if "minimum" in schema and instance < schema["minimum"]:
            issues.append(ValidationIssue(path, "minimum", f"{instance} < minimum {schema['minimum']}"))
        if "maximum" in schema and instance > schema["maximum"]:
            issues.append(ValidationIssue(path, "maximum", f"{instance} > maximum {schema['maximum']}"))
    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                issues.append(ValidationIssue(path, "required", f"missing required '{key}'"))
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    issues.append(ValidationIssue(path, "additionalProperties", f"unexpected property '{key}'"))
        for key, sub in props.items():
            if key in instance:
                issues.extend(validate(instance[key], sub, f"{path}.{key}"))
    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            issues.extend(validate(item, schema["items"], f"{path}[{i}]"))
    return issues


def unsupported_keywords(schema: Any, path: str = "$") -> list[str]:
    """Keywords outside the supported subset, anywhere in a schema."""
    found = []
    if isinstance(schema, dict):
        for k, v in schema.items():
            if k not in SUPPORTED_SCHEMA_KEYWORDS:
                found.append(f"{path}: unsupported keyword '{k}'")
            if k == "properties":
                for pk, pv in v.items():
                    found.extend(unsupported_keywords(pv, f"{path}.properties.{pk}"))
            elif k == "items":
                found.extend(unsupported_keywords(v, f"{path}.items"))
    return found


class SchemaRegistry:
    """Loads `*.schema.json` from a directory and indexes them by name (file stem) and by `$id`."""

    def __init__(self, schema_dir: str | Path):
        self.dir = Path(schema_dir)
        self._by_name: dict[str, dict] = {}
        self._by_id: dict[str, str] = {}
        for p in sorted(self.dir.glob("*.schema.json")):
            name = p.name[: -len(".schema.json")]
            try:
                schema = canonical.loads(p.read_text(encoding="utf-8"))
            except (OSError, canonical.StrictJSONError) as e:
                raise SchemaError(f"{p.name}: unreadable schema ({e})") from e
            bad = unsupported_keywords(schema)
            if bad:
                raise SchemaError(f"{p.name}: " + "; ".join(bad))
            version = schema.get(VERSION_KEY)
            if not (isinstance(version, int) and not isinstance(version, bool) and version >= 1):
                raise SchemaError(f"{p.name}: missing or invalid '{VERSION_KEY}'")
            self._by_name[name] = schema
            if "$id" in schema:
                self._by_id[schema["$id"]] = name

    def names(self) -> list[str]:
        return sorted(self._by_name)

    def get(self, name: str) -> dict:
        try:
            return self._by_name[name]
        except KeyError:
            raise SchemaError(f"unknown schema '{name}'") from None

    def version(self, name: str) -> int:
        return self.get(name)[VERSION_KEY]

    def schema_id(self, name: str) -> str:
        return self.get(name).get("$id", name)

    def validate(self, name: str, instance: Any) -> list[ValidationIssue]:
        return validate(instance, self.get(name))
