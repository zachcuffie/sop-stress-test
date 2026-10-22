# Finding rules

## Evidence class (how sure the issue is real)

| Class | Use when | Required extra field |
|---|---|---|
| **Confirmed defect** | The text itself shows the problem. Either the wrong instruction is there, or the gap persists after searching the whole document and supplied references. A realistic execution failure follows. | none |
| **Conditional concern** | It is a defect only if a stated condition holds, and the condition is plausible but not shown (for example "if the system does not itself enforce approval"). | `Condition:` |
| **Unverified dependency/context** | Assessment depends on something the reviewer cannot see. | `Subtype:` |
| **Optional improvement** | Execution would not fail, but clarity, efficiency or maintainability would improve. | none |

**Subtypes of Unverified dependency/context**
- `reviewer-unavailable`: the SOP names a reference precisely enough for an operator to find it, but it was not supplied to the review. This says nothing about whether the organization has the control.
- `context-unknown`: a fact about the organization or system that the SOP need not state, but on which correctness depends (for example tool configuration).

**When a reference is a confirmed defect.** A reference the *operator* cannot identify or retrieve is a **Confirmed defect** (usability), not an unverified item. Examples: "the usual checklist", "per policy" with no policy named, "as long as required". Record the operator-facing gap. Do not claim that the underlying control is missing.

**Class versus severity.** Class and severity are independent. An unknown with serious potential consequences stays *Unverified* or *Conditional*. Give it the severity it would have if real, but never present it as a confirmed High or Critical.

## Severity (consequence if the issue is real)

| Severity | Meaning |
|---|---|
| **Critical** | Following the SOP as written could plausibly cause severe, hard-to-reverse harm, with no compensating step in the document. Examples: an irrecoverable or fraudulent payment, unauthorized privileged access that persists, an autonomous action that cannot be undone, loss of essential data or evidence, unsafe outcomes for people. |
| **High** | Likely to cause significant error, loss, security exposure or failed execution under realistic conditions; recoverable but costly. |
| **Medium** | Causes confusion, delay, inconsistent execution or weak evidence; a workaround exists. |
| **Low** | Clarity, consistency or maintainability with minor consequence. |

Do not assert legal or regulatory consequences as fact. Write "possible regulatory exposure; applicability to be confirmed by the owner".

## Fix type

| Fix type | Use when |
|---|---|
| `doc edit` | The fix is wording, structure, ordering or a cross-reference, and its meaning is already settled by the document or obviously required. |
| `owner decision` | The fix needs a choice: a role, a threshold, a time limit, a tool, a retention period, or risk acceptance. |
| `doc edit + owner decision` | Both are needed. |
| `none` | No change is needed in this document (for example, an Unverified item that only needs the reference supplied). |

## Required content per finding
Every finding needs a title, a check, locations, evidence, a challenge (where coverage was searched), a fix type, a proposed fix (or "None required" with the reason), and operational verification.

The consequence field depends on the class. None of these asks for an invented scenario:
- **Confirmed and Conditional:** `Failure scenario`, a concrete execution failure.
- **Unverified:** `Impact if confirmed`. This may say "not assessable" with the reason.
- **Optional improvement:** `Benefit`.

## Status

| Status | Meaning |
|---|---|
| `open` | Not yet addressed in any draft. |
| `awaiting-owner-decision` | The draft carries a marker; resolution depends on decision D-xx. A `Decision:` field is required. |
| `addressed-in-draft` | The revised draft proposes text that resolves it without any pending decision. |
| `verified-in-document` | A later version supplied by the owner contains a fix the reviewer checked. This is revision mode only. |
| `regressed` | Was `verified-in-document`, and a later version undid the fix. The finding keeps its ID. |
| `withdrawn` | Retracted after challenge or new evidence. A `Rationale:` field is required. |

**Operational verification** is a separate field. It defaults to `unknown`, and can change only when the user supplies evidence of how the process actually runs (state what that evidence was). A reviewed document is never operational verification.

## Challenge pass (every candidate, before it is reported)

1. **Coverage search.** Look through the whole document: synonyms, other sections, definitions, tables, appendices and footnotes. Then search the supplied references. Record where you looked in `Challenge:`.
2. **Scope fit.** Would a reasonable SOP for this purpose cover the issue, or is it another document's job? If another document covers it and the SOP points there, it is not a defect in this SOP.
3. **Observable or contextual.** Is the issue visible in the text? If it depends on unknown context, classify it as Conditional or Unverified.
4. **Realistic failure.** Name a concrete execution failure (who, when, what goes wrong). If none exists, downgrade to Optional or reject.
5. **Duplicates.** Merge findings with the same root cause into one, listing **all** locations and keeping the most specific evidence. Different root causes at the same location stay separate.
6. **Proportionality.** Do not demand enterprise apparatus that the organization's size and the consequence do not justify.

Rejected candidates are not reported. In Deep mode, add a short count of how many were rejected and the most common reason.

## Ordering
Order findings by severity (Critical, High, Medium, Low), then class (Confirmed, Conditional, Unverified, Optional), then first location. Ordering never removes findings.

## Readiness verdict (the original document, within reviewed scope)

Pick exactly one:

1. **Insufficient evidence to assess.** The text is unreadable, too incomplete, or key sections are missing or blocked, so no supportable verdict exists.
2. **Not ready.** Any of the following applies:
   - a Confirmed Critical or High finding is not withdrawn;
   - a release-critical decision is open;
   - a Conditional or Unverified Critical/High finding remains unresolved and would block safe execution if confirmed. In this case, say that it is what blocks the verdict.
3. **Ready after non-blocking edits.** No blocking items remain; Medium, Low or Optional items remain.
4. **No blocking defects identified within reviewed scope.** Only Low or Optional items remain, or none at all.

Count the findings as they stand in the **original** document. An `addressed-in-draft` finding still counts against the original.

Then state the **Revised draft status** separately. A draft with open release-critical decisions is "**Not releasable** until D-xx, ... are decided". Otherwise it is "Ready for owner review; owner approval required before use". No verdict is operational assurance.

A decision is **release-critical** if leaving it unmade would leave a Critical or High finding unresolved, or would leave a step that cannot be carried out.

Every other open decision is **non-blocking**, and must state `Interim text if undecided:`. This is usually the original wording, which leaves the related finding open but makes nothing worse than the original.

Before release, the owner either decides each non-blocking decision or replaces its marker with the interim text. The draft header lists both sets, so it is clear exactly which markers prevent release.
