"""ctypes bridge for the t81-vm C API."""

from __future__ import annotations

import ctypes
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class VMTraceEntry:
    pc: int
    opcode: int
    trap: Optional[int]


class _CTraceEntry(ctypes.Structure):
    _fields_ = [
        ("pc", ctypes.c_size_t),
        ("opcode", ctypes.c_uint8),
        ("trap", ctypes.c_int),
    ]


def default_vm_lib_paths(workspace_root: Optional[Path] = None) -> list[Path]:
    root = workspace_root if workspace_root is not None else Path(__file__).resolve().parents[3]
    return [
        root / "t81-vm/build/libt81vm_capi.dylib",
        root / "t81-vm/build/libt81vm_capi.so",
    ]


class VMBridge:
    """Minimal runtime bridge for loading and executing T81VM programs."""

    def __init__(self, lib_path: Optional[Path] = None) -> None:
        path = self._resolve_lib_path(lib_path)
        self._lib = ctypes.CDLL(str(path))

        self._lib.t81vm_create.restype = ctypes.c_void_p
        self._lib.t81vm_destroy.argtypes = [ctypes.c_void_p]
        self._lib.t81vm_load_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self._lib.t81vm_load_file.restype = ctypes.c_int
        self._lib.t81vm_run_to_halt.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        self._lib.t81vm_run_to_halt.restype = ctypes.c_int
        self._lib.t81vm_state_hash.argtypes = [ctypes.c_void_p]
        self._lib.t81vm_state_hash.restype = ctypes.c_uint64
        self._lib.t81vm_register.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        self._lib.t81vm_register.restype = ctypes.c_int64
        self._lib.t81vm_trace_len.argtypes = [ctypes.c_void_p]
        self._lib.t81vm_trace_len.restype = ctypes.c_size_t
        self._lib.t81vm_trace_get.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(_CTraceEntry)]
        self._lib.t81vm_trace_get.restype = ctypes.c_int

        handle = self._lib.t81vm_create()
        if handle == 0:
            raise RuntimeError("failed to create t81vm handle")
        self._handle = ctypes.c_void_p(handle)

    @staticmethod
    def _resolve_lib_path(explicit: Optional[Path]) -> Path:
        if explicit is not None:
            if not explicit.exists():
                raise FileNotFoundError(f"t81-vm library not found: {explicit}")
            return explicit

        env = os.environ.get("T81_VM_LIB")
        if env:
            p = Path(env)
            if not p.exists():
                raise FileNotFoundError(f"T81_VM_LIB points to missing file: {p}")
            return p

        for candidate in default_vm_lib_paths():
            if candidate.exists():
                return candidate
        raise FileNotFoundError("unable to locate t81-vm C API library")

    def close(self) -> None:
        if getattr(self, "_handle", None):
            self._lib.t81vm_destroy(self._handle)
            self._handle = ctypes.c_void_p()

    def __del__(self) -> None:
        self.close()

    def load_file(self, path: Path) -> None:
        status = self._lib.t81vm_load_file(self._handle, str(path).encode("utf-8"))
        if status != 0:
            raise RuntimeError(f"t81vm_load_file failed with status={status}")

    def run_to_halt(self, max_steps: int = 100_000) -> int:
        return int(self._lib.t81vm_run_to_halt(self._handle, max_steps))

    def state_hash(self) -> int:
        return int(self._lib.t81vm_state_hash(self._handle))

    def register(self, index: int) -> int:
        return int(self._lib.t81vm_register(self._handle, index))

    def trace(self) -> list[VMTraceEntry]:
        count = int(self._lib.t81vm_trace_len(self._handle))
        out: list[VMTraceEntry] = []
        for i in range(count):
            c_entry = _CTraceEntry()
            status = int(self._lib.t81vm_trace_get(self._handle, i, ctypes.byref(c_entry)))
            if status != 0:
                raise RuntimeError(f"t81vm_trace_get failed with status={status} index={i}")
            out.append(
                VMTraceEntry(
                    pc=int(c_entry.pc),
                    opcode=int(c_entry.opcode),
                    trap=None if c_entry.trap < 0 else int(c_entry.trap),
                )
            )
        return out
