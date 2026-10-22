#!/usr/bin/env python3
"""Deterministic reconciliation of one SOP Stress Test audit (one original document per run).

What it does:
  * validates finding, decision, ledger and redline structure and cross-references
  * applies the redlines to the original and compares the result with the delivered revised SOP
    (detects untraced additions, duplications, deletions, reorderings and changed instructions)
  * checks that each redline's Before text lies inside the section its anchor names
  * supports secret-safe Before text: "[REDACTED: label]" stands for text in the original that must
    not be reproduced; the script fails if any such value appears in the report, redlines or revised SOP,
    and never prints it

Comparison exceptions (formatting only): blank lines are ignored, leading/trailing whitespace is
stripped and runs of internal whitespace are collapsed. Everything else must match.

Usage:
  python reconcile.py --original ORIG --report REPORT.md [--redlines R.md --revised REV.md] [--audit-only]
Exit: 0 = no errors, 1 = errors, 2 = usage problem. Python 3.8+, standard library only.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sop_outline import outline  # noqa: E402

CLASSES = {"Confirmed defect", "Conditional concern", "Unverified dependency/context", "Optional improvement"}
SEVERITIES = {"Critical", "High", "Medium", "Low"}
STATUSES = {"open", "awaiting-owner-decision", "addressed-in-draft", "verified-in-document", "regressed", "withdrawn"}
SUBTYPES = {"reviewer-unavailable", "context-unknown"}
FIX_TYPES = {"doc edit", "owner decision", "doc edit + owner decision", "none"}
LEDGER_RESULTS = {"finding", "reviewed-no-finding", "not-applicable", "excluded", "blocked", "not-reviewed"}
LENS_CHECKS = {
    "core": ["C%02d" % i for i in range(1, 15)],
    "business": ["B%02d" % i for i in range(1, 7)],
    "cyber": ["K%02d" % i for i in range(1, 8)],
    "ai-ops": ["A%02d" % i for i in range(1, 10)],
}
VERDICTS = ["Insufficient evidence to assess", "Not ready", "Ready after non-blocking edits",
            "No blocking defects identified within reviewed scope"]
REQUIRED_ALL = ["Title", "Check", "Locations", "Evidence", "Challenge", "Fix type", "Proposed fix",
                "Operational verification"]
SECRET_PATTERNS = [
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)\b(password|passwd|pwd|secret|api[_ -]?key|token)\s*[:=]\s*(?!\[REDACTED)\S{6,}"),
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}"),
    re.compile(r"[a-z][a-z0-9+.-]*://[^\s:/@]+:[^\s@]+@"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]
REDACTED = re.compile(r"\[REDACTED:[^\]]*\]")
F_HDR = re.compile(r"^#{2,4}\s+(F-\d{3,})\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*$")
D_HDR = re.compile(r"^#{2,4}\s+(D-\d{2,})\s*\|\s*(open|decided|deferred)\s*\|\s*(release-critical|non-blocking)\s*$")
R_HDR = re.compile(r"^#{2,4}\s+(R-\d{3,})\s*\|\s*(\S+)\s*\|\s*(replace|delete|insert-after|insert-before)\s*$")
FIELD = re.compile(r"^-\s+([A-Za-z][A-Za-z /-]*?):\s*(.*)$")
FID = re.compile(r"\bF-\d{3,}\b")
DID = re.compile(r"\bD-\d{2,}\b")
MARKER = re.compile(r"\[\[(DECISION|PROPOSED for)\s+(D-\d{2,})")
HEADER_END = "<!-- END DRAFT HEADER -->"
NOT_CHECKED = [
    "whether each finding is real, correctly classified, or correctly rated",
    "whether a fix actually resolves its finding or introduces a new semantic defect",
    "whether ledger observations are true (only that they exist and are specific enough to parse)",
    "handoffs and dependencies that are not explicit in the text",
    "whether decision options are complete or neutral",
    "secrets the reviewer did not mark with [REDACTED: ...] beyond a few common patterns",
    "cross-document consistency in multi-SOP reviews (one document per run; see output-format.md)",
    "anything about how the process operates in practice",
]


class Result:
    def __init__(self):
        self.errors, self.warnings, self.passes = [], [], []

    def err(self, m):
        self.errors.append(m)

    def warn(self, m):
        self.warnings.append(m)

    def ok(self, m):
        self.passes.append(m)


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def unfenced(lines):
    fence = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            fence = not fence
            continue
        if not fence:
            yield i, line


def blocks(lines, hdr_rx):
    out, cur, fence = [], None, False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            fence = not fence
        if not fence and re.match(r"^#{1,4}\s", line):
            if cur:
                out.append(cur)
                cur = None
            m = hdr_rx.match(line)
            if m:
                cur = (m, [], i)
            continue
        if cur:
            cur[1].append(line)
    if cur:
        out.append(cur)
    return out


def fields(body):
    d = {}
    for line in body:
        m = FIELD.match(line)
        if m:
            d[m.group(1).strip()] = m.group(2).strip()
    return d


def section(text, title):
    m = re.search(r"^##\s+%s\b.*?$(.*?)(?=^##\s|\Z)" % re.escape(title), text, re.M | re.S)
    return m.group(1) if m else None


# ---------------------------------------------------------------- findings and decisions
def parse_findings(report, r):
    lines = report.splitlines()
    findings = {}
    for m, body, ln in blocks(lines, F_HDR):
        fid, cls, sev, st = m.groups()
        if fid in findings:
            r.err("%s defined more than once (line %d)" % (fid, ln))
        f = fields(body)
        f.update({"_class": cls, "_sev": sev, "_status": st})
        findings[fid] = f
        if cls not in CLASSES:
            r.err("%s: invalid class '%s'" % (fid, cls))
        if sev not in SEVERITIES:
            r.err("%s: invalid severity '%s'" % (fid, sev))
        if st not in STATUSES:
            r.err("%s: invalid status '%s'" % (fid, st))
        for k in REQUIRED_ALL:
            if not f.get(k):
                r.err("%s: missing field '%s'" % (fid, k))
        if cls in ("Confirmed defect", "Conditional concern") and not f.get("Failure scenario"):
            r.err("%s: %s needs a 'Failure scenario'" % (fid, cls))
        if cls == "Unverified dependency/context" and not (f.get("Impact if confirmed") or f.get("Failure scenario")):
            r.err("%s: Unverified finding needs 'Impact if confirmed' (may say 'not assessable' with a reason)" % fid)
        if cls == "Optional improvement" and not (f.get("Benefit") or f.get("Failure scenario")):
            r.err("%s: Optional improvement needs 'Benefit'" % fid)
        if cls == "Unverified dependency/context" and f.get("Subtype") not in SUBTYPES:
            r.err("%s: Unverified finding needs Subtype reviewer-unavailable|context-unknown" % fid)
        if cls == "Conditional concern" and not f.get("Condition"):
            r.err("%s: Conditional concern needs a 'Condition'" % fid)
        if f.get("Fix type") and f["Fix type"] not in FIX_TYPES:
            r.err("%s: invalid Fix type '%s' (use: %s)" % (fid, f["Fix type"], "; ".join(sorted(FIX_TYPES))))
        if st == "withdrawn" and not f.get("Rationale"):
            r.err("%s: withdrawn finding needs a 'Rationale'" % fid)
        if st == "awaiting-owner-decision" and not DID.search(f.get("Decision", "")):
            r.err("%s: awaiting-owner-decision needs a 'Decision: D-xx' field" % fid)
        ov = f.get("Operational verification", "")
        if ov and not ov.lower().startswith("unknown") and "evidence" not in ov.lower():
            r.warn("%s: operational verification '%s' cites no supplied evidence" % (fid, ov))
    for i, line in unfenced(lines):
        if re.match(r"^#{2,4}\s+F-\d", line) and not F_HDR.match(line):
            r.err("report line %d: finding header not in 'F-### | class | severity | status' form" % i)
    return findings


def parse_decisions(report, r):
    lines = report.splitlines()
    decisions = {}
    for m, body, ln in blocks(lines, D_HDR):
        did, st, crit = m.groups()
        if did in decisions:
            r.err("%s defined more than once" % did)
        f = fields(body)
        f.update({"_status": st, "_crit": crit})
        decisions[did] = f
        for k in ("Question", "Owner", "Related findings"):
            if not f.get(k):
                r.err("%s: missing field '%s'" % (did, k))
        if st == "open" and crit == "non-blocking" and not f.get("Interim text if undecided"):
            r.err("%s: open non-blocking decision needs 'Interim text if undecided'" % did)
    for i, line in unfenced(lines):
        if re.match(r"^#{2,4}\s+D-\d", line) and not D_HDR.match(line):
            r.err("report line %d: decision header not in 'D-## | open|decided|deferred | release-critical|non-blocking' form" % i)
    return decisions


# ---------------------------------------------------------------- ledger
def active_lenses(led, r):
    m = re.search(r"^Lenses:\s*(.*)$", led, re.M)
    if not m:
        r.err("ledger needs a 'Lenses:' line")
        return ["core"]
    act = ["core"]
    for name in ("business", "cyber", "ai-ops"):
        lm = re.search(r"\b%s\s*\(\s*(active|inactive)" % re.escape(name), m.group(1))
        if not lm:
            r.err("Lenses line does not state whether '%s' is active or inactive" % name)
        elif lm.group(1) == "active":
            act.append(name)
    return act


def check_ledger(report, sections, findings, r):
    led = section(report, "Coverage ledger")
    if led is None:
        r.err("report has no '## Coverage ledger' section")
        return
    rows = re.findall(r"^\|\s*([A-Z]\d{2}(?:\s*,\s*[A-Z]\d{2})*)\s*\|\s*([a-z-]+)\s*\|\s*(.*?)\s*\|\s*$", led, re.M)
    ledger = {}
    for ids, res, obs in rows:
        for cid in re.split(r"\s*,\s*", ids):
            if cid in ledger:
                r.err("ledger lists %s twice" % cid)
            ledger[cid] = (res, obs)
        if res not in LEDGER_RESULTS:
            r.err("ledger %s: invalid result '%s'" % (ids, res))
        elif res == "finding":
            cited = FID.findall(obs)
            if not cited:
                r.err("ledger %s: 'finding' must cite F-IDs" % ids)
            for c in cited:
                if c not in findings:
                    r.err("ledger %s cites unknown %s" % (ids, c))
        elif len(obs.strip()) < 12:
            r.err("ledger %s: '%s' needs a compact observation or reason, not a bare checkbox" % (ids, res))
    lenses = active_lenses(led, r)
    for lens in lenses:
        missing = [c for c in LENS_CHECKS[lens] if c not in ledger]
        if missing:
            r.err("%s lens is active but checks are missing from ledger: %s" % (lens, ", ".join(missing)))
        else:
            r.ok("all %d %s checks present in ledger" % (len(LENS_CHECKS[lens]), lens))
    for fid, f in findings.items():
        if f["_status"] in ("withdrawn", "verified-in-document"):
            continue  # resolved items are recorded in the register, not as open ledger findings
        cited_somewhere = False
        for cid in re.findall(r"\b[A-Z]\d{2}\b", f.get("Check", "")):
            if cid not in ledger:
                r.err("%s names check %s, which is not in the ledger" % (fid, cid))
            elif ledger[cid][0] != "finding" or fid not in ledger[cid][1]:
                r.err("%s names check %s but that ledger row does not cite it as a finding" % (fid, cid))
            else:
                cited_somewhere = True
        if not cited_somewhere:
            r.err("%s is not cited by any ledger row" % fid)

    def anchors_on(label):
        m = re.search(r"^%s:\s*(.*)$" % label, led, re.M)
        if not m:
            return None
        return {a.strip() for a in m.group(1).split(",") if a.strip() and a.strip().lower() != "none"}
    rev, notrev = anchors_on("Sections reviewed"), anchors_on("Sections not reviewed")
    if rev is None or notrev is None:
        r.err("ledger needs 'Sections reviewed:' and 'Sections not reviewed:' lines")
        return
    doc = {s["anchor"] for s in sections}
    if rev & notrev:
        r.err("sections listed as both reviewed and not reviewed: " + ", ".join(sorted(rev & notrev)))
    if doc - rev - notrev:
        r.err("document sections in neither list: " + ", ".join(sorted(doc - rev - notrev)))
    if (rev | notrev) - doc:
        r.err("ledger lists anchors not found in original: " + ", ".join(sorted((rev | notrev) - doc)))
    if not (rev & notrev) and not (doc - rev - notrev) and not ((rev | notrev) - doc):
        r.ok("every original section anchor is accounted for (%d reviewed, %d not reviewed)" % (len(rev), len(notrev)))


# ---------------------------------------------------------------- verdict and draft status
def check_verdict(report, findings, decisions, r):
    m = re.search(r"^Verdict:\s*(.+?)\s*$", report, re.M)
    if not m or m.group(1) not in VERDICTS:
        r.err("report needs 'Verdict:' with one of: " + "; ".join(VERDICTS))
        return
    v = m.group(1)
    live = {k: f for k, f in findings.items() if f["_status"] not in ("withdrawn", "verified-in-document")}
    blocking_conf = [k for k, f in live.items() if f["_class"] == "Confirmed defect" and f["_sev"] in ("Critical", "High")]
    blocking_unk = [k for k, f in live.items() if f["_class"] in ("Conditional concern", "Unverified dependency/context")
                    and f["_sev"] in ("Critical", "High")]
    rc_open = [k for k, d in decisions.items() if d["_status"] == "open" and d["_crit"] == "release-critical"]
    medium = [k for k, f in live.items() if f["_sev"] == "Medium" and f["_class"] != "Optional improvement"]
    if v in VERDICTS[2:] and (blocking_conf or rc_open or blocking_unk):
        r.err("verdict '%s' inconsistent with blocking items %s" % (v, ", ".join(blocking_conf + blocking_unk + rc_open)))
    elif v == VERDICTS[3] and medium:
        r.err("verdict '%s' while Medium findings remain: %s" % (v, ", ".join(medium)))
    elif v == VERDICTS[1] and not (blocking_conf or rc_open or blocking_unk):
        r.warn("verdict 'Not ready' but no blocking finding or release-critical decision is recorded")
    else:
        r.ok("verdict '%s' consistent with findings and decisions" % v)
    ds = re.search(r"^Revised draft status:\s*(.+)$", report, re.M)
    if not ds:
        r.err("report needs a 'Revised draft status:' line")
    elif rc_open and "not releasable" not in ds.group(1).lower():
        r.err("open release-critical decisions %s but draft status does not say 'not releasable'" % ", ".join(rc_open))
    else:
        r.ok("revised draft status line consistent with open decisions")


def check_draft_header(revised, decisions, r):
    if HEADER_END not in revised:
        r.err("revised SOP lacks the '%s' line" % HEADER_END)
        return revised
    head, body = revised.split(HEADER_END, 1)
    if "Not approved for operational use" not in head:
        r.err("revised SOP lacks the draft header ('Not approved for operational use')")
    for label, crit in (("Release-blocking decisions", "release-critical"), ("Non-blocking decisions", "non-blocking")):
        m = re.search(r"%s:\s*(.*)$" % label, head, re.M)
        want = {d for d, x in decisions.items() if x["_status"] == "open" and x["_crit"] == crit}
        if not m:
            r.err("draft header needs a '%s:' line" % label)
            continue
        got = set(DID.findall(m.group(1)))
        if got != want:
            r.err("draft header '%s' lists %s; open %s decisions are %s" % (
                label, ", ".join(sorted(got)) or "none", crit, ", ".join(sorted(want)) or "none"))
        else:
            r.ok("draft header '%s' matches the decision log" % label)
    return body


# ---------------------------------------------------------------- redlines
def parse_redlines(text, r):
    lines = text.splitlines()
    reds = {}
    for m, body, ln in blocks(lines, R_HDR):
        rid, anchor, mode = m.groups()
        if rid in reds:
            r.err("%s defined more than once" % rid)
        f = fields(body)
        raw = "\n".join(body)
        got = dict(re.findall(r"^(Before|After):\s*\n```text\n(.*?)^```", raw, re.M | re.S))
        if "Before" not in got or "After" not in got:
            r.err("%s: needs fenced 'Before:' and 'After:' ```text blocks" % rid)
        reds[rid] = {"anchor": anchor, "mode": mode, "findings": FID.findall(f.get("Findings", "")),
                     "reason": f.get("Reason", ""), "before": got.get("Before", ""), "after": got.get("After", "")}
    for i, line in unfenced(lines):
        if re.match(r"^#{2,4}\s+R-\d", line) and not R_HDR.match(line):
            r.err("redlines line %d: header not in 'R-### | anchor | mode' form" % i)
    return reds


def line_pattern(before_line):
    """Regex for one normalized Before line; [REDACTED: x] matches one or more characters."""
    parts = REDACTED.split(norm(before_line))
    return re.compile("^" + "(.+?)".join(re.escape(p) for p in parts) + "$"), len(parts) - 1


def locate(orig_lines, before, r, rid):
    """Return (start, end, captured_secrets) of the unique whole-line match, or None."""
    blines = [norm(l) for l in before.splitlines() if norm(l)]
    if not blines:
        r.err("%s: Before is empty" % rid)
        return None
    pats = [line_pattern(b) for b in blines]
    nb = [(i, norm(l)) for i, l in enumerate(orig_lines) if norm(l)]
    hits = []
    for k in range(len(nb) - len(blines) + 1):
        caps, okay = [], True
        for j, (pat, _) in enumerate(pats):
            mm = pat.match(nb[k + j][1])
            if not mm:
                okay = False
                break
            caps.extend(mm.groups())
        if okay:
            hits.append((nb[k][0], nb[k + len(blines) - 1][0], caps))
    if len(hits) != 1:
        r.err("%s: Before text matches %d places in original (must be exactly 1, as whole lines)" % (rid, len(hits)))
        return None
    return hits[0]


def apply_redlines(original, sections, reds, findings, decisions, r):
    """Apply edits to the original; return (expected_lines, secret_values)."""
    orig_lines = original.splitlines()
    by_anchor = {s["anchor"]: s for s in sections}
    spans, secrets = [], []
    for rid, x in sorted(reds.items()):
        if not x["findings"]:
            r.err("%s cites no findings" % rid)
        for c in x["findings"]:
            if c not in findings:
                r.err("%s cites unknown %s" % (rid, c))
            elif findings[c]["_status"] == "withdrawn":
                r.err("%s cites withdrawn %s" % (rid, c))
        if not x["reason"]:
            r.err("%s has no Reason" % rid)
        for did in DID.findall(x["after"]):
            if did not in decisions:
                r.err("%s references %s, which is not in the decision log" % (rid, did))
        if ":" in x["anchor"]:
            r.err("%s: document-prefixed anchor '%s' is not supported; reconcile one document per run "
                  "(see output-format.md, multi-SOP reviews)" % (rid, x["anchor"]))
            continue
        if x["anchor"] not in by_anchor:
            r.err("%s: anchor %s does not exist in the original" % (rid, x["anchor"]))
            continue
        if x["mode"] == "delete" and norm(x["after"]):
            r.err("%s: delete redline must have an empty After" % rid)
        if x["mode"] != "delete" and not norm(x["after"]):
            r.err("%s: %s redline has an empty After" % (rid, x["mode"]))
        hit = locate(orig_lines, x["before"], r, rid)
        if not hit:
            continue
        s, e, caps = hit
        sec = by_anchor[x["anchor"]]
        if not (sec["line"] - 1 <= s and e <= sec["end"] - 1):
            r.err("%s: Before text (lines %d-%d) is not inside %s (lines %d-%d)" % (rid, s + 1, e + 1, x["anchor"], sec["line"], sec["end"]))
        secrets.extend(c for c in caps if len(c.strip()) >= 4)
        spans.append((s, e, x, rid))
    spans.sort(key=lambda t: t[0])
    for a, b in zip(spans, spans[1:]):
        if b[0] <= a[1]:
            r.err("%s and %s edit overlapping lines" % (a[3], b[3]))
            return None, secrets
    out = list(orig_lines)
    for s, e, x, rid in reversed(spans):
        after = x["after"].splitlines()
        if x["mode"] in ("replace", "delete"):
            out[s:e + 1] = after if x["mode"] == "replace" else []
        elif x["mode"] == "insert-after":
            out[e + 1:e + 1] = after
        else:
            out[s:s] = after
    return out, secrets


def mask(text, secrets):
    for v in secrets:
        text = text.replace(v, "[REDACTED]")
    for p in SECRET_PATTERNS:
        text = p.sub("[REDACTED]", text)
    return text


def compare(expected, body, r, secrets):
    exp = [norm(l) for l in expected if norm(l)]
    got = [norm(l) for l in body.splitlines() if norm(l)]
    if exp == got:
        r.ok("revised SOP equals the original with all redlines applied (formatting exceptions only)")
        return
    import difflib
    diff = [d for d in difflib.unified_diff(exp, got, "expected (original + redlines)", "delivered revised", n=0, lineterm="")
            if not d.startswith(("---", "+++", "@@"))]
    r.err("revised SOP differs from original + redlines in %d line(s); untraced changes are not allowed:" % len(diff))
    for d in diff[:12]:
        r.err("    %s %s" % ("added (untraced)  " if d.startswith("+") else "expected, missing ", mask(d[1:], secrets)[:100]))


def check_secrets(files, secrets, r):
    for name, text in files:
        if text is None:
            continue
        for v in secrets:
            if v in text:
                r.err("%s contains a value that the redlines mark as [REDACTED] in the original (value not printed)" % name)
                break
        if any(p.search(text) for p in SECRET_PATTERNS):
            r.warn("%s contains text matching a secret-like pattern; confirm nothing sensitive is echoed" % name)
    r.ok("secret check run (%d redacted value(s) tracked; values never printed)" % len(secrets))


def check_traceability(findings, decisions, reds, body, r):
    cited = {c for x in reds.values() for c in x["findings"]}
    for fid, f in findings.items():
        if f["_status"] == "addressed-in-draft" and fid not in cited:
            r.err("%s is addressed-in-draft but no redline cites it" % fid)
        for did in DID.findall(f.get("Decision", "")):
            if did not in decisions:
                r.err("%s points to %s, which is not in the decision log" % (fid, did))
    for d, x in decisions.items():
        for c in FID.findall(x.get("Related findings", "")):
            if c not in findings:
                r.err("%s relates to unknown %s" % (d, c))
    used = {d for _, d in MARKER.findall(body)}
    for d in sorted(used):
        if d not in decisions:
            r.err("revised SOP marker %s is not in the decision log" % d)
        elif decisions[d]["_status"] == "decided":
            r.err("%s is decided but its marker remains in the revised SOP" % d)
    for d, x in decisions.items():
        if x["_status"] == "open" and d not in used:
            r.warn("open decision %s has no marker in the revised SOP" % d)
    if re.search(r"\[\[(?!DECISION D-|PROPOSED for D-)", body):
        r.err("revised SOP has a [[...]] marker not in DECISION/PROPOSED form")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--original", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--redlines")
    ap.add_argument("--revised")
    ap.add_argument("--audit-only", action="store_true")
    ap.add_argument("--emit-applied", metavar="PATH",
                    help="write the original with all redlines applied (no draft header) to PATH; "
                         "use it to build revised-sop.md, then add the header. Comparison is then circular by design.")
    a = ap.parse_args()
    if a.emit_applied and not a.redlines:
        print("--emit-applied needs --redlines")
        return 2
    if not a.audit_only and not a.emit_applied and not (a.redlines and a.revised):
        print("--redlines and --revised are required unless --audit-only")
        return 2

    def rd(p):
        if not p:
            return None
        with open(p, encoding="utf-8") as f:
            return f.read()
    original, report, redl, revised = rd(a.original), rd(a.report), rd(a.redlines), rd(a.revised)
    if a.emit_applied and a.revised:
        print("use --emit-applied without --revised")
        return 2
    r = Result()
    o = outline(original)
    if o["heading_mode"] != "markdown":
        r.warn("original has no Markdown headings; section anchors come from the plain-text heuristic")
    findings = parse_findings(report, r)
    decisions = parse_decisions(report, r)
    r.ok("%d findings and %d decisions parsed" % (len(findings), len(decisions)))
    check_ledger(report, o["sections"], findings, r)
    check_verdict(report, findings, decisions, r)
    secrets = []
    if redl is not None:
        reds = parse_redlines(redl, r)
        expected, secrets = apply_redlines(original, o["sections"], reds, findings, decisions, r)
        if a.emit_applied and expected is not None:
            with open(a.emit_applied, "w", encoding="utf-8") as f:
                f.write("\n".join(expected) + "\n")
            r.ok("wrote original + redlines to %s" % a.emit_applied)
        if revised is not None:
            body = check_draft_header(revised, decisions, r)
            if expected is not None:
                compare(expected, body, r, secrets)
            check_traceability(findings, decisions, reds, body, r)
    check_secrets([("report", report), ("redlines", redl), ("revised SOP", revised)], secrets, r)
    for m in r.passes:
        print("PASS  " + m)
    for m in r.warnings:
        print("WARN  " + m)
    for m in r.errors:
        print("ERROR " + m)
    print("\nSummary: %d error(s), %d warning(s)." % (len(r.errors), len(r.warnings)))
    print("Not checked by this script (requires reviewer judgment):")
    for n in NOT_CHECKED:
        print("  - " + n)
    return 1 if r.errors else 0


if __name__ == "__main__":
    sys.exit(main())
