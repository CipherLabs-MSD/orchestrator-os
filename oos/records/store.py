"""Domain-neutral record store (OOS-0003, ADR-0009).

Stores schema-validated records as one canonical JSON file per record, each wrapped in a generic
envelope (schemas/record-envelope.schema.json). The store knows record *types* only as names
bound to schemas and a mutability rule (orchestration/kernel/record_types.json). It has no idea
what any record means. Domain meaning lives in domain packages (invariant I-1).

Layout under a store root (the caller decides where the root lives, e.g. per the domain workspace binding):

    store.json                         format marker
    .store.lock                        writer lock (released by the OS if the holder dies)
    records/<type>/<id>.json           current version of each record
    history/<type>/<id>/<revision>.json  prior revisions of *mutable* records
"""
from __future__ import annotations

import copy
import datetime as _dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator

from . import _platform, canonical
from .errors import (ConcurrencyConflict, CorruptRecordError, DuplicateRecordError, ImmutableRecordError,
                     InvalidRecordId, RecordNotFound, RecordTooLarge, RecordStoreError, SchemaValidationError,
                     UnknownRecordType, UnsupportedSchemaVersion, ValidationIssue)
from .schema import SchemaRegistry

ENVELOPE_FORMAT = 1
STORE_FORMAT = "oos-record-store/1"
ENVELOPE_SCHEMA = "record-envelope"
DEFAULT_MAX_RECORD_BYTES = 1_048_576

# Portable identifiers: no path separators, no Unicode (NFC/NFD and case folding differ across
# file systems), no Windows device names, no trailing dot. Uniqueness is case-insensitive.
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
_SAFE_TYPE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")

Migration = Callable[[dict], dict]


def check_identifier(value: str, what: str = "record id") -> None:
    if not isinstance(value, str) or not _SAFE_ID.match(value) or value.endswith("."):
        raise InvalidRecordId(f"{what} {value!r} is not a portable identifier")
    if value.split(".")[0].upper() in _WINDOWS_RESERVED:
        raise InvalidRecordId(f"{what} {value!r} is a reserved device name on Windows")


@dataclass(frozen=True)
class RecordType:
    name: str
    schema: str
    mutability: str  # "immutable" (append-only; change by superseding) | "mutable" (revisions)
    max_bytes: int = DEFAULT_MAX_RECORD_BYTES


def load_record_types(path: str | Path) -> dict[str, RecordType]:
    """Load the kernel record-type registry (orchestration/kernel/record_types.json)."""
    doc = canonical.loads(Path(path).read_text(encoding="utf-8"))
    default_max = doc.get("limits", {}).get("max_record_bytes", DEFAULT_MAX_RECORD_BYTES)
    return {name: RecordType(name, spec["schema"], spec["mutability"], spec.get("max_bytes", default_max))
            for name, spec in doc["types"].items()}


@dataclass(frozen=True)
class Record:
    type: str
    id: str
    body: dict
    revision: int
    schema_version: int
    created_at: str
    written_at: str
    provenance: dict
    supersedes: str | None
    digest: str
    migrated_from: int | None = None
    extensions: dict = field(default_factory=dict)


def _utc_now() -> _dt.datetime:
    return _dt.datetime.now(_dt.timezone.utc)


