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
