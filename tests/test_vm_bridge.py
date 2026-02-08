import json
import os
import subprocess
from pathlib import Path

import pytest

from t81_python.vm_bridge import VMBridge, default_vm_lib_paths


def test_default_vm_lib_paths_include_workspace_candidate() -> None:
    candidates = default_vm_lib_paths(Path("/tmp/workspace"))
    assert candidates
    assert str(candidates[0]).endswith("t81-vm/build/libt81vm_capi.dylib")


def test_vm_bridge_explicit_missing_library_raises() -> None:
    with pytest.raises(FileNotFoundError):
        VMBridge(Path("/definitely/missing/libt81vm_capi.so"))


def test_vm_bridge_runtime_canary_when_library_present() -> None:
    vm_lib = os.environ.get("T81_VM_LIB")
    vm_program = os.environ.get("T81_VM_CANARY_PROGRAM")
    if not vm_lib or not vm_program:
        pytest.skip("runtime canary env vars not set")
    assert vm_lib is not None
    assert vm_program is not None

    env = os.environ.copy()
    env["T81_VM_LIB"] = vm_lib
    result = subprocess.run(
        ["python3", "scripts/run_vm_canary.py", vm_program],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "vm canary: ok" in result.stdout


def test_vm_bridge_parity_p0_opcode_canary_when_library_present(tmp_path: Path) -> None:
    if os.environ.get("T81_VM_ENABLE_PARITY_P0_CANARY") != "1":
        pytest.skip("parity p0 canary not enabled for this lane")

    vm_lib = os.environ.get("T81_VM_LIB")
    if not vm_lib:
        pytest.skip("runtime library env var not set")
    assert vm_lib is not None

    program = {
        "insns": [
            {"opcode": "LoadImm", "a": 0, "b": 7, "c": 0},
            {"opcode": "LoadImm", "a": 1, "b": 3, "c": 0},
            {"opcode": "Less", "a": 2, "b": 1, "c": 0},
            {"opcode": "I2F", "a": 3, "b": 0, "c": 0},
            {"opcode": "F2I", "a": 4, "b": 3, "c": 0},
            {"opcode": "I2Frac", "a": 5, "b": 4, "c": 0},
            {"opcode": "Frac2I", "a": 6, "b": 5, "c": 0},
            {"opcode": "Halt", "a": 0, "b": 0, "c": 0},
        ]
    }
    program_path = tmp_path / "parity_p0_canary.tisc.json"
    program_path.write_text(json.dumps(program), encoding="utf-8")

    bridge = VMBridge(Path(vm_lib))
    bridge.load_file(program_path)
    status = bridge.run_to_halt()
    assert status == 0
    assert bridge.register(2) == 1
    assert bridge.register(4) == 7
    assert bridge.register(6) == 7
