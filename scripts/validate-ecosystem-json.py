#!/usr/bin/env python3
"""Validate ecosystem.json against schemas/ecosystem.schema.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("error: jsonschema is not installed. Install dev deps: pip install -e '.[dev]'")
        return 2

    schema_path = Path("schemas/ecosystem.schema.json")
    data_path = Path("ecosystem.json")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    data = json.loads(data_path.read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda item: list(item.path))
    if errors:
        print("ecosystem.json validation failed:")
        for err in errors:
            path = ".".join(str(part) for part in err.path) or "<root>"
            print(f"- {path}: {err.message}")
        return 1

    print("ecosystem.json validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
