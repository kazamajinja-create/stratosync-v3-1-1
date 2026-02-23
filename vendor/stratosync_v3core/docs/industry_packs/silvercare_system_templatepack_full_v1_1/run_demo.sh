#!/usr/bin/env bash
set -euo pipefail

INPUT="${INPUT:-05_STRATOSYNC_RELEASE_DEMO/STRATOSYNC_V1_RELEASE_COMPLETE/integrated_case.v1.0.json}"
OUTDIR="${OUTDIR:-out_demo}"
TEMPLATE="${TEMPLATE:-}"

ARGS=()
WRITE_REPORT="${WRITE_REPORT:-}"
if [[ -n "$TEMPLATE" ]]; then
  ARGS+=(--template "$TEMPLATE")
fi

if [[ -n "$WRITE_REPORT" ]]; then ARGS+=(--write-report); fi
python run_demo.py --input "$INPUT" --out "$OUTDIR" "${ARGS[@]}" "$@"
echo "Done. Outputs in: $OUTDIR"
