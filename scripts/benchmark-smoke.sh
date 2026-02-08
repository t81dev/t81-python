#!/usr/bin/env bash
set -euo pipefail

OUT_DIR=".ci-benchmark-out"
REPORT_JSON=".ci-benchmark-report.json"

python benchmarks/benchmark_export.py \
  --tensors 4 \
  --values-per-tensor 256 \
  --threshold 0.05 \
  --output "${OUT_DIR}" > "${REPORT_JSON}"

python - <<'PY'
from t81_python.pipelines import inspect_artifact

summary = inspect_artifact('.ci-benchmark-out')
if not all(summary.per_tensor_payload_ok.values()):
    raise SystemExit('Artifact sanity check failed: one or more payloads did not round-trip')
print('Artifact sanity check passed for benchmark smoke run')
PY

find "${OUT_DIR}" -type f -delete 2>/dev/null || true
find "${OUT_DIR}" -type d -empty -delete 2>/dev/null || true
find . -maxdepth 1 -name "${REPORT_JSON}" -type f -delete
