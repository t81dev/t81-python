# Benchmarks

Use the synthetic benchmark to estimate export throughput and payload compression:

```bash
python benchmarks/benchmark_export.py --tensors 32 --values-per-tensor 4096 --threshold 0.05
```

Output JSON includes:

- elapsed seconds
- values per second
- float32 input bytes vs ternary payload bytes
- compression ratio
- aggregate trit counts

For reproducibility, keep `--seed` fixed when comparing changes.
