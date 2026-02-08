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
