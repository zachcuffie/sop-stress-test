# Revision mode

Use revision mode when the user supplies a new version together with a prior report (or prior findings register).

1. **Diff.** Compare the old and new versions. Identify changed, added, removed and moved sections.
2. **Decide the review breadth.**
   - **Incremental review:** re-check the changed sections plus every section that depends on them. Use explicit references (from `sop_outline.py`) and your semantic map of roles, handoffs and timing. The script's reference list is an aid; it is not the dependency truth.
   - **Full re-review:** required instead when any of these changed broadly:
     - ownership or roles;
     - scope or applicability;
     - systems or tools;
     - external dependencies;
     - the overall structure (many sections renumbered or merged).

     When unsure, do the full re-review and say why.
3. **Carry prior findings forward with the same IDs.**

| Situation | Status |
|---|---|
| The new text fixes it, and you checked the text | `verified-in-document` |
| A prior `verified-in-document` fix was undone | `regressed`, same ID |
| The same issue reappears after being withdrawn or verified | Reopen with the same ID; note the history |
| Still present | `open` or `awaiting-owner-decision` |
| Prior finding no longer valid (for example the section was removed for a sound reason) | `withdrawn`, with rationale |

4. **New issues**, including defects introduced by the fixes, get **new** IDs, continuing from the highest prior ID. Never renumber.
5. **Unchanged sections** are not re-reported, but their ledger entries are carried forward and labeled "carried from prior review".
6. **Re-issue outputs.** Issue a new verdict, new redlines for the remaining issues only, and a regenerated revised SOP. Then run reconciliation.
7. **Operational verification** remains `unknown` unless the user supplies evidence about how the process runs.
