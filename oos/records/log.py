"""Append-only, hash-chained JSON Lines log (OOS-0003). The substrate for run journals
(EXECUTION_RUNTIME §4) and other history that must never be rewritten.

Each line: {"seq", "at", "kind", "data", "prev", "check"} (schemas/log-entry.schema.json)
  - seq increases by exactly 1;  prev = check of the previous line (null for the first)
  - check = sha256 of the line's canonical form without "check"
Writes: one line per append, under an OS-released lock, flushed and fsynced before returning.

A torn final line (a crash mid-append) is the only tolerated defect. It is reported by `read()`,
and truncated by the next `append()` (it was never acknowledged). Any other defect raises CorruptLogError.
"""
from __future__ import annotations

import datetime as _dt
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import _platform, canonical
from .errors import CorruptLogError, RecordTooLarge, SchemaValidationError, ValidationIssue
from .schema import SchemaRegistry

LOG_ENTRY_SCHEMA = "log-entry"
DEFAULT_MAX_LINE_BYTES = 262_144
_KIND = re.compile(r"^[a-z][a-z0-9_.-]{0,63}$")


@dataclass(frozen=True)
class LogRead:
    entries: list[dict]
    torn_tail: bool


def _now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


class AppendLog:
    def __init__(self, path: str | Path, schemas: SchemaRegistry, *, data_schema: str | None = None,
                 max_line_bytes: int = DEFAULT_MAX_LINE_BYTES, clock: Callable[[], _dt.datetime] = _now,
                 lock_timeout_s: float = 10.0):
        self.path = Path(path)
        self.schemas = schemas
        self.data_schema = data_schema
        self.max_line_bytes = max_line_bytes
        self.clock = clock
        self.lock_timeout_s = lock_timeout_s
        schemas.get(LOG_ENTRY_SCHEMA)
        if data_schema:
            schemas.get(data_schema)

    def append(self, kind: str, data: dict) -> dict:
        if not _KIND.match(kind or ""):
            raise SchemaValidationError("log entry", [ValidationIssue("$.kind", "pattern", f"invalid kind {kind!r}")])
        if self.data_schema:
            issues = self.schemas.validate(self.data_schema, data)
            if issues:
                raise SchemaValidationError(f"log entry data ({self.data_schema})", issues)
        with _platform.FileLock(self.path.with_name(self.path.name + ".lock"), self.lock_timeout_s):
            entries, torn = self._scan(tolerate_torn_tail=True)
            if torn:
                self._truncate_torn_tail()
            last = entries[-1] if entries else None
            entry = {"seq": (last["seq"] + 1) if last else 1,
                     "at": self.clock().astimezone(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                     "kind": kind, "data": data, "prev": last["check"] if last else None}
            entry["check"] = canonical.digest(entry)
            issues = self.schemas.validate(LOG_ENTRY_SCHEMA, entry)
            if issues:
                raise SchemaValidationError("log entry", issues)
            line = (canonical.dumps_line(entry) + "\n").encode("utf-8")
            if len(line) > self.max_line_bytes:
                raise RecordTooLarge(f"log entry of {len(line)} bytes exceeds limit {self.max_line_bytes}")
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "ab") as f:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())
        return entry

    def read(self, *, tolerate_torn_tail: bool = True) -> LogRead:
        entries, torn = self._scan(tolerate_torn_tail=tolerate_torn_tail)
        return LogRead(entries, torn)

    # ------------------------------------------------------------------ internals
    def _scan(self, *, tolerate_torn_tail: bool) -> tuple[list[dict], bool]:
        if not self.path.exists():
            return [], False
        raw = self.path.read_bytes()
        lines = raw.split(b"\n")
        complete, tail = lines[:-1], lines[-1]  # tail == b"" when the file ends with a newline
        entries: list[dict] = []
        loc = self.path.name
        for n, b in enumerate(complete, start=1):
            entries.append(self._parse(b, n, loc, entries[-1] if entries else None))
        torn = bool(tail)
        if torn and not tolerate_torn_tail:
            raise CorruptLogError(loc, len(complete) + 1, "torn final line (interrupted append)")
        return entries, torn

    def _parse(self, b: bytes, n: int, loc: str, prev: dict | None) -> dict:
        if len(b) + 1 > self.max_line_bytes:
            raise CorruptLogError(loc, n, "line exceeds size limit")
        try:
            entry = canonical.loads(b.decode("utf-8"))
        except (UnicodeDecodeError, canonical.StrictJSONError) as e:
            raise CorruptLogError(loc, n, f"unparseable: {e}") from e
        issues = self.schemas.validate(LOG_ENTRY_SCHEMA, entry)
        if issues:
            raise CorruptLogError(loc, n, "schema: " + "; ".join(map(str, issues[:3])))
        check = entry.pop("check")
        if canonical.digest(entry) != check:
            raise CorruptLogError(loc, n, "checksum mismatch")
        entry["check"] = check
        expected_seq = prev["seq"] + 1 if prev else 1
        if entry["seq"] != expected_seq:
            raise CorruptLogError(loc, n, f"sequence gap: expected {expected_seq}, found {entry['seq']}")
        if entry["prev"] != (prev["check"] if prev else None):
            raise CorruptLogError(loc, n, "hash chain broken (line removed, reordered or replaced)")
        return entry

    def _truncate_torn_tail(self) -> None:
        raw = self.path.read_bytes()
        keep = raw.rfind(b"\n") + 1
        with open(self.path, "r+b") as f:
            f.truncate(keep)
            f.flush()
            os.fsync(f.fileno())
