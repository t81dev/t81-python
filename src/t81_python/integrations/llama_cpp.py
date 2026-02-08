"""llama.cpp-python adapter helpers."""

from __future__ import annotations

import importlib.util
from typing import Any


def is_available() -> bool:
    return importlib.util.find_spec("llama_cpp") is not None


def build_model_kwargs(
    *,
    model_path: str,
    n_ctx: int = 4096,
    n_threads: int | None = None,
    use_mlock: bool = False,
) -> dict[str, Any]:
    """Build validated kwargs for `llama_cpp.Llama`."""
    kwargs: dict[str, Any] = {
        "model_path": model_path,
        "n_ctx": n_ctx,
        "use_mlock": use_mlock,
    }
    if n_threads is not None:
        kwargs["n_threads"] = n_threads
    return kwargs
