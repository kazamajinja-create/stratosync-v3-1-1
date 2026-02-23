# Board Dashboard — Wireframe (v2.6)

## 1-page Board View (printable)
[HEADER]
- Project: <name> | Date: <timestamp> | Version: 2.6
- SYSTEM STATE (traffic light):  🟢 GO  /  🟡 CONDITIONAL  /  🔴 FREEZE

[CORE METRICS]
- Political Stability (P): 0.xx   | Band: Stable/Pending/Volatile
- Capital Readiness (C):  0.xx   | Band: Confirmed/Conditional/Unsecured
- Execution Readiness (E):0.xx   | Band: Ready/Partial/Locked
- Synchronization Score (S): 0.xx
- Δ-Index: 0.xx
- Ψ (pressure-adjusted): 0.xx

[ALIGNMENT TRIANGLE]
        P
       / \
      /   \
     C-----E
- Display Δ as “spread” (distance)

[DECISION PANEL]
- Recommendation: GO / CONDITIONAL / FREEZE
- Rationale bullets (top 3):
  1) ...
  2) ...
  3) ...

[LOCK / RELEASE]
- Hard Freeze Condition: met / not met
- Capital Release Trigger: met / not met
- Next evaluation: <time window>

## Operational View (team)
Tabs:
- Overview | Trend | Audit | Governance
Trend:
- Δ and S time series
- State timeline (GO/COND/FREEZE)
Audit:
- hash chain verification status
Governance:
- override history, approvals, expiry


## Implementation note
- A minimal board HTML endpoint is provided at `GET /board/{project_id}`.


## v2.6.2 additions
- `GET /trend/png/{project_id}` renders an embeddable trend chart.
- `GET /board/pdf/{project_id}` renders a 1-page PDF board sheet.
