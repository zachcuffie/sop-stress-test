# Changelog

## 0.1.1 (2026-10-22)
**Validator (`reconcile.py`)**
- Rebuilt around applying redlines and comparing the result with the delivered revised SOP. Untraced additions, duplications, deletions, reordering and changed wording are now errors (previously some were warnings or passed). Formatting exceptions: blank lines and whitespace only.
- Redline anchors must exist, and Before text must lie inside the cited section. Document-prefixed anchors are rejected with guidance.
- Ledger: every check of each active lens is required. Added the `excluded` result; a reason is required. A finding must be cited by each check row it names.
- Findings: `Challenge` and `Proposed fix` are required. The consequence field is per class (`Failure scenario`, `Impact if confirmed` or `Benefit`); no invented scenario is required for unknowns or optional items. Added `Fix type: none`.
- Decisions: open non-blocking decisions need `Interim text if undecided`. The draft header must list release-blocking and non-blocking decisions matching the log.
- Secret-safe redlines: `[REDACTED: label]` in Before matches hidden text. The hidden value must not appear in any output and is never printed. Secret patterns extended.
- `--emit-applied` writes original plus redlines, to build the revised SOP without copy errors.
- Verified findings are no longer required as open ledger findings (found in revision run 08).

**Outline:** section line ranges; plain-text heading fallback; plural section references.

**Evaluation (`score.py`)**
- The gate returns pass, fail or incomplete. CLI exit codes are 0, 1 and 2.
- Fails on adjudication problems, false required checks or forbidden strings. Incomplete on missing outputs, unrecorded required checks, pending adjudication or unset thresholds.
- Mapping IDs are validated against the findings actually reported, and every reported finding must be accounted for.
- Added the `carried-prior` label.

**Example**
- B02 reassessed: added F-012 (stale or replayed request overwrites newer details) and F-013 (conditional duplicate payment from the urgent release).
- The Section 5A fraud route now covers an absent or involved Controller.
- Draft header and non-blocking decisions reconciled (interim text).
- F-007 fix type corrected to `none`.

**Docs:** multi-SOP reviews routed to per-document packages with manual cross-document checks; whole-line redline rule; reconciliation handling of draft-introduced defects.

**Tests:** 31 new regression and behavior tests (55 total), written before the fixes. The pre-fix run is in `evals/results/regression-before.txt`.

**Runs:** 7 author-run, key-aware model runs saved with outputs, reconciliation, adjudication and scores (kept outside the public repository, with the answer keys).
