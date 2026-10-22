# SOP Stress Test report: Changing a Vendor's Bank Details
Verdict: Not ready
Revised draft status: Not releasable until D-01, D-02, D-03, D-05 and D-07 are decided. D-04 and D-06 are non-blocking: before release, each is either decided or its marker is replaced with the interim text in the decision log.

## Readiness summary
The document is not ready. As written, a spoofed or compromised vendor mailbox could redirect payments: verification relies on the sender's domain (F-001), and the urgent path allows a change plus a payment before any approval (F-004).

**Findings:** 13 in total.
- By class: 9 Confirmed defect, 2 Conditional concern, 1 Unverified dependency/context, 1 Optional improvement.
- By severity: 2 Critical, 4 High, 5 Medium, 2 Low.

**Blocking items:**
- F-001: verification relies on email domain.
- F-004: urgent exception skips approval and releases payment.
- F-002: approval happens after the change.
- F-005: no path for failed verification or suspected fraud.
- F-009: if the system does not enforce approval, segregation rests on this document alone (conditional).
- F-013: an urgent release may duplicate a scheduled payment, if the system does not block duplicates (conditional).

**Open decisions:** 7.
- **Release-critical (5):** D-01, D-02, D-03, D-05, D-07. Each leaves a Critical or High finding unresolved, or a step that cannot be carried out, until it is decided.
- **Non-blocking (2):** D-04 (retention period) and D-06 (owner role). Each relates to a Medium or Low finding and has interim text: the original wording. Using that interim text leaves F-008 and F-011 open but makes nothing worse than the original.

This is a document review only. Whether the process runs this way in practice is unknown.

## Scope and assumptions
- Document: `original.md` (Markdown, 31 lines). This is an illustrative synthetic SOP; there was no extraction step.
- Mode: Standard.
- Assumptions:
  - Small finance team (the only roles named are an AP Clerk and a Controller).
  - Payments are released from the same accounting system.
  - Neither the New Vendor Setup SOP nor the accounting system configuration was supplied.

## Coverage ledger
Sections reviewed: S0, S1, S2, S3, S4, S5, S6, S7
Sections not reviewed: none
Lenses: core (active); business (active: vendor master data and payment release); cyber (active: bank-detail change requests are a known impersonation and fraud vector, and identity validation is central); ai-ops (inactive: no model, agent or automated decision is involved)

| Check | Result | Anchors / observation |
|---|---|---|
| C01 | reviewed-no-finding | S1–S2 state purpose and exclude new-vendor setup. |
| C02 | reviewed-no-finding | Trigger is a vendor change request (S4 step 1); no prerequisites beyond system access, which is implied by role. |
| C03 | reviewed-no-finding | Input is the request; output is the updated vendor record (S4). Records gap handled under C09. |
| C04 | finding | F-003, F-011 |
| C05 | finding | F-002, F-012 |
| C06 | finding | F-005 |
| C07 | finding | F-002 |
| C08 | finding | F-003 |
| C09 | finding | F-006, F-008 |
| C10 | finding | F-003, F-005 |
| C11 | finding | F-005, F-010 |
| C12 | finding | F-007, F-008 |
| C13 | finding | F-004 |
| C14 | finding | F-011 |
| B01 | finding | F-002, F-004, F-009 |
| B02 | finding | F-012, F-013 |
| B03 | reviewed-no-finding | No periodic review of master-data changes. For a small team handling per-request changes, this was judged optional and not raised separately. |
| B04 | finding | F-001, F-010 |
| B05 | finding | F-003 |
| B06 | reviewed-no-finding | A system outage delays a change without harm; nothing forces a workaround. |
| K01 | finding | F-001 |
| K02 | finding | F-009 |
| K03 | not-applicable | No privileged or emergency system access is involved in this procedure. |
| K04 | finding | F-005 |
| K05 | finding | F-005 |
| K06 | finding | F-005 |
| K07 | not-applicable | No credentials or secrets are handled; bank details are covered under K01 and B04. |

## Findings register

#### F-001 | Confirmed defect | Critical | awaiting-owner-decision
- Title: Requester identity "verified" by email domain only
- Check: K01, B04
- Locations: S4 step 2
- Evidence: "checking that the email comes from the vendor's domain"
- Failure scenario: An attacker who controls or spoofs the vendor's mailbox, or a look-alike domain, sends new bank details. The domain check passes, and the next payment goes to the attacker.
- Challenge: Searched S1–S7 for call-back, known-contact or second-channel verification; none found. No supplied reference covers it.
- Fix type: doc edit + owner decision
- Proposed fix: R-003 (independent verification through contact details not taken from the request); D-01 (authoritative contact source and who calls)
- Decision: D-01
- Operational verification: unknown

