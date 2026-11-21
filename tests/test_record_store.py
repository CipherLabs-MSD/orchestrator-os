"""OOS-0003 record store: durable behaviour tests (temporary directories only)."""
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from oos.records import (ConcurrencyConflict, CorruptRecordError, DuplicateRecordError,  # noqa: E402
                         ImmutableRecordError, InvalidRecordId, RecordNotFound, RecordStore, RecordTooLarge,
                         RecordType, SchemaError, SchemaRegistry, SchemaValidationError, UnknownRecordType,
                         UnsupportedSchemaVersion, load_record_types)

SCHEMAS = SchemaRegistry(ROOT / "schemas")
TYPES = load_record_types(ROOT / "orchestration" / "kernel" / "record_types.json")
PROV = {"actor": "test-suite", "authority": "D1", "evidence": []}


def fixed_clock():
    return dt.datetime(2026, 10, 2, 12, 0, 0, tzinfo=dt.timezone.utc)


def decision(n=101, **over):
    body = {"id": f"DEC-{n:04d}", "title": "Choose a thing", "level": "D2",
            "scores": {"impact": 1, "reversibility": 1, "uncertainty": 0, "cost": 0, "security": 0, "vision_alignment": 0},
            "decision_class": "general", "status": "decided", "decided_by": "orchestrator", "date": "2026-10-02"}
    body.update(over)
    return body


def task(n=1, state="ready"):
    return {"id": f"TASK-{n:04d}", "node_type": "task", "title": "Do the thing", "state": state}


def widget_schema_dir(base: Path, version: int = 1, extra_required: bool = False) -> Path:
    """A schema directory with the kernel envelope/log schemas plus a type the kernel has never heard of."""
    d = base / f"schemas-v{version}"
    d.mkdir(parents=True, exist_ok=True)
    for name in ("record-envelope", "log-entry"):
        shutil.copy(ROOT / "schemas" / f"{name}.schema.json", d)
    props = {"id": {"type": "string"}, "label": {"type": "string"}}
    widget = {"$id": "test:widget.schema.json", "x-oos-schema-version": version, "type": "object",
              "additionalProperties": False, "required": ["id", "label"] if extra_required else ["id"],
              "properties": props}
    (d / "widget.schema.json").write_text(json.dumps(widget), encoding="utf-8")
    return d


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="oos-store-"))
        self.store = RecordStore(self.tmp / "store", SCHEMAS, TYPES, clock=fixed_clock)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def record_path(self, rtype, rid):
        return self.tmp / "store" / "records" / rtype / f"{rid}.json"


class CreateAndRead(Base):
    def test_round_trip(self):
        r = self.store.create("decision-record", decision(), provenance=PROV)
        got = self.store.get("decision-record", "DEC-0101")
        self.assertEqual(got.body, decision())
        self.assertEqual((got.revision, got.schema_version, got.supersedes), (1, 1, None))
        self.assertEqual(got.provenance["actor"], "test-suite")
        self.assertEqual(got.digest, r.digest)
        self.assertRegex(got.digest, r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(got.created_at, "2026-10-02T12:00:00.000000Z")

    def test_deterministic_bytes(self):
        self.store.create("decision-record", decision(), provenance=PROV)
        other = RecordStore(self.tmp / "other", SCHEMAS, TYPES, clock=fixed_clock)
        other.create("decision-record", dict(reversed(list(decision().items()))), provenance=PROV)
        a = self.record_path("decision-record", "DEC-0101").read_bytes()
        b = (self.tmp / "other" / "records" / "decision-record" / "DEC-0101.json").read_bytes()
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(b"\n") and b"\r" not in a)

    def test_unicode_round_trip(self):
        body = {"id": "CTX-0001", "statement": "Föredrar små steg · 小步快跑 · ✓", "kind": "user_preference",
                "category": "working_style", "scope": "global", "strength": "weak", "confidence": 0.5,
                "source": "fictional test fixture", "learned": "2026-10-02", "status": "active",
                "applies_to_capabilities": []}
        self.store.create("knowledge-entry", body, provenance=PROV)
        self.assertEqual(self.store.get("knowledge-entry", "CTX-0001").body["statement"], body["statement"])
        self.assertIn("小步快跑".encode("utf-8"), self.record_path("knowledge-entry", "CTX-0001").read_bytes())

    def test_ids_and_records_listing(self):
        for n in (3, 1, 2):
            self.store.create("decision-record", decision(n), provenance=PROV)
        self.assertEqual(self.store.ids("decision-record"), ["DEC-0001", "DEC-0002", "DEC-0003"])
        self.assertEqual([r.id for r in self.store.records("decision-record")], ["DEC-0001", "DEC-0002", "DEC-0003"])


