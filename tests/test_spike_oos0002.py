"""Evidence tests for the OOS-0002 runtime spike (disposable code under spikes/oos-0002).

They keep the ADR-0008 evidence reproducible on any machine that runs the suite. The POSIX
branches of the spike only get exercised when this runs on macOS or Linux. Node experiments
run only when OOS_SPIKE_NODE points to a Node binary.
"""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPIKE = ROOT / "spikes" / "oos-0002"
sys.path.insert(0, str(SPIKE))
import py_runner as pr  # noqa: E402


class PythonRuntimeEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e2 = {w["task_id"]: w for w in pr.e2_concurrency()["workers"]}

    def test_concurrent_workers_reach_independent_terminal_states(self):
        expected = {"A-ok-fast": "succeeded", "B-ok-slow": "succeeded", "C-hang": "timed_out",
                    "D-cancel": "cancelled", "E-crash": "crashed", "F-ask": "needs_input",
                    "G-ignores-cancel": "cancelled_forced", "H-leaves-grandchild": "succeeded"}
        self.assertEqual({k: v["status"] for k, v in self.e2.items()}, expected)

    def test_failure_classification_marks_retryability(self):
        self.assertTrue(self.e2["C-hang"]["retryable"])
        self.assertTrue(self.e2["E-crash"]["retryable"])
        self.assertFalse(self.e2["D-cancel"]["retryable"])

    def test_torn_event_is_counted_not_fatal(self):
        self.assertEqual(self.e2["E-crash"]["malformed_events"], 1)

    def test_descendants_are_reaped_at_terminal_state(self):
        self.assertTrue(self.e2["H-leaves-grandchild"]["descendants_reaped_after_exit"])
        self.assertFalse(self.e2["H-leaves-grandchild"]["grandchild_alive_after"])

    def test_tree_kill_reaches_grandchildren(self):
        self.assertFalse(pr.e3_tree_kill()["tree_kill_grandchild_survived"])

    def test_orchestrator_crash_leaves_no_orphans_when_tree_is_owned(self):
        r = pr.e4_orchestrator_crash()
        self.assertEqual(r["job"], {"worker": False, "grandchild": False})

    def test_recovery_after_crash_runs_every_task_exactly_once(self):
        r = pr.e5_recovery()
        self.assertTrue(r["every_task_succeeded_exactly_once"])
        self.assertEqual(r["torn_lines_tolerated"], 1)
        statuses = {t: s["status"] for t, s in r["recovery"]["tasks"].items()}
        self.assertEqual(statuses, {"T1": "succeeded", "T2": "succeeded", "T3": "interrupted", "T4": "interrupted"})

    def test_paths_with_spaces_and_non_ascii(self):
        r = pr.e6_paths_and_signals()
        self.assertTrue(r["utf8_unicode_file_created_correctly"])


@unittest.skipUnless(os.environ.get("OOS_SPIKE_NODE") and Path(os.environ["OOS_SPIKE_NODE"]).exists(),
                     "set OOS_SPIKE_NODE to run the Node comparison")
class NodeRuntimeEvidence(unittest.TestCase):
    def test_node_runner_classifies_and_shows_descendant_escape(self):
        proc = subprocess.run([os.environ["OOS_SPIKE_NODE"], str(SPIKE / "node_runner.mjs"), "e2"],
                              capture_output=True, text=True, encoding="utf-8",
                              env={**os.environ, "OOS_SPIKE_PYTHON": getattr(sys, "_base_executable", None) or sys.executable}, timeout=120)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        workers = {w["task_id"]: w for w in json.loads(proc.stdout)["e2"]["workers"]}
        self.assertEqual(workers["C-hang"]["status"], "timed_out")
        self.assertEqual(workers["E-crash"]["status"], "crashed")


class SpikeIsolation(unittest.TestCase):
    def test_spike_files_are_labelled_disposable(self):
        for p in SPIKE.glob("*.*"):
            if p.suffix in (".py", ".mjs"):
                self.assertIn("DISPOSABLE SPIKE CODE", p.read_text(encoding="utf-8"), p.name)


if __name__ == "__main__":
    unittest.main()
