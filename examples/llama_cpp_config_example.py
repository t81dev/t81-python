"""Build kwargs for llama_cpp.Llama."""

from __future__ import annotations

from t81_python.integrations.llama_cpp import build_model_kwargs


def main() -> None:
    kwargs = build_model_kwargs(
        model_path="/models/model.gguf",
        n_ctx=8192,
        n_threads=8,
        use_mlock=True,
    )
    print(kwargs)


if __name__ == "__main__":
    main()