class Validation(Base):
    def test_invalid_body_rejected_with_structured_issues_and_nothing_written(self):
        with self.assertRaises(SchemaValidationError) as cm:
            self.store.create("decision-record", decision(level="D9", extra=1), provenance=PROV)
        keywords = {(i.path, i.keyword) for i in cm.exception.issues}
        self.assertIn(("$.level", "enum"), keywords)
        self.assertIn(("$", "additionalProperties"), keywords)
        self.assertFalse((self.tmp / "store" / "records").exists() and any((self.tmp / "store" / "records").rglob("*")))

    def test_unknown_type(self):
        with self.assertRaises(UnknownRecordType):
            self.store.create("no-such-type", {"id": "X-0001"}, provenance=PROV)

    def test_provenance_requires_actor(self):
        with self.assertRaises(SchemaValidationError):
            self.store.create("decision-record", decision(), provenance={"authority": "D1"})

    def test_superseded_by_in_body_is_rejected(self):
        with self.assertRaises(SchemaValidationError) as cm:
            self.store.create("decision-record", decision(superseded_by="DEC-0200"), provenance=PROV)
        self.assertIn("x-oos-derived", {i.keyword for i in cm.exception.issues})

    def test_schema_with_unsupported_keyword_fails_closed(self):
        d = widget_schema_dir(self.tmp)
        (d / "bad.schema.json").write_text(json.dumps({"$id": "bad", "x-oos-schema-version": 1, "oneOf": []}), encoding="utf-8")
        with self.assertRaises(SchemaError):
            SchemaRegistry(d)

    def test_schema_without_version_is_rejected(self):
        d = widget_schema_dir(self.tmp)
        (d / "nover.schema.json").write_text(json.dumps({"$id": "nover", "type": "object"}), encoding="utf-8")
        with self.assertRaises(SchemaError):
            SchemaRegistry(d)


class Identity(Base):
    def setUp(self):
        super().setUp()
        reg = SchemaRegistry(widget_schema_dir(self.tmp))
        self.w = RecordStore(self.tmp / "w", reg, {"widget": RecordType("widget", "widget", "immutable")}, clock=fixed_clock)

    def test_duplicate_id(self):
        self.store.create("decision-record", decision(), provenance=PROV)
        with self.assertRaises(DuplicateRecordError):
            self.store.create("decision-record", decision(), provenance=PROV)

    def test_case_insensitive_uniqueness(self):
        self.w.create("widget", {"id": "Alpha"}, provenance=PROV)
        with self.assertRaises(DuplicateRecordError):
            self.w.create("widget", {"id": "ALPHA"}, provenance=PROV)

    def test_non_portable_ids_rejected(self):
        for bad in ("CON", "nul.txt", "a/b", "..", "x.", "é-1", "a\\b", "", "-lead", "x" * 129):
            with self.subTest(bad=bad), self.assertRaises(InvalidRecordId):
                self.w.create("widget", {"id": bad}, provenance=PROV)

    def test_store_accepts_types_it_has_never_heard_of(self):
        # Domain neutrality: the store has no type-specific logic, only schema + mutability.
        r = self.w.create("widget", {"id": "W-1", "label": "anything"}, provenance=PROV)
        self.assertEqual(self.w.get("widget", "W-1").body, {"id": "W-1", "label": "anything"})
        self.assertEqual(r.type, "widget")


