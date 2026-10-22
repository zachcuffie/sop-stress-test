# AI-Assisted Accounts Payable Inbox

Owner: Finance Operations Manager

## 1. Purpose
Use an AI agent to triage the accounts payable inbox, catch phishing, and speed up invoice payment.

## 2. What the agent does
1. The agent reads every email that arrives in the AP inbox, including attachments.
2. It extracts invoice details (supplier, amount, due date, bank details) and creates a payment draft in the payment system.
3. If an email asks to change a supplier's bank details, the agent updates the supplier record in the payment system.
4. Payment drafts under $2,500 are approved automatically by the agent. Larger drafts go to the Finance Operations Manager for approval.
5. The agent flags emails it judges to be phishing and moves them to the Quarantine folder.

## 3. Quarantine
Emails in the Quarantine folder are deleted automatically after 24 hours.

## 4. Oversight
The Finance Operations Manager reviews the agent's activity when issues are reported.

## 5. Configuration
The agent's instructions and permissions are set by the IT contractor.
