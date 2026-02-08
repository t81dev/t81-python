"""CLI entrypoint for diagnostics and export pipelines."""

from __future__ import annotations

import argparse
import json

from .pipelines import (
    export_checkpoint_to_ternary,
    export_state_dict_to_ternary,
    inspect_artifact,
    load_json_state_dict,
)
from .quantization import quantize_float_to_trits


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="t81-python")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("info", help="Show package summary")

    q = sub.add_parser("quantize", help="Quantize numeric values into trits")
    q.add_argument("values", nargs="+", type=float, help="Input floats")
    q.add_argument("--threshold", type=float, default=0.05)

    export = sub.add_parser(
        "export-hf-json",
        help="Export a JSON state-dict mapping into packed ternary artifacts",
    )
    export.add_argument("input", help="Path to JSON mapping tensor names -> values")
    export.add_argument("output", help="Output directory")
    export.add_argument("--threshold", type=float, default=0.05)

    export_hf = sub.add_parser(
        "export-hf",
        help="Export a .safetensors/.pt/.pth checkpoint into packed ternary artifacts",
    )
    export_hf.add_argument("input", help="Checkpoint path")
    export_hf.add_argument("output", help="Output directory")
    export_hf.add_argument("--threshold", type=float, default=0.05)

    inspect = sub.add_parser(
        "inspect-artifact",
        help="Inspect/validate an exported artifact directory",
    )
    inspect.add_argument("output", help="Output directory containing manifest.json + payloads")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command in (None, "info"):
        print("t81-python: typed balanced-ternary helpers for AI integration workflows")
        return

    if args.command == "quantize":
        trits = quantize_float_to_trits(args.values, threshold=args.threshold)
        print(" ".join(str(v) for v in trits.to_ints()))
        return

    if args.command == "export-hf-json":
        state_dict = load_json_state_dict(args.input)
        manifest = export_state_dict_to_ternary(
            state_dict,
            output_dir=args.output,
            threshold=args.threshold,
            source=args.input,
        )
        print(f"Exported {len(manifest.tensors)} tensors to {args.output}")
        return

    if args.command == "export-hf":
        manifest = export_checkpoint_to_ternary(
            args.input,
            output_dir=args.output,
            threshold=args.threshold,
        )
        print(f"Exported {len(manifest.tensors)} tensors to {args.output}")
        return

    if args.command == "inspect-artifact":
        summary = inspect_artifact(args.output)
        print(
            json.dumps(
                {
                    "source": summary.manifest.source,
                    "format_version": summary.manifest.format_version,
                    "total_tensors": summary.total_tensors,
                    "total_trits": summary.total_trits,
                    "counts": summary.counts,
                    "payload_ok": summary.per_tensor_payload_ok,
                },
                indent=2,
            )
        )
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
