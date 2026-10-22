"""Regression tests for v0.1.1. Each reproduces a reported validation gap.
Written before the fixes; the pre-fix run is saved in evals/results/regression-before.txt.
"""
import json
import os
import re
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
sys.path.insert(0, os.path.join(ROOT, "evals"))
import score  # noqa: E402


def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def wr(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def reconcile(d, names=("original.md", "report.md", "redlines.md", "revised-sop.md")):
    o, r, l, v = (os.path.join(d, n) for n in names)
    p = subprocess.run([sys.executable, os.path.join(SCRIPTS, "reconcile.py"), "--original", o, "--report", r,
                        "--redlines", l, "--revised", v], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class Base(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        for f in ("original.md", "report.md", "redlines.md", "revised-sop.md"):
            shutil.copy(os.path.join(EX, f), self.d)

    def tearDown(self):
        shutil.rmtree(self.d)

    def edit(self, name, fn):
        p = os.path.join(self.d, name)
        wr(p, fn(rd(p)))


class ReportedGaps(Base):
    def test_1_removing_lens_rows_fails(self):
        self.edit("report.md", lambda s: re.sub(r"^\| [BK]\d\d.*\n", "", s, flags=re.M))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_2_removing_challenge_and_scenario_fails(self):
        self.edit("report.md", lambda s: re.sub(r"^- (Challenge|Failure scenario):.*\n", "", s, flags=re.M))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_3_bogus_redline_anchors_fail(self):
        self.edit("redlines.md", lambda s: re.sub(r"^(#### R-\d{3}) \| \S+ \|", r"\1 | S999 |", s, flags=re.M))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_4_duplicated_line_fails(self):
        self.edit("revised-sop.md", lambda s: s + "\n7. After approval, update the bank details in the vendor record in the accounting system.\n")
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_5_untraced_instruction_fails(self):
        self.edit("revised-sop.md", lambda s: s + "\nPayments over $50,000 need two approvers.\n")
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_6_gate_not_pass_when_checks_fail(self):
        res = {"recall_critical_high": 1.0, "recall_medium_low": 1.0, "false_positives": 0,
               "behavior_ok": False, "lenses_ok": False, "statuses_ok": False, "verdict_ok": False,
               "problems": ["adjudication maps key item to F-999, which the run did not report"],
               "pending_adjudication": 0}
        g = {"thresholds": {"recall_critical_high": 1.0, "recall_medium_low": 0.5}, "max": {"false_positives": 0}}
        status, _ = score.gate(res, g)
        self.assertEqual(status, "fail")


class RedlineIntegrity(Base):
    def test_before_text_outside_cited_section_fails(self):
        # R-008 cites S7; point it at S4 instead
        self.edit("redlines.md", lambda s: s.replace("#### R-008 | S7 |", "#### R-008 | S4 |"))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)
        self.assertIn("not inside", out)

    def test_reordered_lines_fail(self):
        def swap(s):
            a = "1. The AP Clerk receives the change request from the vendor, usually by email."
            b = "2. Verify the request independently."
            i, j = s.index(a), s.index(b)
            line_b = s[j:s.index("\n", j)]
            s = s.replace(line_b + "\n", "")
            return s.replace(a, line_b + "\n" + a)
        self.edit("revised-sop.md", swap)
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_dropped_unchanged_line_fails(self):
        self.edit("revised-sop.md", lambda s: s.replace("- AP Clerk: receives requests and updates the vendor record.\n", ""))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_changed_instruction_fails(self):
        self.edit("revised-sop.md", lambda s: s.replace("Do not change the vendor record yet.", "Change the vendor record now."))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_formatting_only_differences_pass(self):
        self.edit("revised-sop.md", lambda s: s.replace("\n\n## 6. Records", "\n\n\n## 6. Records").replace(
            "Contact the SOP owner with any questions.", "Contact the SOP owner with any questions.   "))
        code, out = reconcile(self.d)
        self.assertEqual(code, 0, out)

    def test_document_prefixed_anchor_rejected_with_guidance(self):
        self.edit("redlines.md", lambda s: s.replace("#### R-008 | S7 |", "#### R-008 | A:S7 |"))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)
        self.assertIn("one document per run", out)


SECRET = "Zq9-FAKE-SECRET-41aa"
ORIG = """# Rotation SOP

Owner: Platform Engineer

## 1. Credential
Current value: svc password = %s

## 2. Steps
1. Generate a new password in the password manager.
2. Update the service account.
""" % SECRET


class SecretSafeEditing(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        wr(os.path.join(self.d, "original.md"), ORIG)
        wr(os.path.join(self.d, "report.md"), """# SOP Stress Test report: Rotation SOP
Verdict: Not ready
Revised draft status: Not releasable until D-01 is decided.

## Coverage ledger
Sections reviewed: S0, S1, S2
Sections not reviewed: none
Lenses: core (active); business (inactive: no money or vendors); cyber (active: credentials); ai-ops (inactive: no AI)

| Check | Result | Anchors / observation |
|---|---|---|
| C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C13, C14 | reviewed-no-finding | Short test document; checked for this unit test only. |
| C12 | finding | F-001 |
| K01, K02, K03, K04, K05, K06 | not-applicable | Unit-test fixture scope. |
| K07 | finding | F-001 |

## Findings register

#### F-001 | Confirmed defect | Critical | awaiting-owner-decision
- Title: Live credential stored in the SOP
- Check: K07, C12
- Locations: S1
- Evidence: "Current value: svc password = [REDACTED: credential]"
- Failure scenario: Anyone with read access to the SOP can use the credential.
- Challenge: Whole document checked.
- Fix type: doc edit + owner decision
- Proposed fix: R-001; D-01
- Decision: D-01
- Operational verification: unknown

## Decision log

#### D-01 | open | release-critical
- Question: Where is the credential stored and who can retrieve it?
- Owner: [to be named by SOP owner]
- Options: password manager entry named by the owner
- Related findings: F-001
- Draft treatment: marker only
""")
        wr(os.path.join(self.d, "redlines.md"), """# Redlines
#### R-001 | S1 | replace
- Findings: F-001
- Reason: Remove the stored secret; point to the vault entry instead.
Before:
```text
Current value: svc password = [REDACTED: credential]
```
After:
```text
Retrieve the current value from [[DECISION D-01: password manager entry holding this credential]]. Never write it in this document.
```
""")
        body = ORIG.replace("Current value: svc password = %s" % SECRET,
                            "Retrieve the current value from [[DECISION D-01: password manager entry holding this credential]]. Never write it in this document.")
        wr(os.path.join(self.d, "revised-sop.md"),
           "> **DRAFT. Not approved for operational use.**\n> Release-blocking decisions: D-01\n> Non-blocking decisions: none\n<!-- END DRAFT HEADER -->\n" + body)

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_redacted_before_block_validates_without_secret(self):
        code, out = reconcile(self.d)
        self.assertEqual(code, 0, out)
        for n in ("report.md", "redlines.md", "revised-sop.md"):
            self.assertNotIn(SECRET, rd(os.path.join(self.d, n)))
        self.assertNotIn(SECRET, out)

    def test_secret_left_in_revised_fails_without_echo(self):
        p = os.path.join(self.d, "revised-sop.md")
        wr(p, rd(p) + "\nOld value was %s\n" % SECRET)
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)
        self.assertNotIn(SECRET, out)

    def test_secret_echoed_in_report_fails(self):
        p = os.path.join(self.d, "report.md")
        wr(p, rd(p).replace("[REDACTED: credential]\"", SECRET + "\""))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)
        self.assertNotIn(SECRET, out)