#### F-004 | Confirmed defect | Critical | awaiting-owner-decision
- Title: Urgent exception permits change and payment before approval
- Check: C13, B01
- Locations: S5; conflicts with S3 ("Controller: approves changes")
- Evidence: "may make the change and release the payment before the Controller approves"
- Failure scenario: The fraudulent request says "payment due today". Under pressure the operator uses the sanctioned exception, and the money is released before anyone else sees the request.
- Challenge: Checked whether S4 or S3 limits the exception; neither does.
- Fix type: doc edit + owner decision
- Proposed fix: R-005 removes the unverified, unapproved path. D-02 decides whether any bounded exception exists.
- Alternatives: see D-02 options
- Decision: D-02
- Operational verification: unknown

#### F-002 | Confirmed defect | High | addressed-in-draft
- Title: Approval occurs after the change it is meant to control
- Check: C05, C07, B01
- Locations: S4 steps 3–5
- Evidence: "Send the Controller an email letting them know the change was made."
- Failure scenario: The change takes effect immediately. If a payment run happens before the Controller looks, the control has no effect.
- Challenge: No other section requires approval before the update.
- Fix type: doc edit
- Proposed fix: R-003 (approval before update; the update in step 8 happens only after approval and the staleness check in step 7)
- Operational verification: unknown

