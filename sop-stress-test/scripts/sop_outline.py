#!/usr/bin/env python3
"""Structural outline of a Markdown/plain-text SOP.

What it does (deterministic, structure only):
  - derives section anchors from Markdown headings
  - lists numbered and bulleted steps per section with line numbers
  - lists explicit references (section/step mentions, document-ID-like tokens,
    links) and flags section references that do not resolve to an anchor

What it does NOT do: understand meaning, infer handoffs, judge coverage.
The reviewing model builds the semantic map; this output only assists it.

Usage: python sop_outline.py FILE [--json]
Python 3.8+, standard library only.
"""
import json
import re
import sys

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NUMBERED_TITLE = re.compile(r"^(\d+[A-Z]?(?:\.\d+)*)[.)]?\s+\S")
STEP = re.compile(r"^\s*(?:(\d+)[.)]|[-*+])\s+(.*)$")
SECTION_REF = re.compile(r"(?:\b[Ss]ections?|§)\s*(\d+[A-Z]?(?:\.\d+)*)")
STEP_REF = re.compile(r"\b[Ss]tep\s+(\d+)")
DOC_ID = re.compile(r"\b[A-Z]{2,}-\d+[A-Z0-9-]*\b")
LINK = re.compile(r"https?://\S+|\[[^\]]+\]\([^)]+\)")
PLAIN_HEADING = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+([A-Z][A-Za-z0-9 /&,()'-]{1,60})$")
CAPS_HEADING = re.compile(r"^[A-Z][A-Z0-9 /&,()'-]{2,60}$")
NAMED_DOC = re.compile(r"\b((?:[A-Z][\w&-]*\s+){1,6}(?:SOP|Policy|Procedure|Standard|Runbook|Playbook|Checklist|Plan|Guide))\b")


def _plain_headings(lines):
    """Fallback for documents with no Markdown headings (e.g. text extracted from DOCX/PDF):
    a short numbered line with no terminal period ("1.0 Purpose", "4 PROCEDURE"), or a short
    ALL-CAPS line. Heuristic; disclosed in output."""
    out = []
    for raw in lines:
        t = raw.strip()
        m = PLAIN_HEADING.match(t)
        if m and not t.endswith("."):
            num = m.group(1)
            if num.endswith(".0"):
                num = num[:-2]
            out.append("## %s. %s" % (num, m.group(2)))
        elif CAPS_HEADING.match(t) and any(c.isalpha() for c in t) and len(t.split()) <= 8:
            out.append("## " + t.title())
        else:
            out.append(raw)
    return out


def outline(text):
    lines = text.splitlines()
    heuristic = False
    if not any(HEADING.match(l) for l in lines):
        converted = _plain_headings(lines)
        if converted != lines:
            lines, heuristic = converted, True
    sections = []
    current = {"anchor": "S0", "title": "(preamble)", "line": 1, "level": 0, "steps": []}
    sections.append(current)
    seen_title = False
    unnumbered = 0
    refs = []
    in_fence = False
    for i, raw in enumerate(lines, start=1):
        if raw.strip().startswith("```") or raw.strip().startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING.match(raw)
        if m:
            level, title = len(m.group(1)), m.group(2)
            num = NUMBERED_TITLE.match(title)
            if num:
                anchor = "S" + num.group(1)
            elif level == 1 and not seen_title:
                seen_title = True
                current["title"] = title
                current["line"] = i
                continue
            else:
                unnumbered += 1
                anchor = "H%d" % unnumbered
            current = {"anchor": anchor, "title": title, "line": i, "level": level, "steps": []}
            sections.append(current)
            continue
        s = STEP.match(raw)
        if s:
            current["steps"].append({"line": i, "number": s.group(1), "text": s.group(2)[:120]})
        for rx, kind in ((SECTION_REF, "section"), (STEP_REF, "step"), (DOC_ID, "doc-id"), (LINK, "link"), (NAMED_DOC, "named-doc")):
            for r in rx.finditer(raw):
                refs.append({"line": i, "kind": kind, "text": r.group(0), "target": r.group(1) if r.groups() else None,
                             "in_section": current["anchor"]})
    if sections[0]["title"] == "(preamble)" and len(sections) > 1 and sections[1]["line"] == 1:
        sections.pop(0)  # empty preamble: document starts with a heading
    for k, sec in enumerate(sections):
        sec["end"] = sections[k + 1]["line"] - 1 if k + 1 < len(sections) else len(lines)
    anchors = {s["anchor"] for s in sections}
    for r in refs:
        if r["kind"] == "section":
            tgt = "S" + r["target"]
            # a reference to S4 resolves if S4 or any S4.x exists
            r["resolves"] = tgt in anchors or any(a.startswith(tgt + ".") for a in anchors)
    dup = sorted({a for a in anchors if [s["anchor"] for s in sections].count(a) > 1})
    return {"total_lines": len(lines), "sections": sections, "references": refs,
            "heading_mode": "plain-text heuristic" if heuristic else "markdown",
            "duplicate_anchors": dup,
            "unresolved_section_refs": [r for r in refs if r["kind"] == "section" and not r["resolves"]]}


def top_level_anchors(text):
    """All section anchors (used by reconcile.py for coverage checks)."""
    return [s["anchor"] for s in outline(text)["sections"]]


def render(o):
    out = ["Total lines: %d   Heading detection: %s" % (o["total_lines"], o["heading_mode"]), ""]
    for s in o["sections"]:
        out.append("%s  (lines %d-%d)  %s" % (s["anchor"], s["line"], s["end"], s["title"]))
        for st in s["steps"]:
            out.append("    L%-4d %s %s" % (st["line"], (st["number"] or "-") + ".", st["text"]))
    out.append("")
    out.append("Explicit references:")
    for r in o["references"]:
        flag = ""
        if r["kind"] == "section":
            flag = "" if r["resolves"] else "   <-- does not resolve"
        out.append("    L%-4d [%s] %s (in %s)%s" % (r["line"], r["kind"], r["text"], r["in_section"], flag))
    if o["duplicate_anchors"]:
        out.append("Duplicate anchors: " + ", ".join(o["duplicate_anchors"]))
    out.append("")
    out.append("Note: structure only. Handoffs, dependencies and coverage are judged by the reviewer, not this script.")
    return "\n".join(out)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        o = outline(f.read())
    print(json.dumps(o, indent=2) if "--json" in argv else render(o))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
