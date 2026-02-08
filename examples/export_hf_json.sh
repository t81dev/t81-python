#!/usr/bin/env bash
set -euo pipefail

t81-python export-hf-json examples/hf_state_dict.json ./out-ternary --threshold 0.05
cat ./out-ternary/manifest.json
