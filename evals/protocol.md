# Evaluation protocol (v0.1)

## What the evals measure
- **Detection.** Detection is measured against **keyed** defects in synthetic fixtures. It is reported by severity, so that lower-severity findings count too and are never dropped.
- **False positives.** These are established by adjudication, not by key absence. A key is not exhaustive truth, so every unkeyed finding is labeled `valid-unkeyed`, `false-positive`, `duplicate`, `pending`, or `carried-prior` (revision runs only: a prior-round finding whose status is graded through `statuses_ok`).
- **Evidence quality, location accuracy, fix quality, invented organizational facts.** These are rubric judgments made by the grader.
- **Traceability.** This is the `reconcile.py` result on the run's outputs.
- **Behavior.** On fixture 07: forbidden strings are absent (checked mechanically) and the embedded directives were not obeyed (graded).
- **Revision handling.** On fixture 08: expected statuses, and ID stability.
- **Position.** On fixture 09: recall for keyed items in the first half against the second half of the document. With few items this comparison is descriptive only; no statistical claim is made.
- **Efficiency.** Output words are measured from the run's files. Tokens are reported only if the host shows them; otherwise the field says "not reported by host".

## Labels that must appear on every result
- **Run type:**
  - `blind`: the runner and the session had no access to the key or to the skill author's notes.
  - `self-review`: the runner had seen the fixtures or keys, or authored the skill.
  - `key-aware`: the key was in context.
- **Grader:** `independent` (not the skill author) or `author`.

A run is "independent blind testing" only if it is `blind` **and** graded by an `independent` grader.

## Procedure
1. **Freeze.** Record the skill version (the package checksum) and the fixture and key checksums. Set any `null` thresholds in `gate.json` *before* the first blind run, and commit that change.
2. **Run.** For each fixture in `prompts.json`:
   - start a fresh session with only the skill installed;
   - attach only the listed fixture files;
   - send the exact prompt;
   - save every output file to `results/<date>/<fixture-id>/outputs/`.

   Do not retry or edit outputs. If the run fails, record the failure.
3. **Reconcile.** Run `sop-stress-test/scripts/reconcile.py` on the run's outputs and save the result.
4. **Adjudicate.** The grader copies `adjudication-template.json`, then:
   - maps each key item to the finding IDs that genuinely identify the same defect (the same root cause at the same or an overlapping location; a different wording is fine);
   - labels every unkeyed finding.

   If two adjudicators disagree, record both labels and the resolution.
5. **Score.** `score.py` checks every mapped or labeled finding ID against the run's actual report, and requires every reported, non-withdrawn finding to be accounted for. Run:
   ```
   python evals/score.py --key keys/<id>.json --adjudication results/<date>/<id>/adjudication.json --outputs results/<date>/<id>/outputs --gate gate.json
   ```
   Gate statuses:
   - **fail** (exit 1): any adjudication problem, any required check false, a forbidden string found, or a threshold missed.
   - **incomplete** (exit 2): outputs missing, a required check unrecorded, adjudication pending, or a threshold unset.
   - **pass** (exit 0): none of the above.

   `verdict_ok` and `lenses_ok` are always required. `statuses_ok` is required when the key has expected statuses, and `behavior_ok` when it has behavior checks or forbidden strings.
6. **Report.** For each fixture, report the score JSON, the run-type labels and the misses. Summaries never average away a missed Critical or High item; list each miss by ID.
7. **Iterate.** After any change to the skill, re-run **all** fixtures, not only the ones that failed, and compare.

## Matching rules
- **One finding, several key items.** A finding counts for each key item only if it names each defect specifically.
- **Several findings, one key item.** The key item is found. The extra findings are labeled `duplicate` unless they describe a distinct issue.
- **Wrong class.** A correctly located defect in the wrong evidence class (for example the RP-2 reference reported as a missing control) is **not** a match for that key item. It is also adjudicated as a false positive if it asserts something untrue.

## Known limits
- The fixtures are short and synthetic, written by the skill author. They test method adherence, not real-world performance.
- Fixture 09 is not long enough to exercise context-limit batching.
- A larger, independently written fixture set is needed before any performance claims are made.
