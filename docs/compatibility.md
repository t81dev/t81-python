# Compatibility

## Python Support

- Supported runtime versions: Python `3.9` through `3.12`.
- CI executes quality checks across this matrix.

## Optional Dependency Support

- `hf` extra: `torch>=2.1`, `transformers>=4.40`, `safetensors>=0.4`
- `llama` extra: `llama-cpp-python>=0.2.90`

Optional integrations are feature-gated. Core package workflows remain usable without these extras.

## Artifact Compatibility

- Current artifact format version: `0.1`.
- `manifest.json` includes `format_version`; consumers must validate this before decode.
- Backward-incompatible artifact changes require a format-version increment and migration notes.

## CLI Compatibility

Public CLI commands are treated as stable contract surface once documented in `README.md` and `docs/api.md`.

- Additive commands/options may ship in minor releases.
- Renames/removals require changelog entries and migration guidance.
