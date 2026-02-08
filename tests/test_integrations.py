from t81_python.integrations import hf_available, llama_cpp_available
from t81_python.integrations.huggingface import quantize_state_dict
from t81_python.integrations.llama_cpp import build_model_kwargs


def test_integration_availability_checks_return_bool() -> None:
    assert isinstance(hf_available(), bool)
    assert isinstance(llama_cpp_available(), bool)


def test_hf_quantize_state_dict_basic() -> None:
    data = {"weight": [0.1, -0.2, 0.0]}
    out = quantize_state_dict(data, threshold=0.05)
    assert out["weight"] == [1, -1, 0]


def test_build_model_kwargs() -> None:
    kwargs = build_model_kwargs(model_path="model.gguf", n_ctx=8192, n_threads=8)
    assert kwargs["model_path"] == "model.gguf"
    assert kwargs["n_ctx"] == 8192
    assert kwargs["n_threads"] == 8
