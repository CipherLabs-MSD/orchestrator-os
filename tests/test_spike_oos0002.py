"""Evidence tests for the OOS-0002 runtime spike (disposable code under spikes/oos-0002).

They keep the ADR-0008 evidence reproducible on any machine that runs the suite. The POSIX
branches of the spike only get exercised when this runs on macOS or Linux. Node experiments
run only when OOS_SPIKE_NODE points to a Node binary.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

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
        if pr.IS_WINDOWS:
            # On Windows the Job Object (KILL_ON_JOB_CLOSE) must kill the tree at the crash itself,
            # before recovery runs: `job` alone would also pass if recover()'s taskkill did the work.
            # On POSIX a process group outlives the crash until recovery kills it (ADR-0008), so
            # job_before_recovery is reported there, not asserted.
            self.assertEqual(r["job_before_recovery"], {"worker": False, "grandchild": False})

    def test_recovery_after_crash_runs_every_task_exactly_once(self):
        r = pr.e5_recovery()
        self.assertTrue(r["every_task_succeeded_exactly_once"])
        self.assertEqual(r["torn_lines_tolerated"], 1)
        statuses = {t: s["status"] for t, s in r["recovery"]["tasks"].items()}
        self.assertEqual(statuses, {"T1": "succeeded", "T2": "succeeded", "T3": "interrupted", "T4": "interrupted"})

    def test_paths_with_spaces_and_non_ascii(self):
        r = pr.e6_paths_and_signals()
        self.assertTrue(r["utf8_unicode_file_created_correctly"])


class ProcessTreeKill(unittest.TestCase):
    def test_tree_kill_after_worker_exit_reaches_descendants(self):
        # The terminal-state reap in run_worker calls kill_tree after the worker itself has exited
        # and been reaped. The kill must still reach what it left behind (OOS-0023: on POSIX,
        # os.getpgid of the reaped worker raised ProcessLookupError and nothing was killed).
        tree = pr.ProcessTree()
        p = subprocess.Popen([sys.executable, str(pr.PROVIDER)], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, text=True, encoding="utf-8", **tree.spawn_kwargs())
        tree.adopt(p.pid)
        p.stdin.write(json.dumps({"task_id": "reap", "behavior": "leave_grandchild", "duration_s": 0.1}) + "\n")
        p.stdin.flush()
        gc = next(json.loads(line)["pid"] for line in p.stdout if '"grandchild"' in line)
        p.stdin.close()
        p.wait(timeout=30)
        try:
            self.assertTrue(pr.pid_alive(gc), "precondition: the grandchild outlives the worker")
            tree.kill_tree(p.pid)
            deadline = time.monotonic() + 5
            while pr.pid_alive(gc) and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertFalse(pr.pid_alive(gc))
        finally:
            pr.force_kill_pid_tree(gc)
            p.stdout.close()


class RecoveryKillsRecordedTrees(unittest.TestCase):
    def test_recovery_kills_recorded_group_after_its_leader_exited(self):
        # EXECUTION_RUNTIME §4/§5.1 and ADR-0008: after an OOS crash, recovery kills the surviving
        # recorded tree of every interrupted task, from the journal alone. The leader may already be
        # gone while a descendant lives on in its group (OOS-0023).
        tree = pr.ProcessTree()
        p = subprocess.Popen([sys.executable, str(pr.PROVIDER)], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, text=True, encoding="utf-8", **tree.spawn_kwargs())
        tree.adopt(p.pid)
        with tempfile.TemporaryDirectory() as d:
            jp = Path(d) / "run.journal.jsonl"
            j = pr.Journal(jp)
            j.append(event="dispatch_intent", task_id="R", attempt=1, idempotency_key="R:1")
            j.append(event="spawned", task_id="R", attempt=1, **tree.record(p.pid))
            p.stdin.write(json.dumps({"task_id": "R", "behavior": "leave_grandchild", "duration_s": 0.1}) + "\n")
            p.stdin.flush()
            gc = next(json.loads(line)["pid"] for line in p.stdout if '"grandchild"' in line)
            p.stdin.close()
            p.wait(timeout=30)
            try:
                self.assertTrue(pr.pid_alive(gc), "precondition: the grandchild outlives the worker")
                # Simulate the OOS crash for this test's own tree before recovering. On Windows this
                # test process holds the Job Object handle; in a real crash that handle dies with OOS
                # and KILL_ON_JOB_CLOSE kills the tree. Keeping it open would leave the tree alive
                # because of the test itself, a state no crash produces. On POSIX close() does nothing
                # and the group lives on until recover() kills it.
                tree.close()
                report = pr.recover(jp, ["R"])
                self.assertEqual(report["tasks"]["R"]["status"], "interrupted")
                deadline = time.monotonic() + 5
                while pr.pid_alive(gc) and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertFalse(pr.pid_alive(gc))
            finally:
                pr.force_kill_pid_tree(gc)
                p.stdout.close()


@unittest.skipIf(pr.IS_WINDOWS, "process-group kills (os.killpg) exist only on POSIX")
class KillPermissionErrors(unittest.TestCase):
    """A recorded group id recycled by another user's processes gives PermissionError. It is
    logged and recovery goes on with the other tasks (OOS-0023 review, F4)."""

    def test_recovery_continues_after_permission_error(self):
        killed = []

        def fake_killpg(pgid, sig):
            if pgid == 111111:
                raise PermissionError(1, "Operation not permitted")
            killed.append(pgid)

        with tempfile.TemporaryDirectory() as d:
            jp = Path(d) / "run.journal.jsonl"
            j = pr.Journal(jp)
            for t, pgid in (("P", 111111), ("Q", 222222)):
                j.append(event="dispatch_intent", task_id=t, attempt=1, idempotency_key=f"{t}:1")
                j.append(event="spawned", task_id=t, attempt=1, pid=pgid, pgid=pgid)
            with mock.patch.object(pr.os, "killpg", fake_killpg), \
                    mock.patch.object(pr, "pid_alive", return_value=False), \
                    self.assertLogs("oos.spike.runner", "WARNING") as logs:
                report = pr.recover(jp, ["P", "Q"])
        self.assertEqual(report["tasks"]["P"]["status"], "interrupted")
        self.assertIn("PermissionError", report["tasks"]["P"]["kill_error"])
        self.assertEqual(report["tasks"]["Q"]["status"], "interrupted")
        self.assertNotIn("kill_error", report["tasks"]["Q"])
        self.assertEqual(killed, [222222])
        self.assertIn("111111", logs.output[0])

    def test_kill_tree_logs_permission_error(self):
        def denied(pgid, sig):
            raise PermissionError(1, "Operation not permitted")

        with mock.patch.object(pr.os, "killpg", denied), \
                self.assertLogs("oos.spike.runner", "WARNING") as logs:
            pr.ProcessTree().kill_tree(333333)
        self.assertIn("333333", logs.output[0])


@unittest.skipUnless(os.environ.get("OOS_SPIKE_NODE") and Path(os.environ["OOS_SPIKE_NODE"]).exists(),
                     "set OOS_SPIKE_NODE to run the Node comparison")
class NodeRuntimeEvidence(unittest.TestCase):
    def test_node_runner_classifies_and_shows_descendant_escape(self):
        proc = subprocess.run([os.environ["OOS_SPIKE_NODE"], str(SPIKE / "node_runner.mjs"), "e2"],
                              capture_output=True, text=True, encoding="utf-8",
                              env={**os.environ, "OOS_SPIKE_PYTHON": sys.executable}, timeout=120)
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