class CreateOnlyInstallation(Base):
    """Defence in depth: even if the duplicate pre-check were bypassed, creation never overwrites."""

    def test_platform_install_new_refuses_existing_target(self):
        from oos.records import _platform
        d = self.tmp / "inst"
        d.mkdir()
        (d / "final.json").write_bytes(b"original")
        tmp = _platform.write_temp(d, b"intruder")
        with self.assertRaises(FileExistsError):
            _platform.install_new(tmp, d / "final.json")
        self.assertEqual((d / "final.json").read_bytes(), b"original")
        self.assertFalse(tmp.exists())

    def test_create_never_overwrites_even_without_precheck(self):
        class Blind(RecordStore):
            def _find_case_insensitive(self, rt, rid):
                return False
        self.store.create("decision-record", decision(), provenance=PROV)
        before = self.record_path("decision-record", "DEC-0101").read_bytes()
        blind = Blind(self.tmp / "store", SCHEMAS, TYPES, clock=fixed_clock)
        with self.assertRaises(DuplicateRecordError):
            blind.create("decision-record", decision(title="other"), provenance=PROV)
        self.assertEqual(self.record_path("decision-record", "DEC-0101").read_bytes(), before)


class SupersessionAndRevisions(Base):
    def test_supersession_never_modifies_the_old_record(self):
        self.store.create("decision-record", decision(1), provenance=PROV)
        before = self.record_path("decision-record", "DEC-0001").read_bytes()
        new = self.store.create("decision-record", decision(2), provenance=PROV, supersedes="DEC-0001")
        self.assertEqual(new.supersedes, "DEC-0001")
        self.assertEqual(self.store.superseded_by("decision-record", "DEC-0001"), "DEC-0002")
        self.assertIsNone(self.store.superseded_by("decision-record", "DEC-0002"))
        self.assertEqual(self.record_path("decision-record", "DEC-0001").read_bytes(), before)

    def test_supersede_twice_or_missing_rejected(self):
        self.store.create("decision-record", decision(1), provenance=PROV)
        self.store.create("decision-record", decision(2), provenance=PROV, supersedes="DEC-0001")
        with self.assertRaises(DuplicateRecordError):
            self.store.create("decision-record", decision(3), provenance=PROV, supersedes="DEC-0001")
        with self.assertRaises(RecordNotFound):
            self.store.create("decision-record", decision(4), provenance=PROV, supersedes="DEC-0999")

    def test_immutable_types_cannot_be_replaced(self):
        self.store.create("decision-record", decision(), provenance=PROV)
        with self.assertRaises(ImmutableRecordError):
            self.store.replace("decision-record", decision(), provenance=PROV, expected_revision=1)

    def test_mutable_replace_keeps_history_and_chain(self):
        r1 = self.store.create("task-node", task(state="ready"), provenance=PROV)
        old_bytes = self.record_path("task-node", "TASK-0001").read_bytes()
        r2 = self.store.replace("task-node", task(state="in_progress"), provenance={"actor": "dispatcher"}, expected_revision=1)
        self.assertEqual((r2.revision, r2.created_at), (2, r1.created_at))
        self.assertEqual(self.store.get("task-node", "TASK-0001").body["state"], "in_progress")
        hist = self.store.history("task-node", "TASK-0001")
        self.assertEqual([h.revision for h in hist], [1])
        self.assertEqual(hist[0].digest, r1.digest)
        self.assertEqual((self.tmp / "store" / "history" / "task-node" / "TASK-0001" / "000001.json").read_bytes(), old_bytes)
        raw = json.loads(self.record_path("task-node", "TASK-0001").read_text(encoding="utf-8"))
        self.assertEqual(raw["previous_digest"], r1.digest)

    def test_stale_revision_conflict(self):
        self.store.create("task-node", task(), provenance=PROV)
        self.store.replace("task-node", task(state="in_progress"), provenance=PROV, expected_revision=1)
        with self.assertRaises(ConcurrencyConflict):
            self.store.replace("task-node", task(state="done"), provenance=PROV, expected_revision=1)


