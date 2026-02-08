"""Deterministic helpers for basic ternary quantization."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import numpy.typing as npt

from .core import Trit, TritVector

_TRIT_TO_PACKED = {-1: 0, 0: 1, 1: 2}
_PACKED_TO_TRIT = {0: -1, 1: 0, 2: 1}


def quantize_float_to_trits(values: Iterable[float], threshold: float = 0.05) -> TritVector:
    """Convert floats to {-1, 0, +1} with symmetric thresholding."""
    arr = np.asarray(list(values), dtype=np.float64)
    trits = np.where(arr > threshold, 1, np.where(arr < -threshold, -1, 0))
    return TritVector.from_ints(trits.tolist())


def dequantize_trits(values: Iterable[int | Trit], scale: float = 1.0) -> npt.NDArray[np.float32]:
    """Map trits back to float values using a scalar multiplier."""
    ints = np.asarray([int(v) for v in values], dtype=np.float32)
    out = np.asarray(ints * np.float32(scale), dtype=np.float32)
    return out


def pack_trits(values: Iterable[int | Trit]) -> bytes:
    """Pack trits into a compact byte stream using 2-bit symbols."""
    out = bytearray()
    current = 0
    shift = 0
    for raw in values:
        mapped = _TRIT_TO_PACKED[int(raw)]
        current |= (mapped & 0b11) << shift
        shift += 2
        if shift == 8:
            out.append(current)
            current = 0
            shift = 0
    if shift:
        out.append(current)
    return bytes(out)


def unpack_trits(payload: bytes, count: int) -> TritVector:
    """Decode a packed byte stream created by `pack_trits`."""
    out: list[int] = []
    for byte in payload:
        for shift in (0, 2, 4, 6):
            if len(out) >= count:
                return TritVector.from_ints(out)
            out.append(_PACKED_TO_TRIT[(byte >> shift) & 0b11])
    if len(out) != count:
        raise ValueError(f"Expected {count} trits, decoded {len(out)}")
    return TritVector.from_ints(out)
