# AI operations lens

Activate when a model, LLM, agent, or automated decision system generates content, recommends, or takes actions within the procedure. Results are recorded in the ledger as A01–A09.

This lens reviews the *procedure*; it gives no assurance about model safety.

**A01 Data handling.**
- What data enters the model or tool?
- Is sensitive data minimized, excluded or protected?
- Where do prompts, outputs and logs go, and who can read them?
- Are vendor or retention terms an owner decision? Never assume them.

**A02 Untrusted input and prompt injection.**
- Does the AI read content controlled by outsiders (email, tickets, web pages, documents, chat)?
- If so, can that content steer actions or tool calls?
- Does the SOP keep untrusted content from authorizing anything?

**A03 Output validation.**
- Are outputs checked before use, against what source, and by whom or what?
- What happens when output is malformed, low-quality, or conflicts with the record?

**A04 Human oversight.**
- Where must a human review, and with what criteria and time?
- Is review meaningful, or a rubber stamp (volume, no checklist, auto-accept on timeout)?
- Who is accountable for the outcome?

**A05 Recommendations versus executable actions.**
- Is it explicit which outputs are suggestions and which actions the AI may take itself?
- Are irreversible or high-consequence actions gated by a human or deterministic check?

**A06 Agent permissions and tool scope.**
- Are tool and permission scopes the minimum needed?
- Are limits enforced technically or only by instruction? If unknown, record a Conditional finding.
- Can the agent change its own permissions, other records, or payment and identity data?

**A07 Monitoring.**
- Is there ongoing review of errors, drift, overrides, complaints and abuse?
- Who reviews, how often, and on what trigger do they act? Values are owner decisions.

**A08 Change management.**
- How are model, prompt, tool and vendor-version changes approved, tested and recorded?
- Do vendor-side updates arrive unannounced?

**A09 Fallback and rollback.**
- Is there a way to stop the AI quickly (a kill switch), and who can use it?
- Is there a manual fallback when the AI is unavailable or disabled?
- Can actions taken by the AI be identified and reversed?
