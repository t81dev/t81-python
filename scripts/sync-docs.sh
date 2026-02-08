#!/usr/bin/env bash
set -euo pipefail

# Repo-local docs sync helper aligned with t81-docs style workflows.
# It validates required metadata/docs artifacts exist and emits a concise summary
# that can be consumed by higher-level ecosystem sync scripts.

required_files=(
  "README.md"
  "ecosystem.json"
  "STATUS.md"
  "ROADMAP.md"
  "docs/api.md"
  "docs/architecture.md"
  "docs/artifact-spec.md"
  "docs/contracts.md"
  "docs/releasing.md"
)

missing=0
for file in "${required_files[@]}"; do
  if [[ ! -f "${file}" ]]; then
    echo "missing: ${file}"
    missing=1
  fi
done

if [[ ${missing} -ne 0 ]]; then
  echo "docs sync check failed"
  exit 1
fi

python3 - <<'PY'
import json
from pathlib import Path

meta = json.loads(Path("ecosystem.json").read_text(encoding="utf-8"))
summary = {
    "name": meta.get("name"),
    "snapshot_date": meta.get("snapshot_date"),
    "status": meta.get("status"),
    "maturity": meta.get("maturity"),
    "artifact_versions": [a.get("version") for a in meta.get("artifact_formats", [])],
}
print(json.dumps(summary, indent=2))
PY

echo "docs sync check passed"
