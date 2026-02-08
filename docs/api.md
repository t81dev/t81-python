# API Summary

## Core

- `t81_python.Trit`: enum values `-1`, `0`, `1`.
- `t81_python.TritVector.from_ints(values)`: build typed trit vectors.
- `TritVector.to_ints()`: convert back to plain integers.

## Quantization

- `quantize_float_to_trits(values, threshold=0.05)` -> `TritVector`
- `dequantize_trits(values, scale=1.0)` -> `numpy.ndarray`
- `pack_trits(values)` -> `bytes`
- `unpack_trits(payload, count)` -> `TritVector`

## Pipelines

- `export_state_dict_to_ternary(state_dict, output_dir, threshold=0.05, source="in_memory")` -> `ExportManifest`
- `export_checkpoint_to_ternary(checkpoint_path, output_dir, threshold=0.05)` -> `ExportManifest`
- `load_json_state_dict(path)` -> `dict[str, Any]`
- `load_checkpoint_state_dict(path)` -> `dict[str, Any]`
- `read_manifest(path)` -> `ExportManifest`
- `inspect_artifact(output_dir)` -> `ArtifactInspection`

### Export Artifacts

- `manifest.json`:
  - generation timestamp
  - source path/id
  - threshold
  - per-tensor summaries (shape, counts, payload filename)
- `*.t81bin`: packed 2-bit symbol streams for ternary payloads

## Integrations

- `t81_python.integrations.huggingface.is_available()` -> `bool`
- `quantize_state_dict(state_dict, threshold=0.05)` -> `dict[str, list[int]]`
- `t81_python.integrations.llama_cpp.is_available()` -> `bool`
- `build_model_kwargs(...)` -> `dict[str, Any]`

## CLI

- `t81-python info`
- `t81-python quantize [--threshold ...] <values...>`
- `t81-python export-hf-json <input.json> <output_dir> [--threshold ...]`
- `t81-python export-hf <checkpoint.(safetensors|pt|pth|bin)> <output_dir> [--threshold ...]`
- `t81-python inspect-artifact <output_dir>`