#### F-005 | Confirmed defect | High | awaiting-owner-decision
- Title: No path for failed verification, suspected fraud, or misdirected payment
- Check: C06, C10, C11, K04, K05, K06
- Locations: S4 (whole); S5
- Evidence: S4 has no branch for a request that cannot be verified or seems suspicious.
- Failure scenario: The operator suspects the request but has no instruction. They might reply to the attacker's email, delete it, or simply carry on. If money has already gone, nobody knows who acts to recall it.
- Challenge: Searched for "fraud", "suspicious", "escalate" and "recall"; none found.
- Fix type: doc edit + owner decision
- Proposed fix: R-006 (Section 5A: stop, don't reply via the request, keep evidence, report to the Controller or the backup approver); D-07 (who attempts recall)
- Decision: D-07
- Operational verification: unknown

#### F-009 | Conditional concern | High | awaiting-owner-decision
- Title: Segregation may rest on the document alone
- Check: K02, B01
- Locations: S3; S4 step 3
- Evidence: The AP Clerk both updates the record (S3) and, under S5, can release payment.
- Condition: The accounting system does not itself require approval before a bank-detail change takes effect or before payment to changed details.
- Failure scenario: If that condition holds, one person can change details and pay without any system stop, and a skipped step goes unnoticed.
- Challenge: System configuration was not supplied; the SOP is silent on it. Not treated as confirmed.
- Fix type: owner decision
- Proposed fix: R-002 adds marker D-05
- Decision: D-05
- Operational verification: unknown

#### F-013 | Conditional concern | High | awaiting-owner-decision
- Title: Urgent payment release may duplicate a scheduled payment
- Check: B02
- Locations: S5
- Evidence: "may make the change and release the payment"
- Condition: The accounting system does not itself prevent paying the same invoice twice. This is unknown to the reviewer.
- Failure scenario: The AP Clerk releases an urgent payment for an invoice that is already in the next scheduled run, and the vendor is paid twice. If the details were fraudulent, both payments go to the attacker.
- Challenge: Searched S4–S6 for any check that the invoice is not already scheduled or paid; none found. System duplicate controls were not supplied, so this is not treated as confirmed.
- Fix type: owner decision
- Proposed fix: D-02. Both options now require that any expedited payment is checked against scheduled and paid items. R-004 step 9 checks scheduled payments after a change.
- Decision: D-02
- Operational verification: unknown

#### F-003 | Confirmed defect | Medium | awaiting-owner-decision
- Title: Open-ended Controller review with no backup
- Check: C04, C08, C10, B05
- Locations: S4 step 5; S3
- Evidence: "approves the change when they get a chance"
- Failure scenario: The Controller is on leave. Once approval correctly moves before the change, requests stall with no time limit and no alternate approver, which creates pressure to bypass.
- Challenge: No backup role or timing appears anywhere.
- Fix type: doc edit + owner decision
- Proposed fix: R-003 adds marker D-03 (turnaround and backup)
- Decision: D-03
- Operational verification: unknown

#### F-012 | Confirmed defect | Medium | addressed-in-draft
- Title: A stale or replayed request can overwrite newer approved details
- Check: B02, C05
- Locations: S4 steps 1–3
- Evidence: "Update the bank details in the vendor record in the accounting system."
- Failure scenario: An older request, such as a resent email or one found late in the inbox, is processed after a newer approved change. It overwrites the current details, and payments go to an outdated or closed account. Updating a record is not harmless when requests can arrive out of order.
- Challenge: No step compares the request with the record's current state or checks for other open requests.
- Fix type: doc edit
- Proposed fix: R-003 (step 7: before updating, confirm the record has not changed since the request and no other request is open; otherwise restart verification)
- Operational verification: unknown

#### F-006 | Confirmed defect | Medium | addressed-in-draft
- Title: No record of how the request was verified or approved
- Check: C09
- Locations: S4 step 6; S6
- Evidence: "File the request email in the vendor folder."
- Failure scenario: After a disputed or fraudulent change, nothing shows who verified it, how, or who approved it.
- Challenge: S6 covers keeping the request email only.
- Fix type: doc edit
- Proposed fix: R-003 (step 4 records the verification), R-004 (step 10 files the request, verification and approval), R-007 (the record includes verification and approval)
- Operational verification: unknown

#### F-008 | Confirmed defect | Medium | awaiting-owner-decision
- Title: Retention period undefined for the operator
- Check: C09, C12
- Locations: S6
- Evidence: "for as long as required"
- Failure scenario: The operator cannot tell when records may be deleted, and records are either purged too early or kept indefinitely. Whether an organization retention rule exists is unknown; the gap here is that the SOP neither states nor points to one.
- Challenge: No retention policy is named in the document.
- Fix type: owner decision
- Proposed fix: R-007 adds marker D-04
- Decision: D-04
- Operational verification: unknown

#### F-010 | Confirmed defect | Medium | addressed-in-draft
- Title: No confirmation to the vendor and no check of payments already scheduled
- Check: C11, B04
- Locations: S4 (after update)
- Evidence: The procedure ends at filing (S4 step 6); nothing touches scheduled payments or notifies the vendor.
- Failure scenario: A fraudulent change that slipped through is not caught by the real vendor, because the vendor is never told. Payments already queued go to whichever details were current when they were created.
- Challenge: Not covered in S4–S6.
- Fix type: doc edit
- Proposed fix: R-004 (step 9)
- Operational verification: unknown

#### F-007 | Unverified dependency/context | Low | open
- Title: Referenced New Vendor Setup SOP not supplied
- Check: C12
- Locations: S2
- Evidence: "see the New Vendor Setup SOP"
- Subtype: reviewer-unavailable
- Impact if confirmed: Not assessable without the document. The reference is named clearly enough for an operator to find it, so it is not a usability defect.
- Challenge: Not supplied to the review. This says nothing about whether it exists or is adequate.
- Fix type: none
- Proposed fix: None required in this SOP. Supply the referenced SOP if cross-SOP consistency should be checked.
- Operational verification: unknown

#### F-011 | Optional improvement | Low | awaiting-owner-decision
- Title: Owner and contact point named as a department
- Check: C04, C14
- Locations: S0; S7
- Evidence: "Owner: Finance"; "Contact Finance with any questions."
- Benefit: When the procedure needs updating, one role is clearly accountable.
- Challenge: A department may be acceptable in very small teams, hence Optional.
- Fix type: owner decision
- Proposed fix: R-001 (marker D-06), R-008
- Decision: D-06
- Operational verification: unknown

## Decision log

#### D-01 | open | release-critical
- Question: What is the authoritative source of vendor contact details for verification calls, and which role may make the call?
- Owner: [to be named by SOP owner]
- Options: A) the contact on file from vendor onboarding; B) the contact in the signed contract. These are examples of common sources; either must be independent of the change request.
- Related findings: F-001
- Draft treatment: marker only; no option chosen

#### D-02 | open | release-critical
- Question: Do urgent requests get any exception to Section 4?
- Owner: [to be named by SOP owner]
- Options: A) no exception, so an urgent request waits for verification and approval and any late fee is accepted; B) an expedited path in which verification still happens, an alternate approver (named in D-03) approves before any change or payment, and the payment is checked against scheduled and already-paid items before release.
- Related findings: F-004, F-013
- Draft treatment: marker only; the original unapproved path is removed because both options remove it

#### D-03 | open | release-critical
- Question: What is the Controller's review turnaround, and who approves when the Controller is unavailable?
- Owner: [to be named by SOP owner]
- Options: no values proposed; this depends on team size and payment schedule.
- Related findings: F-003
- Draft treatment: marker only