class CorruptionAndLimits(Base):
    def setUp(self):
        super().setUp()
        self.store.create("decision-record", decision(), provenance=PROV)
        self.path = self.record_path("decision-record", "DEC-0101")

    def test_truncated_file(self):
        data = self.path.read_bytes()
        self.path.write_bytes(data[: len(data) // 2])
        with self.assertRaises(CorruptRecordError):
            self.store.get("decision-record", "DEC-0101")
        self.assertEqual(len(self.store.verify()), 1)

    def test_out_of_band_edit_detected_by_digest(self):
        self.path.write_text(self.path.read_text(encoding="utf-8").replace('"D2"', '"D1"'), encoding="utf-8")
        with self.assertRaises(CorruptRecordError) as cm:
            self.store.get("decision-record", "DEC-0101")
        self.assertIn("digest", cm.exception.reason)

    def test_malformed_payloads_fail_safely(self):
        cases = {
            "duplicate keys": b'{"id": "DEC-0101", "id": "DEC-0102"}',
            "NaN": b'{"x": NaN}',
            "deep nesting": b"[" * 200 + b"]" * 200,
            "not utf-8": b'{"x": "\xff\xfe"}',
            "code-looking string is just data": None,
        }
        for name, payload in cases.items():
            if payload is None:
                continue
            with self.subTest(name):
                self.path.write_bytes(payload)
                with self.assertRaises(CorruptRecordError):
                    self.store.get("decision-record", "DEC-0101")

    def test_strings_are_never_executed(self):
        evil = "__import__('os').system('exit 1') ; eval('1+1')"
        self.store.create("decision-record", decision(102, title=evil), provenance=PROV)
        self.assertEqual(self.store.get("decision-record", "DEC-0102").body["title"], evil)

    def test_file_moved_to_another_id_detected(self):
        self.path.rename(self.path.with_name("DEC-0199.json"))
        with self.assertRaises(CorruptRecordError):
            self.store.get("decision-record", "DEC-0199")

    def test_size_limits(self):
        small = RecordStore(self.tmp / "small", SCHEMAS, {"decision-record": RecordType("decision-record", "decision-record", "immutable", 600)}, clock=fixed_clock)
        with self.assertRaises(RecordTooLarge):
            small.create("decision-record", decision(title="x" * 2000), provenance=PROV)
        self.path.write_bytes(b" " * (TYPES["decision-record"].max_bytes + 1))
        with self.assertRaises(RecordTooLarge):
            self.store.get("decision-record", "DEC-0101")


class Evolution(Base):
    def _stores(self, migrations=None):
        v1 = SchemaRegistry(widget_schema_dir(self.tmp, 1))
        v2 = SchemaRegistry(widget_schema_dir(self.tmp, 2, extra_required=True))
        types = {"widget": RecordType("widget", "widget", "immutable")}
        root = self.tmp / "evo"
        return (RecordStore(root, v1, types, clock=fixed_clock),
                RecordStore(root, v2, types, clock=fixed_clock, migrations=migrations))

    def test_newer_version_is_refused(self):
        s1, s2 = self._stores()
        s2.create("widget", {"id": "W-1", "label": "v2"}, provenance=PROV)
        with self.assertRaises(UnsupportedSchemaVersion) as cm:
            s1.get("widget", "W-1")
        self.assertEqual((cm.exception.found, cm.exception.supported), (2, 1))

    def test_older_version_needs_registered_migration(self):
        s1, s2 = self._stores()
        s1.create("widget", {"id": "W-1"}, provenance=PROV)
        with self.assertRaises(UnsupportedSchemaVersion):
            s2.get("widget", "W-1")

    def test_older_version_migrates_on_read_without_rewriting(self):
        s1, s2 = self._stores(migrations={("widget", 1): lambda b: {**b, "label": "migrated"}})
        s1.create("widget", {"id": "W-1"}, provenance=PROV)
        before = (self.tmp / "evo" / "records" / "widget" / "W-1.json").read_bytes()
        r = s2.get("widget", "W-1")
        self.assertEqual((r.body["label"], r.migrated_from, r.schema_version), ("migrated", 1, 1))
        self.assertEqual((self.tmp / "evo" / "records" / "widget" / "W-1.json").read_bytes(), before)


CHILD = textwrap.dedent(r'''
    import os, sys, datetime as dt
    sys.path.insert(0, sys.argv[1])
    from oos.records import RecordStore, SchemaRegistry, load_record_types, DuplicateRecordError, ConcurrencyConflict
    repo, root, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    schemas = SchemaRegistry(os.path.join(repo, "schemas"))
    types = load_record_types(os.path.join(repo, "orchestration", "kernel", "record_types.json"))
    def body(n):
        return {"id": f"DEC-{n:04d}", "title": "t", "level": "D1", "decision_class": "general", "status": "decided",
                "decided_by": "orchestrator", "date": "2026-10-02",
                "scores": {k: 0 for k in ("impact","reversibility","uncertainty","cost","security","vision_alignment")}}
    prov = {"actor": "child"}
    if mode == "die-during-write":
        class Dying(RecordStore):
            def _install_new(self, tmp, final):
                os._exit(7)  # temp file written and fsynced; never installed
        Dying(root, schemas, types).create("decision-record", body(1), provenance=prov)
    elif mode == "die-holding-lock":
        s = RecordStore(root, schemas, types)
        lock = s._lock(); lock.__enter__()
        print("locked", flush=True)
        os._exit(9)
    elif mode == "create-range":
        s = RecordStore(root, schemas, types, lock_timeout_s=60)
        start, count = int(sys.argv[4]), int(sys.argv[5])
        for n in range(start, start + count):
            s.create("decision-record", body(n), provenance=prov)
    elif mode == "race-same-id":
        s = RecordStore(root, schemas, types, lock_timeout_s=60)
        try:
            s.create("decision-record", body(9999), provenance=prov); print("won")
        except DuplicateRecordError:
            print("lost")
    elif mode == "race-replace":
        s = RecordStore(root, schemas, types, lock_timeout_s=60)
        t = {"id": "TASK-0001", "node_type": "task", "title": "x", "state": sys.argv[4]}
        try:
            s.replace("task-node", t, provenance=prov, expected_revision=1); print("won")
        except ConcurrencyConflict:
            print("lost")
''')


def run_child(*args, wait=True):
    cmd = [sys.executable, "-c", CHILD, str(ROOT), *map(str, args)]
    if wait:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


class CrashSafety(Base):
    def test_process_dies_during_write_leaves_no_partial_record(self):
        p = run_child(self.tmp / "store", "die-during-write")
        self.assertEqual(p.returncode, 7, p.stderr)
        with self.assertRaises(RecordNotFound):
            self.store.get("decision-record", "DEC-0001")
        self.assertEqual(self.store.ids("decision-record"), [])
        self.assertTrue(any("leftover temp file" in x for x in self.store.verify()))
        self.assertEqual(self.store.remove_temp_files(), 1)
        self.assertEqual(self.store.verify(), [])
        self.store.create("decision-record", decision(1), provenance=PROV)  # the write can simply be retried

    def test_lock_released_when_holder_dies(self):
        p = run_child(self.tmp / "store", "die-holding-lock")
        self.assertEqual(p.returncode, 9, p.stderr)
        quick = RecordStore(self.tmp / "store", SCHEMAS, TYPES, lock_timeout_s=2)
        quick.create("decision-record", decision(5), provenance=PROV)


class Concurrency(Base):
    def test_parallel_writers_from_separate_processes(self):
        procs = [run_child(self.tmp / "store", "create-range", 1 + i * 20, 20, wait=False) for i in range(5)]
        for p in procs:
            _, err = p.communicate(timeout=180)
            self.assertEqual(p.returncode, 0, err)
        self.assertEqual(len(self.store.ids("decision-record")), 100)
        self.assertEqual(self.store.verify(), [])

    def test_racing_creates_of_the_same_id_have_one_winner(self):
        procs = [run_child(self.tmp / "store", "race-same-id", wait=False) for _ in range(6)]
        outcomes = [p.communicate(timeout=120)[0].strip() for p in procs]
        self.assertEqual(sorted(outcomes), ["lost"] * 5 + ["won"])

    def test_racing_replaces_have_one_winner(self):
        self.store.create("task-node", task(), provenance=PROV)
        procs = [run_child(self.tmp / "store", "race-replace", s, wait=False) for s in ("in_progress", "blocked", "failed", "verifying")]
        outcomes = [p.communicate(timeout=120)[0].strip() for p in procs]
        self.assertEqual(sorted(outcomes), ["lost"] * 3 + ["won"])
        self.assertEqual(self.store.get("task-node", "TASK-0001").revision, 2)
        self.assertEqual(len(self.store.history("task-node", "TASK-0001")), 1)


if __name__ == "__main__":
    unittest.main()
