# ROADMAP

## 0.1.x (Near term)

- Add richer real-checkpoint tests (`.safetensors` + `.pt`) for varied tensor layouts.
- Add benchmark result snapshots and CI-friendly benchmark smoke checks.
- Add migration notes and artifact compatibility examples.

## 0.2.x (Short term)

- Add direct Hugging Face model loading helpers and selective module export filters.
- Add richer artifact inspection outputs (per-tensor entropy/distribution stats).
- Add optional conversion bridges for downstream packaging (e.g., GGUF metadata helpers).

## 0.3.x (Medium term)

- Align more closely with `t81lib` runtime primitives for unified compute + export stories.
- Add signed release artifacts and tightened release governance.
- Add cross-repo integration docs synced into `t81-docs`.

## Success Criteria

- Stable, documented API and CLI contracts.
- Reproducible export artifacts with versioned schema guarantees.
- Measurable throughput/compression tracking over time.
