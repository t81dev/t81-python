from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "t81_python.cli", *args],
        check=True,
        text=True,
        capture_output=True,
    )


def test_cli_export_and_inspect(tmp_path: Path) -> None:
    input_json = tmp_path / "state.json"
    out_dir = tmp_path / "out"
    input_json.write_text(json.dumps({"w": [0.1, -0.2, 0.0, 0.06]}), encoding="utf-8")

    export = _run_cli("export-hf-json", str(input_json), str(out_dir), "--threshold", "0.05")
    assert "Exported 1 tensors" in export.stdout

    inspect = _run_cli("inspect-artifact", str(out_dir))
    payload = json.loads(inspect.stdout)
    assert payload["total_tensors"] == 1
    assert payload["payload_ok"]["w"] is True


def test_cli_export_hf_safetensors_and_inspect(tmp_path: Path) -> None:
    if importlib.util.find_spec("safetensors") is None:
        return
    from safetensors.numpy import save_file

    checkpoint = tmp_path / "weights.safetensors"
    out_dir = tmp_path / "out"
    save_file(
        {"layer.weight": np.asarray([0.2, -0.3, 0.0, 0.07], dtype=np.float32)},
        str(checkpoint),
    )

    export = _run_cli("export-hf", str(checkpoint), str(out_dir), "--threshold", "0.05")
    assert "Exported 1 tensors" in export.stdout

    inspect = _run_cli("inspect-artifact", str(out_dir))
    payload = json.loads(inspect.stdout)
    assert payload["total_tensors"] == 1
    assert payload["payload_ok"]["layer.weight"] is True
