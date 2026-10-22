# Cybersecurity lens

Activate when the procedure involves identities, access, credentials, systems, sensitive data or incidents. Results are recorded in the ledger as K01–K07.

**K01 Identity validation.**
- Before acting on a request, is the requester's identity verified through a channel independent of the request (call-back to a number on file, a known manager, in-person)?
- Is a spoofable signal (email domain, display name, caller ID, knowledge of public facts) treated as proof?

**K02 Access and least privilege.**
- Is access granted, changed and removed on defined triggers, scoped to need, and reviewed?
- Does the SOP rely on a system enforcing something without saying so? If so, raise it as Conditional or context-unknown, not as a confirmed defect.

**K03 Privileged and emergency access.**
- How are elevated rights obtained, time-limited, logged, and revoked?
- Is there a break-glass path, and is it controlled and reviewed after use?

**K04 Incident escalation.**
- Are suspicious events, failed verifications and suspected compromise routed to someone with authority?
- Are the means and urgency of escalation clear?
- Is the operator told not to tip off a suspected attacker (for example by replying through the attacker's channel)?

**K05 Evidence preservation.** Are logs, messages and artifacts preserved when something suspicious happens, not deleted, overwritten or auto-expired before review?

**K06 Containment and recovery.**
- After compromise or a wrong change, how is damage stopped (disable, revoke, rotate, recall), how is it restored, and how is that confirmed?
- Are dependent systems and in-flight actions considered?

**K07 Secrets handling.**
- Are credentials, keys and tokens kept out of the SOP, tickets and chat?
- Are secrets rotated when people leave or exposure is suspected?
- Are shared accounts accounted for?
- If the SOP itself contains a secret, that is a finding. Quote it as `[REDACTED: credential]`.

Do not claim compliance with any framework. Mapping to a framework, if requested, is the owner's assertion to verify.
