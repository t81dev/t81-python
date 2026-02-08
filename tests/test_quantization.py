import numpy as np

from t81_python.quantization import (
    dequantize_trits,
    pack_trits,
    quantize_float_to_trits,
    unpack_trits,
)


def test_quantize_thresholding() -> None:
    trits = quantize_float_to_trits([-0.2, -0.01, 0.0, 0.02, 0.3], threshold=0.05)
    assert trits.to_ints() == [-1, 0, 0, 0, 1]


def test_pack_unpack_roundtrip() -> None:
    values = [-1, 0, 1, -1, 1, 0, 0]
    packed = pack_trits(values)
    decoded = unpack_trits(packed, count=len(values))
    assert decoded.to_ints() == values


def test_dequantize_scale() -> None:
    arr = dequantize_trits([-1, 0, 1], scale=0.5)
    assert np.allclose(arr, np.array([-0.5, 0.0, 0.5], dtype=np.float32))
