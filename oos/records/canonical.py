"""Deterministic serialization and strict, data-only parsing.

- Canonical form: UTF-8, sorted keys, 2-space indent, LF, trailing newline, no NaN/Infinity.
  Identical content always yields identical bytes, which gives stable digests and clean diffs.
- Parsing never executes anything (JSON only, never pickle/eval). It rejects duplicate keys,
  non-standard constants and excessive nesting.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

MAX_DEPTH = 64


class StrictJSONError(ValueError):
    pass


def dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def dumps_line(obj: Any) -> str:
    """Single-line canonical form (for append-only logs)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(dumps_line(obj).encode("utf-8")).hexdigest()


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    out: dict = {}
    for k, v in pairs:
        if k in out:
            raise StrictJSONError(f"duplicate key {k!r}")
        out[k] = v
    return out


def _reject_constant(name: str) -> Any:
    raise StrictJSONError(f"non-standard JSON constant {name}")


def _depth(obj: Any, level: int = 0) -> None:
    if level > MAX_DEPTH:
        raise StrictJSONError(f"nesting deeper than {MAX_DEPTH}")
    if isinstance(obj, dict):
        for v in obj.values():
            _depth(v, level + 1)
    elif isinstance(obj, list):
        for v in obj:
            _depth(v, level + 1)


def loads(text: str) -> Any:
    try:
        obj = json.loads(text, object_pairs_hook=_no_duplicates, parse_constant=_reject_constant)
    except RecursionError as e:
        raise StrictJSONError("nesting too deep") from e
    except json.JSONDecodeError as e:
        raise StrictJSONError(f"invalid JSON: {e.msg} at line {e.lineno} column {e.colno}") from e
    _depth(obj)
    return obj
