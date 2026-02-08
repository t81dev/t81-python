import importlib.util
import json
from pathlib import Path

import numpy as np

from t81_python.pipelines import (
    export_checkpoint_to_ternary,
    export_state_dict_to_ternary,
    inspect_artifact,
    load_checkpoint_state_dict,
    load_json_state_dict,
)


def test_export_state_dict_to_ternary(tmp_path: Path) -> None:
    state_dict = {
        "layer.weight": [[0.5, -0.1], [0.0, 0.06]],
        "layer.bias": [0.01, -0.2],
    }

    manifest = export_state_dict_to_ternary(state_dict, tmp_path, threshold=0.05, source="test")

    assert manifest.source == "test"
    assert len(manifest.tensors) == 2

    manifest_path = tmp_path / "manifest.json"
    assert manifest_path.exists()

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["format_version"] == "0.1"
    assert len(payload["tensors"]) == 2


def test_load_json_state_dict(tmp_path: Path) -> None:
    payload = {"x": [0.1, -0.1, 0.0]}
    path = tmp_path / "state.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    loaded = load_json_state_dict(path)
    assert loaded == payload


def test_inspect_artifact(tmp_path: Path) -> None:
    state_dict = {"layer.weight": [0.5, -0.1, 0.0, 0.06]}
    export_state_dict_to_ternary(state_dict, tmp_path, threshold=0.05, source="test")

    summary = inspect_artifact(tmp_path)
    assert summary.total_tensors == 1
    assert summary.total_trits == 4
    assert summary.per_tensor_payload_ok["layer.weight"] is True


def test_load_checkpoint_state_dict_invalid_extension(tmp_path: Path) -> None:
    path = tmp_path / "checkpoint.unknown"
    path.write_text("x", encoding="utf-8")
    try:
        load_checkpoint_state_dict(path)
    except ValueError as exc:
        assert "Unsupported checkpoint format" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported extension")


def test_load_checkpoint_state_dict_safetensors(tmp_path: Path) -> None:
    if importlib.util.find_spec("safetensors") is None:
        return
    from safetensors.numpy import save_file

    checkpoint = tmp_path / "weights.safetensors"
    payload = {
        "layer.weight": np.asarray([[0.1, -0.2], [0.0, 0.06]], dtype=np.float32),
        "layer.bias": np.asarray([0.01, -0.4], dtype=np.float32),
    }
    save_file(payload, str(checkpoint))

    state_dict = load_checkpoint_state_dict(checkpoint)
    assert set(state_dict.keys()) == {"layer.weight", "layer.bias"}


def test_export_checkpoint_to_ternary_safetensors(tmp_path: Path) -> None:
    if importlib.util.find_spec("safetensors") is None:
        return
    from safetensors.numpy import save_file

    checkpoint = tmp_path / "weights.safetensors"
    out_dir = tmp_path / "out"
    payload = {
        "layer.weight": np.asarray([[0.3, -0.2], [0.07, -0.01]], dtype=np.float32),
    }
    save_file(payload, str(checkpoint))

    manifest = export_checkpoint_to_ternary(checkpoint, out_dir, threshold=0.05)
    assert manifest.source.endswith("weights.safetensors")
    assert len(manifest.tensors) == 1

    summary = inspect_artifact(out_dir)
    assert summary.total_tensors == 1
    assert summary.per_tensor_payload_ok["layer.weight"] is True


def test_export_checkpoint_to_ternary_pt(tmp_path: Path) -> None:
    if importlib.util.find_spec("torch") is None:
        return
    import torch

    checkpoint = tmp_path / "weights.pt"
    out_dir = tmp_path / "out-pt"
    torch.save({"w": torch.tensor([0.4, -0.1, 0.0], dtype=torch.float32)}, checkpoint)

    manifest = export_checkpoint_to_ternary(checkpoint, out_dir, threshold=0.05)
    assert len(manifest.tensors) == 1
    assert manifest.tensors[0].name == "w"
