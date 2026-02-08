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

## VM ABI Compatibility

- Runtime integration target: `t81-vm` C ABI (`include/t81/vm/c_api.h`).
- Baseline runtime contract tag: `runtime-contract-v0.1`.
- Default bridge loader behavior:
  - use `T81_VM_LIB` if set,
  - else attempt workspace-local `t81-vm/build/libt81vm_capi.{dylib,so}`.
- ABI and bridge regressions are covered by `tests/test_vm_bridge.py`.
- Bridge parity canary includes VM P0 comparison/conversion opcodes (`Less`, `I2F`, `F2I`, `I2Frac`, `Frac2I`).
- Contract assumptions are validated by `scripts/check-vm-contract.py`.
- CI coverage:
  - runtime contract gate against `t81-vm/main` (`scripts/check-vm-contract.py`),
  - floating lane against latest `t81-vm/main`,
  - pinned lane against `runtime-contract-v0.1`.

## Release Cadence Rule

- VM ABI-affecting changes in `t81-vm` require synchronized updates to:
  - `docs/compatibility.md` (this file),
  - `docs/contracts.md`,
  - bridge tests in `tests/test_vm_bridge.py`.
