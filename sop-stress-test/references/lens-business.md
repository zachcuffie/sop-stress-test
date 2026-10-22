# Business operations lens

Activate when the procedure involves money, vendors, customers, approvals, staffing or service delivery. Results are recorded in the ledger as B01–B06.

**B01 Approvals and segregation.**
- Is approval required *before* the action it controls?
- Is the approver someone other than the person executing, where the consequence warrants it?
- Is the approver's authority bounded?
- Can approval be bypassed by urgency, size-splitting, or self-approval?

Thresholds are owner decisions; never invent amounts.

**B02 Duplicate and repeated processing.**
- Could the same request, invoice, payment or order be processed twice (resubmission, two channels, retry after a partial failure)?
- Is there a check before acting?

**B03 Reconciliation.** Is there a periodic or per-run comparison that would detect errors the per-item steps miss (records against bank, system against source)? Scale to consequence and volume.

**B04 Vendors and third parties.**
- Are third-party inputs validated?
- Are changes to third-party master data (contacts, bank details) independently verified?
- Are dependencies on a vendor's timing or availability handled?

**B05 Staffing and coverage.** Do absence, vacation, turnover or after-hours operation stall or break the process? Is there a backup role? Does the process depend on one person's undocumented knowledge?

**B06 Continuity.**
- What happens when a key system or channel is down?
- Is there a manual fallback, and does it preserve the key control?
- How is backlog handled when service is restored?
