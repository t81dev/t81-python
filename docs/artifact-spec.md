# Artifact Spec

This document defines the `t81-python` ternary artifact format produced by export commands.

## Version

- Current `format_version`: `0.1`

## Directory Layout

- `manifest.json`
- `*.t81bin` payload files (one per tensor)

## `manifest.json` Schema

Top-level fields:

- `generated_at_utc` (`string`, ISO8601 UTC timestamp)
- `format_version` (`string`)
- `source` (`string`)
- `threshold` (`number`)
- `tensors` (`array`)

Each tensor entry:

- `name` (`string`)
- `shape` (`array[int]`)
- `numel` (`int`)
- `threshold` (`number`)
- `counts` (`object` with keys `-1`, `0`, `+1`)
- `payload_file` (`string`, relative filename ending in `.t81bin`)

## Payload Encoding

- Payloads are packed 2-bit symbols in little-endian bit order within each byte.
- Trit to symbol mapping:
  - `-1 -> 0`
  - `0 -> 1`
  - `+1 -> 2`
- Symbol `3` is currently unused.

## Validation Rules

- `numel` must equal the decoded trit count for each payload.
- Decoded per-tensor trit counts must match `counts` in `manifest.json`.
- Aggregate trit counts should be derivable by summing tensor-level counts.

## Forward Compatibility

- Consumers should branch behavior on `format_version`.
- Any incompatible encoding or schema change should increment `format_version`.
