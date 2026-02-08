"""End-to-end HF checkpoint export to ternary artifacts."""

from __future__ import annotations

import importlib.util
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import numpy as np
import numpy.typing as npt

from t81_python.quantization import pack_trits, quantize_float_to_trits, unpack_trits


@dataclass(frozen=True)
class TensorExportSummary:
    name: str
    shape: list[int]
    numel: int
    threshold: float
    counts: dict[str, int]
    payload_file: str


@dataclass(frozen=True)
class ExportManifest:
    generated_at_utc: str
    format_version: str
    source: str
    threshold: float
    tensors: list[TensorExportSummary]


@dataclass(frozen=True)
class ArtifactInspection:
    manifest: ExportManifest
    total_tensors: int
    total_trits: int
    counts: dict[str, int]
    per_tensor_payload_ok: dict[str, bool]


def _to_numpy(value: Any) -> npt.NDArray[np.float32]:
    if hasattr(value, "detach") and hasattr(value, "cpu") and hasattr(value, "numpy"):
        arr = np.asarray(value.detach().cpu().numpy(), dtype=np.float32)
        return cast(npt.NDArray[np.float32], arr)
    arr = np.asarray(value, dtype=np.float32)
    return cast(npt.NDArray[np.float32], arr)


def export_state_dict_to_ternary(
    state_dict: dict[str, Any],
    output_dir: str | Path,
    *,
    threshold: float = 0.05,
    source: str = "in_memory",
) -> ExportManifest:
    """Export tensor-like state dict items into packed ternary artifacts + JSON manifest."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tensor_summaries: list[TensorExportSummary] = []
    for name, value in state_dict.items():
        arr = _to_numpy(value)
        flattened = arr.reshape(-1)
        trits = quantize_float_to_trits(flattened.tolist(), threshold=threshold)

        ints = trits.to_ints()
        counts = {
            "-1": sum(1 for v in ints if v == -1),
            "0": sum(1 for v in ints if v == 0),
            "+1": sum(1 for v in ints if v == 1),
        }

        safe_name = name.replace("/", "_").replace(".", "_")
        payload_file = f"{safe_name}.t81bin"
        payload_path = out_dir / payload_file
        payload_path.write_bytes(pack_trits(ints))

        tensor_summaries.append(
            TensorExportSummary(
                name=name,
                shape=list(arr.shape),
                numel=int(flattened.size),
                threshold=threshold,
                counts=counts,
                payload_file=payload_file,
            )
        )

    manifest = ExportManifest(
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        format_version="0.1",
        source=source,
        threshold=threshold,
        tensors=tensor_summaries,
    )
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "generated_at_utc": manifest.generated_at_utc,
                "format_version": manifest.format_version,
                "source": manifest.source,
                "threshold": manifest.threshold,
                "tensors": [asdict(t) for t in manifest.tensors],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def load_json_state_dict(path: str | Path) -> dict[str, Any]:
    """Load a JSON mapping of tensor names to nested numeric arrays."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Expected top-level JSON object mapping tensor names to values")
    return payload


def _normalize_loaded_checkpoint(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        nested = payload.get("state_dict")
        if isinstance(nested, dict):
            return nested
        return payload
    raise ValueError("Checkpoint loader returned non-dict payload")


def load_checkpoint_state_dict(path: str | Path) -> dict[str, Any]:
    """Load a checkpoint from .safetensors or .pt/.pth into a state-dict mapping."""
    checkpoint = Path(path)
    suffix = checkpoint.suffix.lower()

    if suffix == ".safetensors":
        if importlib.util.find_spec("safetensors") is None:
            raise RuntimeError(
                "Missing dependency: safetensors. Install with `pip install -e '.[hf]'`."
            )
        from safetensors import safe_open

        framework = "pt" if importlib.util.find_spec("torch") is not None else "np"
        state_dict: dict[str, Any] = {}
        with safe_open(str(checkpoint), framework=framework, device="cpu") as handle:
            for key in handle.keys():
                state_dict[key] = handle.get_tensor(key)
        return state_dict

    if suffix in {".pt", ".pth", ".bin"}:
        if importlib.util.find_spec("torch") is None:
            raise RuntimeError("Missing dependency: torch. Install with `pip install -e '.[hf]'`.")
        import torch

        loaded = torch.load(str(checkpoint), map_location="cpu")
        return _normalize_loaded_checkpoint(loaded)

    raise ValueError(
        f"Unsupported checkpoint format: {suffix}. Expected .safetensors, .pt, .pth, or .bin"
    )


def export_checkpoint_to_ternary(
    checkpoint_path: str | Path,
    output_dir: str | Path,
    *,
    threshold: float = 0.05,
) -> ExportManifest:
    """Load a checkpoint file and export packed ternary artifacts."""
    state_dict = load_checkpoint_state_dict(checkpoint_path)
    return export_state_dict_to_ternary(
        state_dict,
        output_dir=output_dir,
        threshold=threshold,
        source=str(checkpoint_path),
    )


def read_manifest(path: str | Path) -> ExportManifest:
    """Read a JSON manifest file into typed structures."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    tensors: list[TensorExportSummary] = []
    for row in payload["tensors"]:
        tensors.append(
            TensorExportSummary(
                name=row["name"],
                shape=[int(x) for x in row["shape"]],
                numel=int(row["numel"]),
                threshold=float(row["threshold"]),
                counts={
                    "-1": int(row["counts"]["-1"]),
                    "0": int(row["counts"]["0"]),
                    "+1": int(row["counts"]["+1"]),
                },
                payload_file=row["payload_file"],
            )
        )
    return ExportManifest(
        generated_at_utc=str(payload["generated_at_utc"]),
        format_version=str(payload["format_version"]),
        source=str(payload["source"]),
        threshold=float(payload["threshold"]),
        tensors=tensors,
    )


def inspect_artifact(output_dir: str | Path) -> ArtifactInspection:
    """Validate payload decode lengths and summarize aggregate trit counts."""
    out_dir = Path(output_dir)
    manifest = read_manifest(out_dir / "manifest.json")

    total_trits = 0
    counts = {"-1": 0, "0": 0, "+1": 0}
    per_tensor_payload_ok: dict[str, bool] = {}

    for tensor in manifest.tensors:
        total_trits += tensor.numel
        counts["-1"] += tensor.counts["-1"]
        counts["0"] += tensor.counts["0"]
        counts["+1"] += tensor.counts["+1"]

        payload = (out_dir / tensor.payload_file).read_bytes()
        decoded = unpack_trits(payload, count=tensor.numel)
        decoded_counts = {
            "-1": sum(1 for value in decoded.values if int(value) == -1),
            "0": sum(1 for value in decoded.values if int(value) == 0),
            "+1": sum(1 for value in decoded.values if int(value) == 1),
        }
        per_tensor_payload_ok[tensor.name] = decoded_counts == tensor.counts

    return ArtifactInspection(
        manifest=manifest,
        total_tensors=len(manifest.tensors),
        total_trits=total_trits,
        counts=counts,
        per_tensor_payload_ok=per_tensor_payload_ok,
    )