#### D-04 | open | non-blocking
- Question: How long are vendor change records kept, or which retention rule applies?
- Owner: [to be named by SOP owner]
- Options: state a period, or point to the organization's retention rule by name.
- Related findings: F-008
- Draft treatment: marker only
- Interim text if undecided: the original wording "for as long as required". F-008 stays open.

#### D-05 | open | release-critical
- Question: Does the accounting system require approval before a bank-detail change takes effect? If not, what compensating control applies?
- Owner: [to be named by SOP owner]
- Options: A) confirm the system enforces it and cite the setting; B) if not, add a periodic independent review of changed vendor details. B is an example of a compensating control.
- Related findings: F-009
- Draft treatment: marker only

#### D-06 | open | non-blocking
- Question: Which role owns this SOP?
- Owner: [to be named by Finance lead]
- Options: any named role
- Related findings: F-011
- Draft treatment: marker only
- Interim text if undecided: the original "Owner: Finance". F-011 stays open.

#### D-07 | open | release-critical
- Question: Who contacts the bank to try to recall a misdirected payment, and who else must be told?
- Owner: [to be named by SOP owner]
- Options: no values proposed.
- Related findings: F-005
- Draft treatment: marker only

## Scenario notes
- New employee, literal reading: a domain match "passes", so they update and pay. Produced F-001 and F-002.
- Operator under pressure, "payment due today": the S5 exception is used. Produced F-004.
- Controller on leave plus an urgent request: requests stall and the incentive to bypass grows. Produced F-003, and strengthened F-004.
- Suspicious request with no instruction: the operator might reply to the attacker. Produced F-005.
- Process owner after a reported fraud: no verification evidence and no recall owner. Produced F-006 and F-005.
- Combination of a compromised vendor mailbox and a queued payment run: produced F-010.
- An old request is replayed after a newer approved change: produced F-012.
- An urgent release combined with the regular payment run: produced F-013. Whether the system blocks duplicate payments is unknown.
- Second-order check on the revised text: step 6 now waits on D-03, so the procedure stalls until D-03 is decided. This is why D-03 is release-critical; no new finding.

## Reconciliation
Script (`reconcile.py` v0.1.1, run in the build sandbox):
```text
PASS  13 findings and 7 decisions parsed
PASS  all 14 core checks present in ledger
PASS  all 6 business checks present in ledger
PASS  all 7 cyber checks present in ledger
PASS  every original section anchor is accounted for (8 reviewed, 0 not reviewed)
PASS  verdict 'Not ready' consistent with findings and decisions
PASS  revised draft status line consistent with open decisions
PASS  draft header 'Release-blocking decisions' matches the decision log
PASS  draft header 'Non-blocking decisions' matches the decision log
PASS  revised SOP equals the original with all redlines applied (formatting exceptions only)
PASS  secret check run (0 redacted value(s) tracked; values never printed)

Summary: 0 error(s), 0 warning(s).
Not checked by this script (requires reviewer judgment):
  - whether each finding is real, correctly classified, or correctly rated
  - whether a fix actually resolves its finding or introduces a new semantic defect
  - whether ledger observations are true (only that they exist and are specific enough to parse)
  - handoffs and dependencies that are not explicit in the text
  - whether decision options are complete or neutral
  - secrets the reviewer did not mark with [REDACTED: ...] beyond a few common patterns
  - cross-document consistency in multi-SOP reviews (one document per run; see output-format.md)
  - anything about how the process operates in practice
```
Semantic checks done by the reviewer:
- Each Critical and High finding was traced to revised text that removes the defective instruction, or to a named decision where a value is needed.
- The revised text was re-walked as a new employee and as an operator under pressure:
  - Step 3 routes failures to 5A, which exists.
  - Steps 7–8 prevent a stale request from overwriting newer details.
  - Step 9 relies on the contact source from step 2 (D-01).
  - S5 no longer contradicts S3.

Corrections history:
- **Missed second-order defect, fixed in v0.1.1.** The v0.1.0 reconciliation said "no new finding". That was wrong: R-006 sent every fraud report to the Controller, with no route when the Controller is unavailable or involved. R-006 now routes to the backup approver under D-03. This is a defect in the draft, not in the original, so it is recorded here rather than as a finding against the original. It remains covered by F-005.
- **Wrong B02 observation, corrected in v0.1.1.** In v0.1.0, B02 was marked as no finding, with double payment called out of scope. Original S5 explicitly lets the AP Clerk release payment, so B02 now cites F-012 (stale or replayed request) and F-013 (possible duplicate payment). F-013 is Conditional, because duplicate-payment controls in the system are unknown.
- **Step dependency on D-03.** Step 6 cannot run until D-03 is decided. This is why D-03 is release-critical.
