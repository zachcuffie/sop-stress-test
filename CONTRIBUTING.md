# Contributing

Thanks for helping test SOP Stress Test. It is in beta. Real-world feedback is the thing it needs most.

## Ways to help
- **Run it on a procedure and report what it got wrong.** That means a real defect it missed, a finding that was not a real problem, or an output that was hard to use. Open an issue with the SOP (sanitized) and the outputs, or describe them if you cannot share them.
- **Run the blind evaluation protocol** in `evals/protocol.md`. The answer keys are not in this repository; open an issue to coordinate grading.
- **Contribute a sanitized SOP as a new fixture.** Never submit real company procedures, names, systems, credentials or customer data. Rewrite or invent details so nothing traces back to an organization.

## Changes
- Work on a branch and open a pull request. `main` is protected and changes are merged only after review.
- Run `python -m unittest discover -s tests` before opening a pull request. CI runs the same tests.
- Keep the skill lean. Changes to review rules, verdict rules or gate thresholds need a stated reason and a test.
- Do not add answer keys, key-aware run outputs or secrets to the repository.
