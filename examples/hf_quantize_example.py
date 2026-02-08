"""Minimal Hugging Face style weight quantization example."""

from __future__ import annotations

from t81_python.integrations.huggingface import quantize_state_dict


def main() -> None:
    mock_state = {
        "layer.weight": [0.22, -0.51, 0.00, 0.04, 0.90],
        "layer.bias": [0.01, -0.20],
    }
    trits = quantize_state_dict(mock_state, threshold=0.05)
    print(trits)


if __name__ == "__main__":
    main()
