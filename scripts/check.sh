#!/usr/bin/env bash
set -euo pipefail

scripts/validate-ecosystem-json.py
scripts/sync-docs.sh
ruff check .
mypy src tests benchmarks
pytest -q
