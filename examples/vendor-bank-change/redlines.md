# Redlines: SOP "Changing a Vendor's Bank Details"
These are text redlines, not native Word tracked changes. Each block cites the findings it addresses. Redlines are numbered in document order.

#### R-001 | S0 | replace
- Findings: F-011
- Reason: A department is not an accountable owner. The role is an owner decision, so the line carries a marker instead of an invented role.
Before:
```text
Owner: Finance
```
After:
```text
Owner: [[DECISION D-06: named role that owns this SOP]]
```

#### R-002 | S3 | insert-after
- Findings: F-009
- Reason: Segregation between changing details and releasing payment currently rests on this document alone. Whether the system enforces it is unknown to the reviewer and must be confirmed.
Before:
```text
- Controller: approves changes.
```
After:
```text
[[DECISION D-05: confirm whether the accounting system requires approval before a bank detail change takes effect; if it does not, decide what compensating control applies]]
```

#### R-003 | S4 | replace
- Findings: F-001, F-002, F-003, F-006, F-012
- Reason: The edit makes five changes. Independent verification replaces the spoofable domain check (F-001). Approval moves before the change it controls (F-002). Review gets a time limit and a backup through a decision marker (F-003). The verification evidence is recorded (F-006). A stale or replayed request can no longer overwrite newer details (F-012). Step 1 is kept unchanged.
Before:
```text
2. Confirm the request is from the vendor by checking that the email comes from the vendor's domain.
3. Update the bank details in the vendor record in the accounting system.
4. Send the Controller an email letting them know the change was made.
5. The Controller approves the change when they get a chance.
```
After:
```text
2. Verify the request independently. Call the vendor using contact details from [[DECISION D-01: authoritative source of vendor contact details, and who may make the verification call]], not from the request. Confirm the change with a person at the vendor. A matching email domain does not count as verification.
3. If the vendor does not confirm the change, or the request seems unusual, stop. Do not change the record. Follow Section 5A.
4. Record the verification on the request: who called, the number used, who confirmed at the vendor, and the date and time.
5. Send the request and the verification record to the Controller for approval. Do not change the vendor record yet.
6. The Controller approves or rejects the change within [[DECISION D-03: review turnaround, and the backup approver when the Controller is unavailable]].
7. After approval, check that the vendor record has not changed since this request was received and that no other change request for this vendor is open. If either is not true, stop and start again from step 2 with the most recent request.
8. Update the bank details in the vendor record in the accounting system.
```

#### R-004 | S4 | replace
- Findings: F-010, F-006
- Reason: Adds a confirmation to the vendor's known contact, which catches fraud that got past verification, and a check of payments already scheduled. Also widens the filed record to include the verification and the approval.
Before:
```text
6. File the request email in the vendor folder.
```
After:
```text
9. Send a confirmation of the change to the vendor using the contact details from step 2, and check any payments already scheduled to this vendor so they go to the approved account.
10. File the request, the verification record and the approval in the vendor folder.
```

#### R-005 | S5 | replace
- Findings: F-004
- Reason: The urgent path allowed a change and a payment before any approval, which is the pressure pattern this procedure most needs to resist. Whether any exception exists is an owner decision. Every option in D-02 removes the part that skips verification and approval, so the draft removes it without choosing between the options.
Before:
```text
If the vendor says a payment is due today, the AP Clerk may make the change and release the payment before the Controller approves, to avoid late fees.
```
After:
```text
[[DECISION D-02: whether urgent requests may use any exception to Section 4; options are in the decision log. Under every option, no change is made and no payment is released before independent verification and approval.]]
```

#### R-006 | S6 | insert-before
- Findings: F-005
- Reason: There was no path for a failed verification or a suspected fraud, and no recovery if money had already moved. The recall step needs an owner decision. Reports go to the Controller or, when the Controller is unavailable or involved, to the backup approver under D-03 (this second route was added in v0.1.1 after the second-order check).
Before:
```text
## 6. Records
```
After:
```text
## 5A. Suspected fraud or failed verification
1. Do not change the vendor record and do not release any payment to the new details.
2. Do not reply using contact details from the request.
3. Keep the request and its attachments; do not delete them.
4. Report it to the Controller before taking any other action on this vendor. If the Controller is unavailable or is involved in the request, report it to the backup approver named under D-03.
5. If a payment may already have gone to details that were not verified, tell the Controller at once. [[DECISION D-07: who contacts the bank to try to recall the payment, and who else must be told]]
```

#### R-007 | S6 | replace
- Findings: F-008, F-006
- Reason: "As long as required" cannot be followed. The period is an owner decision. The record now includes the verification and the approval.
Before:
```text
Keep the request email and any attachments in the vendor folder for as long as required.
```
After:
```text
Keep the request, the verification record, the approval and any attachments in the vendor folder for [[DECISION D-04: retention period for vendor change records]].
```

#### R-008 | S7 | replace
- Findings: F-011
- Reason: Points questions to the accountable owner instead of a department.
Before:
```text
Contact Finance with any questions.
```
After:
```text
Contact the SOP owner with any questions.
```
