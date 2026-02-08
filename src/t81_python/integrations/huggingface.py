"""Hugging Face adapter helpers."""

from __future__ import annotations

import importlib.util
from typing import Any

import numpy as np

from ..quantization import quantize_float_to_trits


def is_available() -> bool:
    return (
        importlib.util.find_spec("torch") is not None
        and importlib.util.find_spec("transformers") is not None
    )


def quantize_state_dict(
    state_dict: dict[str, Any],
    *,
    threshold: float = 0.05,
) -> dict[str, list[int]]:
    """Quantize tensor-like state dict entries into plain trit arrays."""
    quantized: dict[str, list[int]] = {}
    for key, value in state_dict.items():
        if hasattr(value, "detach") and hasattr(value, "cpu") and hasattr(value, "numpy"):
            arr = value.detach().cpu().numpy()
        else:
            arr = np.asarray(value)
        trits = quantize_float_to_trits(arr.ravel().tolist(), threshold=threshold)
        quantized[key] = trits.to_ints()
    return quantized
