> **DRAFT. Not approved for operational use.** Produced by an SOP Stress Test review of "Changing a Vendor's Bank Details" (last updated March 2026). Changes trace to findings in report.md and redlines.md. Owner approval is required before any use.
> Release-blocking decisions: D-01, D-02, D-03, D-05, D-07 (each leaves a Critical or High finding unresolved, or a step that cannot be carried out).
> Non-blocking decisions: D-04, D-06 (before release, decide each one or replace its marker with the interim text in the decision log; the related finding then stays open).
<!-- END DRAFT HEADER -->
# SOP: Changing a Vendor's Bank Details

Owner: [[DECISION D-06: named role that owns this SOP]]
Last updated: March 2026

## 1. Purpose
This procedure explains how to update a vendor's payment details in the accounting system so that payments go to the right account.

## 2. Scope
Applies to all changes to vendor bank account details in the accounting system. Does not cover adding new vendors (see the New Vendor Setup SOP).

## 3. Roles
- AP Clerk: receives requests and updates the vendor record.
- Controller: approves changes.
[[DECISION D-05: confirm whether the accounting system requires approval before a bank detail change takes effect; if it does not, decide what compensating control applies]]

## 4. Procedure
1. The AP Clerk receives the change request from the vendor, usually by email.
2. Verify the request independently. Call the vendor using contact details from [[DECISION D-01: authoritative source of vendor contact details, and who may make the verification call]], not from the request. Confirm the change with a person at the vendor. A matching email domain does not count as verification.
3. If the vendor does not confirm the change, or the request seems unusual, stop. Do not change the record. Follow Section 5A.
4. Record the verification on the request: who called, the number used, who confirmed at the vendor, and the date and time.
5. Send the request and the verification record to the Controller for approval. Do not change the vendor record yet.
6. The Controller approves or rejects the change within [[DECISION D-03: review turnaround, and the backup approver when the Controller is unavailable]].
7. After approval, check that the vendor record has not changed since this request was received and that no other change request for this vendor is open. If either is not true, stop and start again from step 2 with the most recent request.
8. Update the bank details in the vendor record in the accounting system.
9. Send a confirmation of the change to the vendor using the contact details from step 2, and check any payments already scheduled to this vendor so they go to the approved account.
10. File the request, the verification record and the approval in the vendor folder.

## 5. Urgent requests
[[DECISION D-02: whether urgent requests may use any exception to Section 4; options are in the decision log. Under every option, no change is made and no payment is released before independent verification and approval.]]

## 5A. Suspected fraud or failed verification
1. Do not change the vendor record and do not release any payment to the new details.
2. Do not reply using contact details from the request.
3. Keep the request and its attachments; do not delete them.
4. Report it to the Controller before taking any other action on this vendor. If the Controller is unavailable or is involved in the request, report it to the backup approver named under D-03.
5. If a payment may already have gone to details that were not verified, tell the Controller at once. [[DECISION D-07: who contacts the bank to try to recall the payment, and who else must be told]]

## 6. Records
Keep the request, the verification record, the approval and any attachments in the vendor folder for [[DECISION D-04: retention period for vendor change records]].

## 7. Questions
Contact the SOP owner with any questions.
