# API SPEC — STRATOSYNC v2.6

## POST /evaluate
Evaluates the current synchronization state.

Request JSON:
{
  "project_id": "string (optional)",
  "political_score": 0.0-1.0,
  "capital_score": 0.0-1.0,
  "execution_score": 0.0-1.0,
  "noise": 0.0-1.0,
  "weights": {"wp":0.4,"wc":0.3,"we":0.3} (optional),
  "alpha": 0.2 (optional)
}

Response JSON:
{
  "evaluation_id": "uuid",
  "project_id": "...",
  "version": "2.6",
  "inputs": {...},
  "outputs": {
     "political_filtered": ...,
     "capital_filtered": ...,
     "execution_filtered": ...,
     "synchronization_score": ...,
     "delta_index": ...,
     "psi_adjusted_execution": ...,
     "system_state": "GO|CONDITIONAL|FREEZE",
     "reasons": ["..."]
  },
  "audit": {
     "record_hash": "sha256",
     "prev_hash": "sha256 or null"
  },
  "timestamp": "ISO-8601"
}

## GET /state/{project_id}
Returns the last evaluation for a project.

## GET /delta-trend/{project_id}?n=50
Returns last n delta values for charting.

## POST /override-lock
Governance-gated endpoint (requires ADMIN_TOKEN).
Use to apply a temporary override with reason and expiry.


## GET /audit/verify/{project_id}
Verifies record_hash correctness for the last n records for a project.

## POST /evidence/export/{project_id}
Creates an evidence bundle zip under /data (ADMIN_TOKEN required).

## GET /board/{project_id}
Returns a simple board-ready HTML view for the latest project state.


## GET /trend/png/{project_id}
Renders a PNG chart for Δ-Index and Sync Score over the last n evaluations.

## GET /board/pdf/{project_id}
Renders a 1-page board PDF (includes embedded trend chart when available).


### Evidence bundle attachments (v2.7.1)
`POST /evidence/export/{project_id}` now includes `trend.png` and `board.pdf` inside the exported zip when available.
