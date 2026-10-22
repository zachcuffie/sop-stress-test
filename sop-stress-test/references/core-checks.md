# Core checks (always applied)

Each check is applied to the whole document and, where relevant, to each section. Record one ledger result per check: one observation for a pass, finding IDs for a finding.

The "Avoid" lines name common false positives.

**C01 Purpose, scope and applicability.** Can a reader tell when this SOP applies, when it does not, and what it is for?
*Avoid:* demanding scope text for an obviously single-purpose checklist.

**C02 Triggers and prerequisites.** What starts the procedure? What must be true or available first (access, inputs, approvals, tools)? Are both stated where a new person would need them?

**C03 Inputs and outputs.** Are the required inputs named and obtainable, and is each output (record, change, deliverable) defined along with its recipient?

**C04 Ownership and authority.**
- Does every step have an actor (a role, not "someone")?
- Does the SOP have an owner?
- Is there a backup for any role whose absence would stall the process?
- Does the actor have the authority the step assumes?

*Avoid:* requiring named individuals; a role is enough.

**C05 Step clarity and sequencing.**
- Are steps actionable and unambiguous ("check", "ensure" and "as appropriate" with no criteria)?
- Are they in an order that works, with no step depending on a later step's output?
- Are terms defined?
- Do controls happen *before* the irreversible action they guard?

**C06 Decision branches.**
- Does every decision have explicit conditions, complete and mutually exclusive outcomes, and a default?
- Does every branch end in an outcome or rejoin the flow?

**C07 Handoffs.** For each transfer between people, teams or systems, check all of the following:
- what is handed over;
- by what means;
- how receipt is confirmed;
- what happens if it is not received or acted on.

**C08 Timing.**
- Deadlines, durations, frequencies, cut-offs and time zones where they matter.
- Waits that have no limit ("when they get a chance").
- Timers that should trigger escalation.

*Avoid:* inventing durations. Raise the missing limit and use a decision marker for its value.

**C09 Completion evidence and records.** How does the operator know the procedure is done? What is recorded, where, by whom, and for how long? Is the record sufficient to show what was checked?

**C10 Exceptions and escalation.**
- What happens when inputs are wrong, a check fails, an approver is absent, or the case is unusual?
- Who is escalated to?
- Are permitted exceptions bounded, and do they keep the key control?

**C11 Failure, rollback and recovery.**
- If a step fails part-way, or a wrong action is taken, how is it detected, stopped, reversed or recovered?
- What happens to work already in flight?

**C12 Dependencies and references.**
- Are referenced systems, documents, SOPs and contacts identifiable and retrievable *by the operator*?
- What if a dependency is unavailable?

The reviewer not having a reference is not, by itself, a defect (see finding-rules).

**C13 Internal consistency.**
- Contradictions between sections.
- Mismatched role names and terminology.
- Broken numbering or cross-references.
- Steps that conflict with stated roles or authority.

**C14 Maintenance.** Is there an owner of the document, a version or date, and a review trigger proportionate to criticality?
*Avoid:* demanding formal document control from a small team. An owner plus a date is often enough.

## Whole-document principles (check after section passes)
- Every role mentioned is defined, and every defined role is used.
- The happy path is executable start to finish by a new employee.
- Safeguards cannot be bypassed by a later exception clause.
- Terminology is stable, so the same thing has the same name throughout.
- Cross-SOP: shared roles, handoffs and timings agree with other supplied SOPs.
