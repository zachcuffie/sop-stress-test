# SOP Stress Test report (prior round): Staff Password Reset by Help Desk
Verdict: Not ready

## Findings register (excerpt carried into revision)

#### F-001 | Confirmed defect | Critical | open
- Title: Identity confirmed with name and employee ID only
- Check: K01
- Locations: S1 step 2
- Evidence: "asking for the staff member's full name and employee ID"
- Fix type: doc edit + owner decision
- Operational verification: unknown

#### F-002 | Confirmed defect | Medium | open
- Title: No record of resets
- Check: C09
- Locations: S1
- Evidence: no logging step
- Fix type: doc edit
- Operational verification: unknown

#### F-003 | Confirmed defect | High | verified-in-document
- Title: Temporary password not forced to change (fixed in v1 by step 4)
- Check: K02
- Locations: S1 step 4
- Evidence: v1 step 4 "must be changed at first login"
- Fix type: doc edit
- Operational verification: unknown

#### F-004 | Confirmed defect | Medium | open
- Title: No path for resets outside help desk hours
- Check: C08, C10
- Locations: S2
- Evidence: "8:00 to 18:00 on weekdays"
- Fix type: owner decision
- Operational verification: unknown