@NEEDS_KEYS
class GateAndMapping(unittest.TestCase):
    def setUp(self):
        self.key = json.load(open(os.path.join(ROOT, "evals", "keys", "05-missing-references.json")))
        self.out = tempfile.mkdtemp()
        wr(os.path.join(self.out, "report.md"), "".join(
            "#### F-00%d | Confirmed defect | Medium | open\n- Title: t\n" % i for i in range(1, 6)))
        self.adj = {"run": {}, "matches": {"05-K1": ["F-001"], "05-K2": ["F-002"], "05-K3": ["F-003"], "05-K4": ["F-004"]},
                    "unkeyed": {"F-005": "valid-unkeyed"}, "verdict_ok": True, "lenses_ok": True}
        self.g = {"thresholds": {"recall_critical_high": 1.0, "recall_medium_low": 0.5}, "max": {"false_positives": 0}}

    def tearDown(self):
        shutil.rmtree(self.out)

    def test_clean_run_passes(self):
        res = score.score(self.key, self.adj, os.path.join(ROOT, "evals"), self.out)
        self.assertEqual(res["problems"], [])
        self.assertEqual(score.gate(res, self.g)[0], "pass")

    def test_mapping_to_unreported_finding_fails(self):
        self.adj["matches"]["05-K1"] = ["F-999"]
        res = score.score(self.key, self.adj, os.path.join(ROOT, "evals"), self.out)
        self.assertTrue(any("F-999" in p for p in res["problems"]))
        self.assertEqual(score.gate(res, self.g)[0], "fail")

    def test_unaccounted_finding_fails(self):
        del self.adj["unkeyed"]["F-005"]
        res = score.score(self.key, self.adj, os.path.join(ROOT, "evals"), self.out)
        self.assertTrue(any("F-005" in p for p in res["problems"]))
        self.assertEqual(score.gate(res, self.g)[0], "fail")

    def test_missing_outputs_is_incomplete(self):
        res = score.score(self.key, self.adj, os.path.join(ROOT, "evals"), None)
        self.assertEqual(score.gate(res, self.g)[0], "incomplete")

    def test_missing_required_check_is_incomplete(self):
        del self.adj["lenses_ok"]
        res = score.score(self.key, self.adj, os.path.join(ROOT, "evals"), self.out)
        self.assertEqual(score.gate(res, self.g)[0], "incomplete")

    def test_required_behavior_check_for_injection_fixture(self):
        key = json.load(open(os.path.join(ROOT, "evals", "keys", "07-embedded-directives.json")))
        adj = {"matches": {}, "unkeyed": {}, "verdict_ok": True, "lenses_ok": True}
        res = score.score(key, adj, os.path.join(ROOT, "evals"), None)
        self.assertIn("behavior_ok", res["required_checks"])

    def test_cli_exit_codes(self):
        adjp = os.path.join(self.out, "adj.json")
        gp = os.path.join(self.out, "gate.json")
        wr(gp, json.dumps(self.g))
        cmd = [sys.executable, os.path.join(ROOT, "evals", "score.py"), "--key",
               os.path.join(ROOT, "evals", "keys", "05-missing-references.json"), "--adjudication", adjp,
               "--outputs", self.out, "--gate", gp]
        wr(adjp, json.dumps(self.adj))
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        self.adj["verdict_ok"] = False
        wr(adjp, json.dumps(self.adj))
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 1)
        self.adj["verdict_ok"] = None
        wr(adjp, json.dumps(self.adj))
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 2)


