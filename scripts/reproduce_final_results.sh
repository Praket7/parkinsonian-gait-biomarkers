#!/usr/bin/env bash
set -euo pipefail
python -m src.run_pipeline --config configs/analysis.yaml --data-root "${PARKINSON_GAIT_DATA_ROOT:?Set PARKINSON_GAIT_DATA_ROOT to the authorized Drive folder}"
