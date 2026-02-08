# Ecosystem Contracts

This document defines cross-repository contracts for `t81-python` within the `t81dev` ecosystem.

## Repository Role

`t81-python` is the Python-facing integration and artifact workflow layer.

- It should expose ergonomic typed APIs for ternary quantization workflows.
- It should provide stable CLI workflows for export and artifact inspection.
- It should avoid duplicating low-level arithmetic primitives that belong in `t81lib`.

## Upstream/Downstream Boundaries

### `t81-vm` (runtime upstream)

Contract:

- `t81-vm` owns VM execution semantics and the host C ABI.
- `t81-python` consumes `include/t81/vm/c_api.h` through `src/t81_python/vm_bridge.py`.
- ABI changes require synchronized updates in `t81-vm/docs/contracts/vm-compatibility.json` and `t81-python` compatibility notes/tests.

### `t81lib` (upstream core)

Contract:

- `t81lib` owns high-performance arithmetic kernels and low-level primitives.
- `t81-python` may consume `t81lib` interfaces, but does not redefine core numeric semantics.
- Any artifact encoding change should be coordinated so both repos can read/write consistently.

### `t81-examples` (demo surface)

Contract:

- Canonical user workflows should be mirrored in `t81-examples`.
- `t81-python` examples remain minimal and package-scoped; broader narrative demos belong in `t81-examples`.

### `t81-docs` (docs hub)

Contract:

- Repo metadata in `ecosystem.json` should remain accurate for docs automation.
- Any CLI/API/format changes should be reflected in local docs and be sync-ready for central docs.

## API Compatibility Policy

- Public API surface is `t81_python.*` and documented CLI commands.
- Backward-incompatible API removals require a documented deprecation path.
- New CLI commands may be added in minor releases; renames/removals require changelog and migration notes.

## Artifact Compatibility Policy

- Export artifact format is versioned via `format_version` in `manifest.json`.
- Consumers must check `format_version` before decoding.
- Breaking encoding/schema changes require a new format version and migration guidance.

## Release Coordination Checklist

1. Update `CHANGELOG.md`, `STATUS.md`, and `ROADMAP.md`.
2. Run quality gates locally and in CI.
3. Confirm docs changes in `README.md` and `docs/`.
4. If contract-impacting changes exist, notify dependent repos (`t81-docs`, `t81-examples`, `t81lib`).
