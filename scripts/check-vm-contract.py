#!/usr/bin/env python3
"""Validate t81-python assumptions against the canonical VM contract."""

from __future__ import annotations

import json
import os
from pathlib import Path


REQUIRED_FORMATS = {"TextV1", "TiscJsonV1"}
REQUIRED_HOST_ABI_NAME = "t81vm-c-api"
REQUIRED_TRACE_FORMAT = "trace-v1"


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    vm_dir = Path(os.environ.get("T81_VM_DIR", str((root / "../t81-vm").resolve())))
    contract_path = vm_dir / "docs/contracts/vm-compatibility.json"
    if not contract_path.exists():
        raise SystemExit(f"Missing VM contract file: {contract_path}")

    contract = json.loads(contract_path.read_text(encoding="utf-8"))

    host_abi = contract.get("host_abi", {})
    if host_abi.get("name") != REQUIRED_HOST_ABI_NAME:
        raise SystemExit(
            f"Unsupported VM ABI name: {host_abi.get('name')} (expected {REQUIRED_HOST_ABI_NAME})"
        )

    abi_version = str(host_abi.get("version", "")).strip()
    if not abi_version:
        raise SystemExit("VM ABI version is missing")

    formats = {entry.get("name") for entry in contract.get("accepted_program_formats", [])}
    missing_formats = sorted(REQUIRED_FORMATS - formats)
    if missing_formats:
        raise SystemExit(f"Missing required VM formats: {', '.join(missing_formats)}")

    trace_format = str(contract.get("trace_contract", {}).get("format_version", "")).strip()
    if trace_format != REQUIRED_TRACE_FORMAT:
        raise SystemExit(
            f"Unexpected trace format: {trace_format!r} (expected {REQUIRED_TRACE_FORMAT!r})"
        )

    opcodes = set(contract.get("supported_opcodes", []))
    for opcode in ("LoadImm", "Add", "Halt"):
        if opcode not in opcodes:
            raise SystemExit(f"Missing expected opcode used by canary assumptions: {opcode}")

    print(f"t81-python contract gate: ok (abi={abi_version})")


if __name__ == "__main__":
    main()
