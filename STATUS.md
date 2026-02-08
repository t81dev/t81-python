# STATUS

Snapshot date: 2026-02-08

## Current State

- Package scaffold, typed APIs, and CLI are in place.
- End-to-end export workflows support:
  - `export-hf-json` for JSON state-dict fixtures
  - `export-hf` for `.safetensors` and `.pt/.pth/.bin`
- Artifact round-trip inspection is available via `inspect-artifact`.
- CI and publish workflows are configured.

## Validation Baseline

- `ruff check .`
- `mypy src tests benchmarks`
- `pytest`
- `python -m build`

All currently pass in local validation.

## Known Constraints

- Real `.pt` export path depends on `torch` availability.
- Ecosystem demo parity in `t81-examples` is not yet synced from this repo.
- No performance regression thresholds are enforced in CI yet.

## Immediate Priorities

1. Mirror canonical export/inspect demos in `t81-examples`.
2. Add checkpoint fixture tests for wider tensor shapes and edge cases.
3. Add benchmark baselines and guardrails for throughput/compression drift.
