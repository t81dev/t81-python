# Architecture

## Goals

- Provide a stable Python-first entrypoint for balanced ternary experimentation.
- Keep the base install lightweight and push heavy integrations behind extras.
- Preserve deterministic behavior in quantization primitives.
- Support artifact export workflows usable in CI/CD and release pipelines.

## Layers

1. Core (`core.py`): `Trit` and `TritVector` typed model.
2. Quantization (`quantization.py`): threshold mapping, dequantization, and packing.
3. Pipelines (`pipelines/hf_export.py`): state-dict style export to packed ternary + manifest.
4. Integrations (`integrations/`): optional adapters for external runtime ecosystems.
5. CLI (`cli.py`): operational entrypoint for diagnostics and export.

## Dependency Policy

- Required: `numpy`.
- Optional: `torch` + `transformers` (`hf` extra), `llama-cpp-python` (`llama` extra).
- Development: lint/type/test tools under `dev` extra.

## Automation

- `.github/workflows/ci.yml`: lint, type-check, tests, and build validation.
- `.github/workflows/publish.yml`: build and publish to PyPI on `v*` tags.
