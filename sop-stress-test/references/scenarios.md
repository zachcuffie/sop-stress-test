# Scenario simulation

Scenarios generate *candidate* findings. Every candidate still goes through the challenge pass.

## Personas (all modes)
- **New employee.** Reads literally and knows no unwritten context. Where do they stall, guess, or do the wrong thing? Watch for undefined terms, missing locations of tools and documents, and unclear "who".
- **Process owner.** Answers for outcomes. Can they tell that the process ran correctly? Can they prove it later? Who maintains the document, and what happens when roles change?
- **Operator under pressure.** End of day, urgent request, approver unavailable, system slow. Which steps get skipped? Does any exception clause make skipping legitimate? Does the SOP still protect the key control?

## Failure combinations (Standard: chosen by consequence; Deep: all that are relevant)
Combine two conditions when each is plausible and the combination is not handled:
- approver or owner absent + deadline;
- system or channel down + manual workaround that drops a control;
- duplicate or repeated trigger + a non-idempotent action;
- interruption part-way + no record of what was completed;
- wrong upstream input + no validation;
- impersonation or spoofing + urgency or authority pressure;
- AI output wrong or manipulated + reviewer rubber-stamping;
- staff change + undocumented access, credentials or knowledge;
- after-hours or a holiday + an escalation path that only works in business hours.

## Cross-SOP (when several SOPs are supplied, or one depends heavily on another)
Follow every handoff into the other document. Check that roles, timings, inputs and outputs line up, and that no item falls between the two documents.

If the other SOP was not supplied, record the dependency as Unverified (`reviewer-unavailable`) and continue.

## Second-order (Deep; also during reconciliation in every mode)
Re-run the relevant persona over the *revised* text. Did a fix create a new dependency on an undecided value, a new handoff without an owner, a new contradiction, or an unusable step?

## Recording
In the report's Scenario notes, list each scenario you ran and the finding IDs it produced (or "no new finding"). Keep this to one line per scenario.
