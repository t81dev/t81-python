# t81-python

High-level Python package for the `t81dev` ecosystem with clean APIs, type hints, and integration helpers for Hugging Face and llama.cpp Python bindings.

## Status

`0.1.0` foundation scaffold plus CI, release automation, and an end-to-end export workflow for checkpoint-like tensors.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Optional extras:

```bash
pip install -e '.[hf]'
pip install -e '.[llama]'
pip install -e '.[dev]'
```

## Quickstart

```python
from t81_python import quantize_float_to_trits

trits = quantize_float_to_trits([0.12, -0.40, 0.01], threshold=0.05)
print(trits.to_ints())  # [1, -1, 0]
```

CLI:

```bash
t81-python info
t81-python quantize --threshold 0.05 0.2 -0.3 0.0
```

## End-to-End Export Workflow

Given a JSON mapping that looks like a simplified state dict:

```json
{
  "lm_head.weight": [0.22, -0.44, 0.01, 0.00],
  "model.layers.0.attn.q_proj.weight": [[0.3, -0.2], [0.07, -0.01]]
}
```

Export packed ternary artifacts and a manifest:

```bash
t81-python export-hf-json examples/hf_state_dict.json ./out-ternary --threshold 0.05
```

Output includes:

- `out-ternary/manifest.json`
- one `.t81bin` payload per tensor

From real checkpoints:

```bash
t81-python export-hf ./model.safetensors ./out-ternary --threshold 0.05
t81-python export-hf ./model.pth ./out-ternary --threshold 0.05
```

Validate exported artifacts:

```bash
t81-python inspect-artifact ./out-ternary
```

## Quality and Automation

- CI: `.github/workflows/ci.yml`
- Publish on version tags: `.github/workflows/publish.yml` (tags like `v0.1.0`)
- Standard local scripts: `scripts/check.sh`, `scripts/test.sh`, `scripts/build.sh`, `scripts/release-check.sh`, `scripts/benchmark-smoke.sh`, `scripts/sync-docs.sh`
- Make targets: `make check`, `make test`, `make build`, `make bench`, `make release-check`, `make sync-docs`, `make validate-ecosystem`

## Project Layout

- `src/t81_python/core.py`: balanced ternary core types.
- `src/t81_python/quantization.py`: quantize/dequantize and compact packing utilities.
- `src/t81_python/pipelines/hf_export.py`: end-to-end state-dict export flow.
- `src/t81_python/integrations/huggingface.py`: state-dict ternary conversion helpers.
- `src/t81_python/integrations/llama_cpp.py`: validated kwargs builder for `llama_cpp.Llama`.
- `examples/`: minimal integration-focused scripts.
- `tests/`: `pytest` coverage for core and pipeline behavior.
- `docs/`: architecture and API notes.
- `benchmarks/`: reproducible export throughput/compression benchmark script.

## Ecosystem Alignment

This repository is structured to align with related repositories in `https://github.com/t81dev`:

- typed APIs and clear package surface (`t81lib` style)
- practical docs-first organization (`t81-docs` style)
- reproducible examples and explicit status framing (`t81-examples` + research repos)

## Documentation Index

- `docs/api.md`
- `docs/architecture.md`
- `docs/artifact-spec.md`
- `docs/benchmarks.md`
- `docs/contracts.md`
- `docs/compatibility.md`
- `docs/releasing.md`
- `STATUS.md`
- `ROADMAP.md`
- `ecosystem.json`
