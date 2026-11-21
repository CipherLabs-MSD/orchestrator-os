"""OOS-0003 append-only log (journal substrate): durability and integrity tests."""
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

from oos.records import AppendLog, CorruptLogError, RecordTooLarge, SchemaRegistry, SchemaValidationError  # noqa: E402

SCHEMAS = SchemaRegistry(ROOT / "schemas")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="oos-log-"))
        self.path = self.tmp / "run" / "journal.jsonl"
        self.log = AppendLog(self.path, SCHEMAS)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class AppendAndRead(Base):
    def test_round_trip_sequence_and_chain(self):
        a = self.log.append("run_started", {"run": "R-1", "note": "début ✓"})
        b = self.log.append("dispatch_intent", {"task": "T-1", "attempt": 1})
        read = self.log.read()
        self.assertFalse(read.torn_tail)
        self.assertEqual([e["seq"] for e in read.entries], [1, 2])
        self.assertIsNone(read.entries[0]["prev"])
        self.assertEqual(read.entries[1]["prev"], a["check"])
        self.assertEqual(read.entries[1], b)
        self.assertEqual(read.entries[0]["data"]["note"], "début ✓")

    def test_invalid_kind_and_oversize_rejected_without_writing(self):
        with self.assertRaises(SchemaValidationError):
            self.log.append("Bad Kind!", {})
        with self.assertRaises(RecordTooLarge):
            AppendLog(self.path, SCHEMAS, max_line_bytes=200).append("big", {"x": "y" * 500})
        self.assertFalse(self.path.exists())

    def test_data_schema_enforced(self):
        log = AppendLog(self.tmp / "ev.jsonl", SCHEMAS, data_schema="failed-approach")
        with self.assertRaises(SchemaValidationError):
            log.append("failed", {"id": "FAILED-0001"})
        self.assertEqual(log.read().entries, [])


class TornAndCorrupt(Base):
    def setUp(self):
        super().setUp()
        for i in range(3):
            self.log.append("step", {"i": i})

    def test_torn_tail_tolerated_reported_then_truncated_by_next_append(self):
        with open(self.path, "ab") as f:
            f.write(b'{"seq": 4, "kind": "ste')  # crash mid-append
        read = self.log.read()
        self.assertTrue(read.torn_tail)
        self.assertEqual(len(read.entries), 3)
        with self.assertRaises(CorruptLogError):
            self.log.read(tolerate_torn_tail=False)
        e = self.log.append("step", {"i": 3})
        self.assertEqual(e["seq"], 4)
        read = self.log.read(tolerate_torn_tail=False)
        self.assertEqual([x["seq"] for x in read.entries], [1, 2, 3, 4])

    def test_edited_line_detected(self):
        lines = self.path.read_text(encoding="utf-8").splitlines(keepends=True)
        lines[1] = lines[1].replace('"i":1', '"i":7')
        self.path.write_text("".join(lines), encoding="utf-8")
        with self.assertRaises(CorruptLogError) as cm:
            self.log.read()
        self.assertEqual((cm.exception.line_no, cm.exception.reason), (2, "checksum mismatch"))

    def test_removed_line_detected(self):
        lines = self.path.read_text(encoding="utf-8").splitlines(keepends=True)
        self.path.write_text(lines[0] + lines[2], encoding="utf-8")
        with self.assertRaises(CorruptLogError) as cm:
            self.log.read()
        self.assertIn("sequence gap", cm.exception.reason)

    def test_forged_line_with_valid_own_checksum_breaks_the_chain(self):
        from oos.records import canonical
        lines = self.path.read_text(encoding="utf-8").splitlines(keepends=True)
        forged = json.loads(lines[1])
        forged["data"] = {"i": 42}
        forged.pop("check")
        forged["check"] = canonical.digest(forged)  # self-consistent forgery
        lines[1] = canonical.dumps_line(forged) + "\n"
        self.path.write_text("".join(lines), encoding="utf-8")
        with self.assertRaises(CorruptLogError) as cm:
            self.log.read()
        self.assertEqual(cm.exception.line_no, 3)
        self.assertIn("hash chain broken", cm.exception.reason)

    def test_garbage_line_in_the_middle_is_not_tolerated(self):
        lines = self.path.read_text(encoding="utf-8").splitlines(keepends=True)
        self.path.write_text(lines[0] + "not json\n" + lines[1], encoding="utf-8")
        with self.assertRaises(CorruptLogError):
            self.log.read()

    def test_corrupt_log_refuses_further_appends(self):
        self.path.write_text(self.path.read_text(encoding="utf-8").replace('"i":0', '"i":9'), encoding="utf-8")
        with self.assertRaises(CorruptLogError):
            self.log.append("step", {"i": 4})


CHILD = textwrap.dedent(r'''
    import os, sys
    sys.path.insert(0, sys.argv[1])
    from oos.records import AppendLog, SchemaRegistry
    log = AppendLog(sys.argv[2], SchemaRegistry(os.path.join(sys.argv[1], "schemas")), lock_timeout_s=60)
    for i in range(int(sys.argv[4])):
        log.append("step", {"writer": sys.argv[3], "i": i})
''')


class ConcurrentAppends(Base):
    def test_processes_append_without_interleaving_or_gaps(self):
        procs = [subprocess.Popen([sys.executable, "-c", CHILD, str(ROOT), str(self.path), f"w{k}", "25"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for k in range(4)]
        for p in procs:
            _, err = p.communicate(timeout=180)
            self.assertEqual(p.returncode, 0, err)
        read = self.log.read(tolerate_torn_tail=False)
        self.assertEqual([e["seq"] for e in read.entries], list(range(1, 101)))
        per_writer = {}
        for e in read.entries:
            per_writer.setdefault(e["data"]["writer"], []).append(e["data"]["i"])
        self.assertEqual({k: v for k, v in per_writer.items()}, {f"w{k}": list(range(25)) for k in range(4)})
        self.assertTrue(all(json.loads(l) for l in self.path.read_text(encoding="utf-8").splitlines()))


if __name__ == "__main__":
    unittest.main()
