#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"
ADMIN_TOKEN="${ADMIN_TOKEN:-CHANGE_ME}"
PROJECT_ID="demo:alpha"

echo "Posting demo evaluations to ${BASE_URL} for project ${PROJECT_ID}..."

for i in $(seq 1 20); do
  # simple deterministic variation
  P=$(python - <<'PY'
import math,sys
i=int(sys.argv[1])
print(round(0.65+0.15*math.sin(i/3),3))
PY $i)
  C=$(python - <<'PY'
import math,sys
i=int(sys.argv[1])
print(round(0.60+0.18*math.cos(i/4),3))
PY $i)
  E=$(python - <<'PY'
import math,sys
i=int(sys.argv[1])
print(round(0.70+0.12*math.sin(i/5),3))
PY $i)
  ETA=$(python - <<'PY'
import math,sys
i=int(sys.argv[1])
print(round(0.05+0.03*abs(math.sin(i/7)),3))
PY $i)

  curl -sS -X POST "${BASE_URL}/evaluate"     -H "Content-Type: application/json"     -d "{"project_id":"${PROJECT_ID}","political_score":${P},"capital_score":${C},"execution_score":${E},"noise":${ETA}}"     >/dev/null
done

echo "Generating board PDF and trend chart..."
curl -sS "${BASE_URL}/trend/png/${PROJECT_ID}?n=50" -o "data/trend_demo_alpha.png" >/dev/null || true
curl -sS "${BASE_URL}/board/pdf/${PROJECT_ID}?n=50" -o "data/board_demo_alpha.pdf" >/dev/null || true

echo "Exporting evidence bundle (admin)..."
curl -sS -X POST "${BASE_URL}/evidence/export/${PROJECT_ID}?n=200"   -H "X-Admin-Token: ${ADMIN_TOKEN}"   -H "Content-Type: application/json"   -d "{}" | tee "data/evidence_export_response.json" >/dev/null || true

echo "Done."