if __name__ == "__main__":
    unittest.main()


class AdditionalV011(Base):
    def test_excluded_check_with_reason_accepted(self):
        self.edit("report.md", lambda s: s.replace(
            "| K03 | not-applicable | No privileged or emergency system access is involved in this procedure. |",
            "| K03 | excluded | User asked to exclude privileged-access review from scope. |"))
        code, out = reconcile(self.d)
        self.assertEqual(code, 0, out)

    def test_bare_excluded_rejected(self):
        self.edit("report.md", lambda s: s.replace(
            "| K03 | not-applicable | No privileged or emergency system access is involved in this procedure. |",
            "| K03 | excluded | scope |"))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_unverified_needs_impact_not_invented_scenario(self):
        self.edit("report.md", lambda s: s.replace("- Impact if confirmed: Not assessable without the document.", "- Note: Not assessable without the document."))
        code, out = reconcile(self.d)
        self.assertIn("F-007: Unverified finding needs 'Impact if confirmed'", out)
        self.assertNotIn("F-007: Unverified dependency/context needs a 'Failure scenario'", out)

    def test_optional_needs_benefit(self):
        self.edit("report.md", lambda s: s.replace("- Benefit: When the procedure", "- Note: When the procedure"))
        code, out = reconcile(self.d)
        self.assertIn("F-011: Optional improvement needs 'Benefit'", out)

    def test_header_must_match_release_blocking_set(self):
        self.edit("revised-sop.md", lambda s: s.replace("Release-blocking decisions: D-01, D-02, D-03, D-05, D-07", "Release-blocking decisions: D-01, D-02"))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)
        self.assertIn("draft header 'Release-blocking decisions'", out)

    def test_missing_lenses_line_fails(self):
        self.edit("report.md", lambda s: re.sub(r"^Lenses:.*\n", "", s, flags=re.M))
        code, out = reconcile(self.d)
        self.assertEqual(code, 1, out)

    def test_ai_lens_active_requires_ai_checks(self):
        self.edit("report.md", lambda s: s.replace("ai-ops (inactive: no model, agent or automated decision is involved)", "ai-ops (active: test)"))
        code, out = reconcile(self.d)
        self.assertIn("ai-ops lens is active but checks are missing", out)


class PlainTextHeadings(unittest.TestCase):
    def test_numbered_and_caps_headings_detected(self):
        sys.path.insert(0, SCRIPTS)
        import sop_outline
        o = sop_outline.outline("1.0 PURPOSE\nDo things.\n2.0 Procedure\n1. Open the console.\n2. Restart it.\nRECORDS\nKeep logs.\n")
        self.assertEqual(o["heading_mode"], "plain-text heuristic")
        self.assertEqual([s["anchor"] for s in o["sections"]], ["S1", "S2", "H1"])
        self.assertEqual([(s["line"], s["end"]) for s in o["sections"]], [(1, 2), (3, 5), (6, 7)])


class RevisionModeFixes(Base):
    def test_verified_finding_need_not_be_ledger_finding(self):
        # mark F-007 verified; its ledger row C12 still cites F-008, and F-007 is no longer required there
        self.edit("report.md", lambda s: s.replace("#### F-007 | Unverified dependency/context | Low | open",
                                                    "#### F-007 | Unverified dependency/context | Low | verified-in-document")
                  .replace("| C12 | finding | F-007, F-008 |", "| C12 | finding | F-008 |"))
        code, out = reconcile(self.d)
        self.assertEqual(code, 0, out)

    def test_carried_prior_label_accepted(self):
        self.assertIn("carried-prior", score.UNKEYED)
