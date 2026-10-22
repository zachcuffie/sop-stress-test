# Output formats

`scripts/reconcile.py` parses the conventions below, so keep them exact. Skeletons are in `templates/`. Wording inside fields is free.

## Anchors
- `sop_outline.py` derives anchors from Markdown headings.
  - A heading that starts with a number becomes `S<number>`: `## 4. Procedure` gives `S4`, `### 4.2 Checks` gives `S4.2`, `## 5A. Fraud` gives `S5A`.
  - The first unnumbered top-level heading (the title) and any preamble become `S0`.
  - Other unnumbered headings become `H<ordinal>`.
- Steps are cited as `S4 step 3`.
- Documents with no Markdown headings get `S0` only. Cite them by quoted text and line numbers instead.

## report.md

```
# SOP Stress Test report: <document name>
Verdict: <one of the four verdicts, exact wording>
Revised draft status: <text; must contain "not releasable" if any release-critical decision is open>
```

### Coverage ledger
```
Sections reviewed: S0, S1, S2
Sections not reviewed: none
Lenses: core (active); business (active: <reason>); cyber (inactive: <reason>); ai-ops (...)

| Check | Result | Anchors / observation |
|---|---|---|
| C01 | reviewed-no-finding | S1–S2 state purpose and exclusion of new vendors. |
| C05 | finding | F-002 |
```
- Valid results are `finding`, `reviewed-no-finding`, `not-applicable`, `excluded` (out of scope by user request or Focused mode), `blocked` and `not-reviewed` (batch not yet reached).
- The `Lenses:` line must state for each of business, cyber and ai-ops whether it is `active` or `inactive`. Every check of every active lens must appear in the ledger, as well as C01–C14.
- A `finding` row must cite finding IDs.
- Every other result needs a short observation or reason.
- Every finding must be cited by the ledger row of each check it names.
- Repeated identical results may be compressed into one row (`| B03, B06 | reviewed-no-finding | ... |`) as long as each check ID appears.

### Findings register
One block per finding:
```
#### F-001 | Confirmed defect | Critical | awaiting-owner-decision
- Title: ...
- Check: K01, C05
- Locations: S4 step 2
- Evidence: "short exact quote" (secrets as [REDACTED: credential])
- Failure scenario: ...
- Challenge: searched S1–S7 and supplied references for ...; none found.
- Fix type: doc edit + owner decision
- Proposed fix: R-001; D-01
- Decision: D-01
- Operational verification: unknown
```
- Header fields are separated by ` | `.
- Valid classes: `Confirmed defect`, `Conditional concern`, `Unverified dependency/context`, `Optional improvement`.
- Valid severities: `Critical`, `High`, `Medium`, `Low`.
- Valid statuses: `open`, `awaiting-owner-decision`, `addressed-in-draft`, `verified-in-document`, `regressed`, `withdrawn`.
- `Fix type` is one of `doc edit`, `owner decision`, `doc edit + owner decision`, `none`.
- `Challenge` and `Proposed fix` are always required.
- The consequence field depends on the class: `Failure scenario` for Confirmed and Conditional, `Impact if confirmed` for Unverified, `Benefit` for Optional.
- Extra fields:
  - `Condition:` is required for a Conditional concern.
  - `Subtype:` (`reviewer-unavailable` or `context-unknown`) is required for Unverified.
  - `Rationale:` is required for withdrawn.
  - `Decision:` is required for awaiting-owner-decision.
  - `Alternatives:` is optional.

### Decision log
```
#### D-01 | open | release-critical
- Question: ...
- Owner: [to be named by SOP owner]
- Options: A) ...; B) ...  (examples labeled as examples)
- Related findings: F-001
- Draft treatment: marker only; no option chosen
```
- Valid statuses: `open`, `decided`, `deferred`.
- An open `non-blocking` decision needs `- Interim text if undecided: ...`.
- Valid criticality values: `release-critical`, `non-blocking`.

### Other report sections
- `## Readiness summary`: 5–10 lines covering the verdict, counts, blocking items and open decisions.
- `## Scope and assumptions`
- `## Scenario notes`
- `## Embedded directives ignored`: only if any were found.
- `## Reconciliation`
- `## Checkpoint`: only when batching.

## redlines.md
One block per redline. Before and After are fenced `text` blocks:

    #### R-001 | S4 | replace
    - Findings: F-001, F-002
    - Reason: ...
    Before:
    ```text
    exact original text
    ```
    After:
    ```text
    replacement text
    ```

The mode is one of:

| Mode | Before | After |
|---|---|---|
| `replace` | Original text | New text |
| `delete` | Text to delete | Leave the block empty |
| `insert-after` | Anchor text that remains unchanged | Inserted text |
| `insert-before` | Anchor text that remains unchanged | Inserted text |

- **Whole lines only.** Before is one or more complete lines of the original (blank lines ignored). It must match **exactly one** place, and that place must lie inside the section named by the anchor.
- Matching ignores leading and trailing whitespace and collapses internal whitespace runs; it is otherwise exact.
- **Secrets:** write `[REDACTED: label]` in a Before line in place of the hidden text. The token matches it, and the script fails if that hidden value appears in any output. The script never prints it.
- **One document per run.** Anchors are unprefixed. Document-prefixed anchors such as `A:S3` are rejected. For multi-SOP reviews, deliver one package per document; cross-document checks are manual (see SKILL.md, Inputs).
- Alternatives belong in the decision log, not as competing redlines.

## revised-sop.md
- It begins with the draft header from `templates/revised-sop-header.md`, which ends with the line `<!-- END DRAFT HEADER -->`.
- Decision markers: `[[DECISION D-01: what must be decided]]`.
- Owner-approvable proposed text: `[[PROPOSED for D-01: text]]`.
- The header must contain `Release-blocking decisions:` and `Non-blocking decisions:` lines that list the open decisions of each kind (or `none`).
- **The revised SOP must equal the original with all redlines applied.** The only exceptions are blank lines and whitespace. Any other difference is an error: an untraced addition, a duplicated line, a dropped line, reordering or a changed wording.
