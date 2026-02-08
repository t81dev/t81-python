"""Benchmark export throughput and compression for synthetic checkpoint tensors."""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

from t81_python.pipelines import export_state_dict_to_ternary, inspect_artifact


def make_state_dict(tensors: int, values_per_tensor: int, seed: int) -> dict[str, list[float]]:
    rng = random.Random(seed)
    out: dict[str, list[float]] = {}
    for idx in range(tensors):
        out[f"layer_{idx}.weight"] = [rng.uniform(-1.0, 1.0) for _ in range(values_per_tensor)]
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tensors", type=int, default=32)
    parser.add_argument("--values-per-tensor", type=int, default=4096)
    parser.add_argument("--threshold", type=float, default=0.05)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", type=Path, default=Path("benchmark-out"))
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    state_dict = make_state_dict(args.tensors, args.values_per_tensor, args.seed)
    float_bytes = sum(len(values) for values in state_dict.values()) * 4

    start = time.perf_counter()
    export_state_dict_to_ternary(
        state_dict,
        output_dir=args.output,
        threshold=args.threshold,
        source="benchmark_synthetic",
    )
    elapsed = time.perf_counter() - start

    inspection = inspect_artifact(args.output)
    payload_bytes = sum(
        (args.output / tensor.payload_file).stat().st_size for tensor in inspection.manifest.tensors
    )

    report = {
        "tensors": args.tensors,
        "values_per_tensor": args.values_per_tensor,
        "threshold": args.threshold,
        "elapsed_seconds": round(elapsed, 6),
        "values_per_second": int((args.tensors * args.values_per_tensor) / max(elapsed, 1e-9)),
        "float32_bytes": float_bytes,
        "ternary_payload_bytes": payload_bytes,
        "compression_ratio": round(float_bytes / max(payload_bytes, 1), 4),
        "counts": inspection.counts,
    }

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
