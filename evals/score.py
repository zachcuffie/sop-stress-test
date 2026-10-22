#!/usr/bin/env python3
"""Score one adjudicated evaluation run against its answer key.

Inputs:
  --key KEY.json            answer key (evals/keys/)
  --adjudication ADJ.json   grader's mapping for one run (see protocol.md)
  --outputs DIR             optional: the run's output files, scanned for
                            forbidden strings and measured for size
  --gate GATE.json          optional: release-gate thresholds

Exit codes with --gate: 0 = pass, 1 = fail, 2 = incomplete. Without --gate: 1 if the
adjudication has problems, else 0.

This script never decides whether a finding is valid. It only computes
metrics from the human or independent adjudication it is given.
Python 3.8+, standard library only.
"""
import argparse
import json
import os
import re
import sys

SEVS = ["Critical", "High", "Medium", "Low"]
UNKEYED = {"valid-unkeyed", "false-positive", "duplicate", "pending", "carried-prior"}


def read_text(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def frac(n, d):
    return None if d == 0 else round(n / d, 3)


F_HDR = re.compile(r"^#{2,4}\s+(F-\d{3,})\s*\|[^|]*\|[^|]*\|\s*([a-z-]+)\s*$", re.M)


def reported_findings(outputs):
    """Finding IDs and statuses declared in the run's output files."""
    found = {}
    for root, _, files in os.walk(outputs):
        for f in files:
            if not f.endswith(".md"):
                continue
            for fid, st in F_HDR.findall(read_text(os.path.join(root, f))):
                found[fid] = st
    return found


def score(key, adj, base_dir, outputs=None):
    fx_path = os.path.join(base_dir, key["fixture"])
    fx = read_text(fx_path)
    total = len(fx.splitlines())
    res = {"fixture": key["fixture"], "run": adj.get("run", {}), "problems": []}
    items = key.get("items", [])
    matches = adj.get("matches", {})
    found = {}
    for it in items:
        m = matches.get(it["id"])
        if m is None:
            res["problems"].append("key item %s has no adjudication entry" % it["id"])
            m = []
        found[it["id"]] = bool(m)
        idx = fx.find(it["locate"])
        it["_line"] = fx[:idx].count("\n") + 1 if idx >= 0 else None
    for kid in matches:
        if kid not in found:
            res["problems"].append("adjudication references unknown key item %s" % kid)
    reported = reported_findings(outputs) if outputs else None
    res["outputs_supplied"] = outputs is not None
    mapped = {f for ids in matches.values() for f in (ids or [])}
    un_ids = set(adj.get("unkeyed", {}))
    if reported is not None:
        res["reported_findings"] = sorted(reported)
        for f in sorted((mapped | un_ids) - set(reported)):
            res["problems"].append("adjudication refers to %s, which the run did not report" % f)
        live = {f for f, st in reported.items() if st != "withdrawn"}
        for f in sorted(live - mapped - un_ids):
            res["problems"].append("reported finding %s is not accounted for (map it or label it unkeyed)" % f)
    for f in sorted(mapped & un_ids):
        res["problems"].append("%s is both mapped to a key item and labeled unkeyed" % f)
    by = {}
    for s in SEVS:
        group = [i for i in items if i["severity"] == s]
        by[s] = {"keyed": len(group), "found": sum(found[i["id"]] for i in group),
                 "recall": frac(sum(found[i["id"]] for i in group), len(group))}
    res["recall_by_severity"] = by
    ch = [i for i in items if i["severity"] in ("Critical", "High")]
    ml = [i for i in items if i["severity"] in ("Medium", "Low")]
    res["recall_critical_high"] = frac(sum(found[i["id"]] for i in ch), len(ch))
    res["recall_medium_low"] = frac(sum(found[i["id"]] for i in ml), len(ml))
    res["recall_overall"] = frac(sum(found.values()), len(items))
    early = [i for i in items if i["_line"] is not None and i["_line"] <= total / 2]
    late = [i for i in items if i["_line"] is not None and i["_line"] > total / 2]
    res["position"] = {"definition": "early = key item located in first half of fixture lines (%d lines)" % total,
                       "early": {"keyed": len(early), "found": sum(found[i["id"]] for i in early)},
                       "late": {"keyed": len(late), "found": sum(found[i["id"]] for i in late)}}
    res["missed"] = [i["id"] for i in items if not found[i["id"]]]
    un = adj.get("unkeyed", {})
    bad = {k: v for k, v in un.items() if v not in UNKEYED}
    if bad:
        res["problems"].append("invalid unkeyed labels: %s" % bad)
    res["unkeyed"] = {lab: sorted(k for k, v in un.items() if v == lab) for lab in sorted(UNKEYED)}
    res["false_positives"] = len(res["unkeyed"]["false-positive"])
    res["pending_adjudication"] = len(res["unkeyed"]["pending"])
    req = ["verdict_ok", "lenses_ok"]
    if key.get("expected_statuses"):
        req.append("statuses_ok")
    if key.get("behavior_checks") or key.get("forbidden_output_strings"):
        req.append("behavior_ok")
    res["required_checks"] = req
    for k in ("verdict_ok", "lenses_ok", "statuses_ok", "behavior_ok"):
        if k in adj:
            res[k] = adj[k]
    if "rubric" in adj:
        res["rubric"] = adj["rubric"]
    if outputs:
        text, words = "", 0
        for root, _, files in os.walk(outputs):
            for f in files:
                try:
                    t = read_text(os.path.join(root, f))
                except (UnicodeDecodeError, OSError):
                    continue
                text += t
                words += len(t.split())
        leaks = [s for s in key.get("forbidden_output_strings", []) if s in text]
        res["forbidden_strings_found"] = leaks
        res["output_words_measured"] = words
    res["usage_tokens"] = adj.get("run", {}).get("usage_tokens", "not reported by host")
    return res


def gate(res, g):
    """Return (status, detail) with status in {'pass', 'fail', 'incomplete'}.
    fail: any problem in adjudication, any required/declared check False, forbidden strings, threshold miss.
    incomplete: missing evidence (no outputs, required check unset, pending adjudication, unset threshold)."""
    fail, incomplete, out = [], [], []
    for p in res.get("problems", []):
        fail.append("adjudication problem: " + p)
    required = res.get("required_checks", ["verdict_ok", "lenses_ok"])
    for k in ("verdict_ok", "lenses_ok", "statuses_ok", "behavior_ok"):
        v = res.get(k)
        if v is False:
            fail.append("%s is false" % k)
        elif k in required and v is not True:
            incomplete.append("%s not recorded" % k)
    if res.get("forbidden_strings_found"):
        fail.append("forbidden strings present in outputs")
    if res.get("outputs_supplied") is False:
        incomplete.append("run outputs not supplied (required evidence)")
    if res.get("pending_adjudication"):
        incomplete.append("%d finding(s) pending adjudication" % res["pending_adjudication"])
    for metric, thr in g.get("thresholds", {}).items():
        val = res.get(metric)
        if thr is None:
            incomplete.append("%s: threshold not set (maintainer decision)" % metric)
        elif val is None:
            out.append("%s: not applicable for this fixture" % metric)
        elif val < thr:
            fail.append("%s: %s < %s" % (metric, val, thr))
        else:
            out.append("%s: %s >= %s pass" % (metric, val, thr))
    for metric, thr in g.get("max", {}).items():
        val = res.get(metric)
        if thr is None:
            incomplete.append("%s: maximum not set (maintainer decision)" % metric)
        elif val is not None and val > thr:
            fail.append("%s: %s > %s" % (metric, val, thr))
        elif val is not None:
            out.append("%s: %s <= %s pass" % (metric, val, thr))
    status = "fail" if fail else ("incomplete" if incomplete else "pass")
    return status, ["FAIL " + x for x in fail] + ["INCOMPLETE " + x for x in incomplete] + out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--key", required=True)
    ap.add_argument("--adjudication", required=True)
    ap.add_argument("--outputs")
    ap.add_argument("--gate")
    a = ap.parse_args()
    key = load_json(a.key)
    adj = load_json(a.adjudication)
    base = os.path.dirname(os.path.dirname(os.path.abspath(a.key)))
    res = score(key, adj, base, a.outputs)
    if a.gate:
        status, lines = gate(res, load_json(a.gate))
        res["gate"] = {"result": status, "detail": lines}
        print(json.dumps(res, indent=2))
        return {"pass": 0, "fail": 1, "incomplete": 2}[status]
    print(json.dumps(res, indent=2))
    return 1 if res["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
