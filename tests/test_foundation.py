"""Tests for the OOS-0001 foundation: the repo passes every validator check, and the
validator itself catches the failures it claims to catch (negative tests).

Run: python -m unittest discover tests
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import validate as v  # noqa: E402


class RepositoryPassesAllChecks(unittest.TestCase):
    def test_each_check_passes(self):
        for name, fn in v.CHECKS:
            with self.subTest(check=name):
                self.assertEqual(fn(), [], f"check '{name}' failed")


class MiniSchemaValidator(unittest.TestCase):
    SCHEMA = {
        "type": "object",
        "additionalProperties": False,
        "required": ["id", "n"],
        "properties": {
            "id": {"type": "string", "pattern": "^X-[0-9]{2}$"},
            "n": {"type": "integer", "minimum": 0, "maximum": 3},
            "tags": {"type": "array", "items": {"type": "string", "enum": ["a", "b"]}},
            "maybe": {"type": ["string", "null"], "pattern": "^ok$"},
        },
    }

    def test_valid_instance(self):
        self.assertEqual(v.validate_instance({"id": "X-01", "n": 2, "tags": ["a"], "maybe": None}, self.SCHEMA), [])

    def test_rejects_missing_required_extra_property_pattern_range_enum(self):
        errors = v.validate_instance({"id": "Y-1", "n": 9, "tags": ["z"], "extra": 1}, self.SCHEMA)
        joined = "\n".join(errors)
        for fragment in ("does not match", "> maximum", "not in", "unexpected property 'extra'"):
            self.assertIn(fragment, joined)
        self.assertIn("missing required 'n'", "\n".join(v.validate_instance({"id": "X-01"}, self.SCHEMA)))

    def test_bool_is_not_integer(self):
        self.assertTrue(v.validate_instance({"id": "X-01", "n": True}, self.SCHEMA))


class GraphChecks(unittest.TestCase):
    def test_cycle_detected(self):
        self.assertIsNotNone(v.find_cycle({"A": ["B"], "B": ["C"], "C": ["A"]}))

    def test_dag_has_no_cycle(self):
        self.assertIsNone(v.find_cycle({"A": [], "B": ["A"], "C": ["A", "B"]}))

    def test_waves(self):
        self.assertEqual(v.waves({"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}), {"A": 0, "B": 1, "C": 1, "D": 2})


class DecisionClassifier(unittest.TestCase):
    def setUp(self):
        self.policy = v.load_json("orchestration/decision_policy.json")

    def test_policy_change_is_always_d4(self):
        # The system cannot raise its own authority, even for a "trivial" change.
        self.assertEqual(v.classify([0, 0, 0, 0, 0, 0], "oos_policy_or_authority_change", self.policy), "D4")

    def test_combination_rule_escalates(self):
        # Each dimension alone maps to D3, but together impact>=2 and reversibility>=2 means D4.
        self.assertEqual(v.classify([2, 2, 0, 0, 0, 0], "general", self.policy), "D4")

    def test_architecture_is_not_automatically_d4(self):
        # Meaningful but reversible, intent-aligned architecture is D3, not "ask the human".
        self.assertEqual(v.classify([2, 1, 1, 0, 0, 1], "new_service_or_datastore", self.policy), "D3")


class ContextFileChecks(unittest.TestCase):
    HEADER = "<!-- context-file\ncategory: creative\nstatus: {status}\nentries: {n}\n-->\n# T\n"
    ENTRY = ("### CTX-0001 — t\n- statement: s\n- kind: user_preference\n- category: creative\n"
             "- scope: global\n- strength: weak\n- confidence: 0.5\n- source: stated-directly\n"
             "- learned: 2026-10-01\n- applies_to_capabilities: [ux]\n- status: active\n")

    def test_placeholder_with_entry_is_rejected(self):
        text = self.HEADER.format(status="placeholder", n=1) + "PLACEHOLDER\n" + self.ENTRY
        errors = v.check_context_text("x.md", text, "creative")
        self.assertTrue(any("marked placeholder but contains entries" in e for e in errors))

    def test_curated_valid_entry_passes(self):
        text = self.HEADER.format(status="curated", n=1) + self.ENTRY
        self.assertEqual(v.check_context_text("x.md", text, "creative"), [])

    def test_entry_in_wrong_file_is_rejected(self):
        text = self.HEADER.format(status="curated", n=1).replace("creative", "profile") + self.ENTRY
        errors = v.check_context_text("x.md", text, "profile")
        self.assertTrue(any("belongs in another file" in e for e in errors))

    def test_entry_missing_provenance_is_rejected(self):
        text = self.HEADER.format(status="curated", n=1) + self.ENTRY.replace("- source: stated-directly\n", "")
        self.assertTrue(any("missing required 'source'" in e for e in v.check_context_text("x.md", text, "creative")))

    def test_commented_template_is_not_an_entry(self):
        text = self.HEADER.format(status="placeholder", n=0) + "PLACEHOLDER\n<!--\n" + self.ENTRY + "-->\n"
        self.assertEqual(v.check_context_text("x.md", text, "creative"), [])


class SecretScan(unittest.TestCase):
    def test_detects_token_shapes(self):
        fake = "gh" + "p_" + "A" * 36  # assembled at runtime so this file never contains a token
        self.assertTrue(v.scan_secrets(f"token = {fake}"))
        self.assertTrue(v.scan_secrets("-----BEGIN " + "PRIVATE KEY-----"))

    def test_ignores_ordinary_text(self):
        self.assertEqual(v.scan_secrets("the sk-learn library and ghp docs"), [])


if __name__ == "__main__":
    unittest.main()
