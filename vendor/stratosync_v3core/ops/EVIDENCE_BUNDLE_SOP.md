# Evidence Bundle SOP (Sovereign-Ready posture)

## Artifacts
- audit_log.jsonl (hash-chained)
- state_db.json (latest snapshot per project)
- version manifest (git commit / build id)
- configuration snapshot (thresholds/weights)

## Procedure
1) For each decision window, export:
   - filtered audit records for project_id(s)
   - hash chain verification (prev_hash continuity)
2) Generate a decision memo:
   - state outputs (S, Δ, Ψ) + reasons
   - override records (if any) with approver identity (external system)
3) Store bundle in immutable storage (WORM / object lock) if required.

## Verification
- Recompute SHA256 chain for exported records and compare to embedded record_hash.


## Optional (v2.6.2)
- Include `board.pdf` (1-page decision sheet) and `trend.png` in the bundle when exporting.