def _timestamp(t: _dt.datetime) -> str:
    return t.astimezone(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class RecordStore:
    def __init__(self, root: str | Path, schemas: SchemaRegistry, types: dict[str, RecordType], *,
                 clock: Callable[[], _dt.datetime] = _utc_now, lock_timeout_s: float = 10.0,
                 migrations: dict[tuple[str, int], Migration] | None = None):
        self.root = Path(root)
        self.schemas = schemas
        self.types = dict(types)
        self.clock = clock
        self.lock_timeout_s = lock_timeout_s
        self.migrations = dict(migrations or {})  # (schema name, from_version) -> fn(body) -> body at from_version+1
        for t in self.types.values():
            if not _SAFE_TYPE.match(t.name):
                raise RecordStoreError(f"record type name {t.name!r} is not a portable identifier")
            if t.mutability not in ("immutable", "mutable"):
                raise RecordStoreError(f"record type {t.name}: invalid mutability {t.mutability!r}")
            schemas.get(t.schema)  # fails fast on unknown schema
        schemas.get(ENVELOPE_SCHEMA)
        self._init_root()

    # ------------------------------------------------------------------ public API
    def create(self, record_type: str, body: dict, *, provenance: dict, supersedes: str | None = None) -> Record:
        """Validate and durably write a new record. Never overwrites."""
        rt = self._type(record_type)
        rid = self._validated_body_id(rt, body)
        if supersedes is not None:
            check_identifier(supersedes, "superseded record id")
        with self._lock():
            if self._find_case_insensitive(rt, rid):
                raise DuplicateRecordError(f"{rt.name}/{rid} already exists (ids are unique case-insensitively)")
            if supersedes is not None:
                self._get_locked(rt, supersedes)  # must exist and be intact
                if self._superseder_of(rt, supersedes):
                    raise DuplicateRecordError(f"{rt.name}/{supersedes} is already superseded")
            now = _timestamp(self.clock())
            env = self._envelope(rt, rid, body, revision=1, created_at=now, written_at=now,
                                 provenance=provenance, supersedes=supersedes, previous_digest=None)
            data = self._encode(rt, env)
            final = self._path(rt, rid)
            tmp = _platform.write_temp(final.parent, data)
            try:
                self._install_new(tmp, final)
            except FileExistsError:
                raise DuplicateRecordError(f"{rt.name}/{rid} already exists") from None
        return self._to_record(env)

    def replace(self, record_type: str, body: dict, *, provenance: dict, expected_revision: int) -> Record:
        """New revision of a *mutable* record (optimistic concurrency). The prior revision is kept in history."""
        rt = self._type(record_type)
        if rt.mutability != "mutable":
            raise ImmutableRecordError(f"{rt.name} is append-only: create a superseding record instead")
        rid = self._validated_body_id(rt, body)
        with self._lock():
            current_path = self._path(rt, rid)
            current = self._get_locked(rt, rid)
            if current.revision != expected_revision:
                raise ConcurrencyConflict(f"{rt.name}/{rid}", expected_revision, current.revision)
            hist = self.root / "history" / rt.name / rid / f"{current.revision:06d}.json"
            htmp = _platform.write_temp(hist.parent, current_path.read_bytes())
            self._install_new(htmp, hist)
            env = self._envelope(rt, rid, body, revision=current.revision + 1, created_at=current.created_at,
                                 written_at=_timestamp(self.clock()), provenance=provenance,
                                 supersedes=current.supersedes, previous_digest=current.digest)
            tmp = _platform.write_temp(current_path.parent, self._encode(rt, env))
            _platform.install_replace(tmp, current_path)
        return self._to_record(env)

    def get(self, record_type: str, record_id: str) -> Record:
        rt = self._type(record_type)
        check_identifier(record_id)
        return self._get_locked(rt, record_id)  # reads are lock-free: files are installed atomically

    def ids(self, record_type: str) -> list[str]:
        rt = self._type(record_type)
        d = self.root / "records" / rt.name
        if not d.is_dir():
            return []
        return sorted(p.stem for p in d.glob("*.json") if not p.name.startswith(_platform.TMP_PREFIX))

    def records(self, record_type: str) -> Iterator[Record]:
        for rid in self.ids(record_type):
            yield self.get(record_type, rid)

    def superseded_by(self, record_type: str, record_id: str) -> str | None:
        """Derived, never stored in the superseded record: the store is append-only for history."""
        return self._superseder_of(self._type(record_type), record_id)

    def history(self, record_type: str, record_id: str) -> list[Record]:
        rt = self._type(record_type)
        check_identifier(record_id)
        d = self.root / "history" / rt.name / record_id
        if not d.is_dir():
            return []
        return [self._read_file(rt, p, expect_id=record_id)
                for p in sorted(d.glob("*.json")) if not p.name.startswith(_platform.TMP_PREFIX)]

    def verify(self) -> list[str]:
        """Integrity scan of every stored record. Returns human-readable problems (empty = intact)."""
        problems = []
        for rt in self.types.values():
            d = self.root / "records" / rt.name
            if not d.is_dir():
                continue
            for p in sorted(d.iterdir()):
                if p.name.startswith(_platform.TMP_PREFIX):
                    problems.append(f"{rt.name}/{p.name}: leftover temp file from an interrupted write")
                    continue
                try:
                    self._read_file(rt, p, expect_id=p.stem)
                except RecordStoreError as e:
                    problems.append(str(e))
        return problems

    def remove_temp_files(self) -> int:
        """Delete leftovers of interrupted writes (never visible as records). Returns count."""
        n = 0
        with self._lock():
            for p in (self.root / "records").rglob(f"{_platform.TMP_PREFIX}*"):
                p.unlink()
                n += 1
            for p in (self.root / "history").rglob(f"{_platform.TMP_PREFIX}*"):
                p.unlink()
                n += 1
        return n

    # ------------------------------------------------------------------ internals
    def _init_root(self) -> None:
        marker = self.root / "store.json"
        if marker.exists():
            try:
                fmt = canonical.loads(marker.read_text(encoding="utf-8")).get("format")
            except canonical.StrictJSONError as e:
                raise CorruptRecordError("store.json", str(e)) from e
            if fmt != STORE_FORMAT:
                raise RecordStoreError(f"store.json: unsupported store format {fmt!r} (expected {STORE_FORMAT})")
            return
        self.root.mkdir(parents=True, exist_ok=True)
        with self._lock():
            if not marker.exists():
                tmp = _platform.write_temp(self.root, canonical.dumps({"format": STORE_FORMAT}).encode("utf-8"))
                try:
                    _platform.install_new(tmp, marker)
                except FileExistsError:
                    pass

    def _lock(self) -> _platform.FileLock:
        return _platform.FileLock(self.root / ".store.lock", self.lock_timeout_s)

    def _install_new(self, tmp: Path, final: Path) -> None:  # seam for fault-injection tests
        _platform.install_new(tmp, final)

    def _type(self, name: str) -> RecordType:
        try:
            return self.types[name]
        except KeyError:
            raise UnknownRecordType(f"unknown record type {name!r}") from None

    def _path(self, rt: RecordType, rid: str) -> Path:
        return self.root / "records" / rt.name / f"{rid}.json"

    def _find_case_insensitive(self, rt: RecordType, rid: str) -> bool:
        return rid.lower() in {i.lower() for i in self.ids(rt.name)}

    def _superseder_of(self, rt: RecordType, rid: str) -> str | None:
        for other in self.ids(rt.name):
            if self._read_file(rt, self._path(rt, other), expect_id=other).supersedes == rid:
                return other
        return None

    def _validated_body_id(self, rt: RecordType, body: dict) -> str:
        if not isinstance(body, dict):
            raise SchemaValidationError(f"{rt.name}", [ValidationIssue("$", "type", "record body must be an object")])
        issues = self.schemas.validate(rt.schema, body)
        if body.get("superseded_by") is not None:
            issues.append(ValidationIssue("$.superseded_by", "x-oos-derived",
                                          "supersession is recorded on the new record (supersedes=...), not in the old body"))
        if issues:
            raise SchemaValidationError(f"{rt.name}/{body.get('id', '?')}", issues)
        rid = body.get("id")
        check_identifier(rid)
        return rid

    def _envelope(self, rt: RecordType, rid: str, body: dict, *, revision: int, created_at: str, written_at: str,
                  provenance: dict, supersedes: str | None, previous_digest: str | None) -> dict:
        env = {
            "oos_record": ENVELOPE_FORMAT, "type": rt.name, "id": rid,
            "schema": self.schemas.schema_id(rt.schema), "schema_version": self.schemas.version(rt.schema),
            "revision": revision, "created_at": created_at, "written_at": written_at,
            "provenance": copy.deepcopy(provenance), "supersedes": supersedes,
            "previous_digest": previous_digest, "extensions": {}, "body": copy.deepcopy(body),
        }
        env["digest"] = canonical.digest(env)
        issues = self.schemas.validate(ENVELOPE_SCHEMA, env)
        if issues:
            raise SchemaValidationError(f"{rt.name}/{rid} envelope", issues)
        return env

    def _encode(self, rt: RecordType, env: dict) -> bytes:
        data = canonical.dumps(env).encode("utf-8")
        if len(data) > rt.max_bytes:
            raise RecordTooLarge(f"{rt.name}/{env['id']}: {len(data)} bytes exceeds limit {rt.max_bytes}")
        return data

    def _get_locked(self, rt: RecordType, rid: str) -> Record:
        path = self._path(rt, rid)
        if not path.is_file():
            raise RecordNotFound(f"{rt.name}/{rid} not found")
        return self._read_file(rt, path, expect_id=rid)

    def _read_file(self, rt: RecordType, path: Path, *, expect_id: str) -> Record:
        loc = f"{rt.name}/{path.name}"
        size = path.stat().st_size
        if size > rt.max_bytes:
            raise RecordTooLarge(f"{loc}: {size} bytes exceeds limit {rt.max_bytes}; refusing to parse")
        try:
            env = canonical.loads(path.read_bytes().decode("utf-8"))
        except UnicodeDecodeError as e:
            raise CorruptRecordError(loc, f"not UTF-8 ({e.reason})") from e
        except canonical.StrictJSONError as e:
            raise CorruptRecordError(loc, str(e)) from e
        issues = self.schemas.validate(ENVELOPE_SCHEMA, env)
        if issues:
            raise CorruptRecordError(loc, "envelope schema: " + "; ".join(map(str, issues[:3])))
        body_digest = env.pop("digest")
        if canonical.digest(env) != body_digest:
            raise CorruptRecordError(loc, "digest mismatch (content changed outside the store)")
        env["digest"] = body_digest
        if env["type"] != rt.name or env["id"] != expect_id or env["body"].get("id") != expect_id:
            raise CorruptRecordError(loc, "type/id do not match the record's location")
        if env["schema"] != self.schemas.schema_id(rt.schema):
            raise CorruptRecordError(loc, f"written with schema {env['schema']!r}, expected {self.schemas.schema_id(rt.schema)!r}")
        current = self.schemas.version(rt.schema)
        found = env["schema_version"]
        migrated_from = None
        if found > current:
            raise UnsupportedSchemaVersion(loc, found, current, "is newer than this OOS supports; upgrade OOS")
        if found < current:
            body = env["body"]
            for v in range(found, current):
                step = self.migrations.get((rt.schema, v))
                if step is None:
                    raise UnsupportedSchemaVersion(loc, found, current, f"is older and no migration {v}->{v + 1} is registered")
                body = step(copy.deepcopy(body))
            env = {**env, "body": body}
            migrated_from = found
        issues = self.schemas.validate(rt.schema, env["body"])
        if issues:
            raise CorruptRecordError(loc, "body fails its schema: " + "; ".join(map(str, issues[:3])))
        return self._to_record(env, migrated_from=migrated_from)

    @staticmethod
    def _to_record(env: dict, migrated_from: int | None = None) -> Record:
        return Record(type=env["type"], id=env["id"], body=copy.deepcopy(env["body"]), revision=env["revision"],
                      schema_version=env["schema_version"], created_at=env["created_at"], written_at=env["written_at"],
                      provenance=copy.deepcopy(env["provenance"]), supersedes=env["supersedes"], digest=env["digest"],
                      migrated_from=migrated_from, extensions=copy.deepcopy(env.get("extensions", {})))
