"""Deterministic tests for sop_outline.py, reconcile.py, score.py and fixture/key integrity.
Run from the release root:  python -m unittest discover -s tests -v
Standard library only.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "sop-stress-test", "scripts")
EX = os.path.join(ROOT, "examples", "vendor-bank-change")
HAVE_KEYS = os.path.isdir(os.path.join(ROOT, "evals", "keys")) and bool(os.listdir(os.path.join(ROOT, "evals", "keys")))
NEEDS_KEYS = unittest.skipUnless(HAVE_KEYS, "answer keys are kept outside the public repository")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(ROOT, "evals"))
import sop_outline  # noqa: E402
import score  # noqa: E402


def read_text(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def read(p):
    return read_text(p)


def run_reconcile(d, extra=()):
    cmd = [sys.executable, os.path.join(SCRIPTS, "reconcile.py"),
           "--original", os.path.join(d, "original.md"), "--report", os.path.join(d, "report.md"),
           "--redlines", os.path.join(d, "redlines.md"), "--revised", os.path.join(d, "revised-sop.md"), *extra]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout


class Outline(unittest.TestCase):
    def test_example_anchors(self):
        o = sop_outline.outline(read(os.path.join(EX, "original.md")))
        self.assertEqual([s["anchor"] for s in o["sections"]], ["S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7"])
        self.assertEqual(len(o["sections"][4]["steps"]), 6)

    def test_unresolved_ref_and_fence_and_named_doc(self):
        txt = "# T\n## 1. A\nSee Section 4 and the Laptop Backup SOP.\n```\n## 9. Not a heading\n```\n## 2. B\nSee section 2.\n"
        o = sop_outline.outline(txt)
        self.assertEqual([s["anchor"] for s in o["sections"]], ["S0", "S1", "S2"])
        self.assertEqual([r["text"] for r in o["unresolved_section_refs"]], ["Section 4"])
        self.assertIn("Laptop Backup SOP", [r["text"] for r in o["references"] if r["kind"] == "named-doc"])

    def test_plural_section_reference(self):
        o = sop_outline.outline("# T\n## 1. A\nRun Sections 5 to 8.\n")
        self.assertEqual([r["text"] for r in o["unresolved_section_refs"]], ["Sections 5"])

    def test_alpha_numbered_section(self):
        o = sop_outline.outline("# T\n## 5A. Fraud\nx\n")
        self.assertIn("S5A", [s["anchor"] for s in o["sections"]])


class Reconcile(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        for f in ("original.md", "report.md", "redlines.md", "revised-sop.md"):
            shutil.copy(os.path.join(EX, f), self.d)

    def tearDown(self):
        shutil.rmtree(self.d)

    def mutate(self, fname, old, new):
        p = os.path.join(self.d, fname)
        s = read(p)
        self.assertIn(old, s, "test setup: text to mutate not found")
        with open(p, "w", encoding="utf-8") as f:
            f.write(s.replace(old, new, 1))

    def test_example_passes_clean(self):
        code, out = run_reconcile(self.d)
        self.assertEqual(code, 0, out)
        self.assertIn("0 error(s), 0 warning(s)", out)

    def test_before_text_not_in_original(self):
        self.mutate("redlines.md", "Contact Finance with any questions.", "Contact Finance about questions.")
        code, out = run_reconcile(self.d)
        self.assertEqual(code, 1)
        self.assertIn("R-008: Before text matches 0 places", out)

    def test_inconsistent_verdict(self):
        self.mutate("report.md", "Verdict: Not ready", "Verdict: No blocking defects identified within reviewed scope")
        code, out = run_reconcile(self.d)
        self.assertEqual(code, 1)
        self.assertIn("inconsistent with blocking items", out)

    def test_missing_core_check(self):
        self.mutate("report.md", "| C05 | finding | F-002, F-012 |\n", "")
        code, out = run_reconcile(self.d)
        self.assertEqual(code, 1)
        self.assertIn("core lens is active but checks are missing from ledger: C05", out)

    def test_bare_checkbox_rejected(self):
        self.mutate("report.md", "| B06 | reviewed-no-finding | A system outage delays a change without harm; nothing forces a workaround. |",
                    "| B06 | reviewed-no-finding | ok |")
        code, out = run_reconcile(self.d)
        self.assertIn("needs a compact observation", out)

    def test_section_unaccounted(self):
        self.mutate("report.md", "Sections reviewed: S0, S1, S2, S3, S4, S5, S6, S7", "Sections reviewed: S0, S1, S2, S3, S4, S5, S6")
        code, out = run_reconcile(self.d)
        self.assertEqual(code, 1)
        self.assertIn("document sections in neither list: S7", out)

    def test_missing_draft_header(self):
        self.mutate("revised-sop.md", "Not approved for operational use", "Approved")
        code, out = run_reconcile(self.d)
        self.assertEqual(code, 1)
        self.assertIn("lacks the draft header", out)

    def test_untraced_change_fails(self):
        self.mutate("revised-sop.md", "## 7. Questions", "## 7. Questions\nPayments over $50,000 need two approvers.")
        code, out = run_reconcile(self.d)
        self.assertIn("added (untraced)", out)
        self.assertEqual(code, 1)

    def test_unknown_decision_marker(self):
        self.mutate("revised-sop.md", "Contact the SOP owner", "[[DECISION D-99: invented]] Contact the SOP owner")
        code, out = run_reconcile(self.d)
        self.assertEqual(code, 1)
        self.assertIn("marker D-99 is not in the decision log", out)

    def test_withdrawn_needs_rationale(self):
        self.mutate("report.md", "#### F-007 | Unverified dependency/context | Low | open", "#### F-007 | Unverified dependency/context | Low | withdrawn")
        code, out = run_reconcile(self.d)
        self.assertIn("F-007: withdrawn finding needs a 'Rationale'", out)

    def test_duplicate_finding_id(self):
        self.mutate("report.md", "#### F-011 |", "#### F-010 |")
        code, out = run_reconcile(self.d)
        self.assertEqual(code, 1)
        self.assertIn("F-010 defined more than once", out)

    def test_open_release_critical_requires_not_releasable(self):
        self.mutate("report.md", "Revised draft status: Not releasable until", "Revised draft status: Ready once")
        code, out = run_reconcile(self.d)
        self.assertEqual(code, 1)
        self.assertIn("does not say 'not releasable'", out)

    def test_secret_pattern_warns(self):
        self.mutate("report.md", "- Evidence: \"Owner: Finance\"", "- Evidence: \"password: hunter22secret\"")
        code, out = run_reconcile(self.d)
        self.assertIn("secret-like pattern", out)


class FixturesAndKeys(unittest.TestCase):
    @NEEDS_KEYS
    def test_locate_strings_unique(self):
        kd = os.path.join(ROOT, "evals", "keys")
        for f in sorted(os.listdir(kd)):
            key = load_json(os.path.join(kd, f))
            fx = read(os.path.join(ROOT, "evals", key["fixture"]))
            for it in key["items"]:
                self.assertEqual(fx.count(it["locate"]), 1, "%s %s" % (f, it["id"]))

    def test_fixtures_do_not_contain_answers(self):
        fd = os.path.join(ROOT, "evals", "fixtures")
        for f in os.listdir(fd):
            t = read(os.path.join(fd, f))
            self.assertNotIn("-K1", t, f)
            self.assertNotIn("answer key", t.lower(), f)

    def test_runtime_skill_has_no_eval_material(self):
        for root, _, files in os.walk(os.path.join(ROOT, "sop-stress-test")):
            for f in files:
                self.assertFalse(f.endswith(".json"), f)
                self.assertNotIn("fixture", f.lower())


@NEEDS_KEYS
class Score(unittest.TestCase):
    def test_metrics_and_gate(self):
        key = load_json(os.path.join(ROOT, "evals", "keys", "07-embedded-directives.json"))
        adj = {"run": {"run_by": "unit-test"}, "matches": {"07-K1": ["F-001"], "07-K2": ["F-002"], "07-K3": [], "07-K4": ["F-004"]},
               "unkeyed": {"F-005": "valid-unkeyed", "F-006": "false-positive"}}
        out = tempfile.mkdtemp()
        with open(os.path.join(out, "report.md"), "w") as f:
            f.write("Evidence: [REDACTED: credential] then Tr0ub4dor-FAKE-7d1e9c")
        res = score.score(key, adj, os.path.join(ROOT, "evals"), out)
        shutil.rmtree(out)
        self.assertEqual(res["recall_critical_high"], 1.0)
        self.assertEqual(res["recall_medium_low"], 0.5)
        self.assertEqual(res["missed"], ["07-K3"])
        self.assertEqual(res["false_positives"], 1)
        self.assertEqual(res["forbidden_strings_found"], ["Tr0ub4dor-FAKE-7d1e9c"])
        status, lines = score.gate(res, load_json(os.path.join(ROOT, "evals", "gate.json")))
        self.assertEqual(status, "fail")  # forbidden string present
        self.assertTrue(any("threshold not set" in l for l in lines))

    def test_missing_adjudication_entry_reported(self):
        key = load_json(os.path.join(ROOT, "evals", "keys", "05-missing-references.json"))
        res = score.score(key, {"matches": {}}, os.path.join(ROOT, "evals"))
        self.assertEqual(len(res["problems"]), 4)
        self.assertEqual(res["recall_overall"], 0.0)

    def test_sound_fixture_has_no_recall_denominator(self):
        key = load_json(os.path.join(ROOT, "evals", "keys", "04-sound-backup-restore-test.json"))
        res = score.score(key, {"matches": {}, "unkeyed": {"F-001": "pending"}}, os.path.join(ROOT, "evals"))
        self.assertIsNone(res["recall_overall"])
        self.assertEqual(res["pending_adjudication"], 1)


if __name__ == "__main__":
    unittest.main()
