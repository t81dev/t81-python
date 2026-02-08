#!/usr/bin/env python3
"""Validate t81-python assumptions against the canonical VM contract."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

REQUIRED_FORMATS = {"TextV1", "TiscJsonV1"}
REQUIRED_HOST_ABI_NAME = "t81vm-c-api"
REQUIRED_TRACE_FORMAT = "trace-v1"


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    vm_dir = Path(os.environ.get("T81_VM_DIR", str((root / "../t81-vm").resolve())))
    local_contract_path = root / "contracts/runtime-contract.json"
    if not local_contract_path.exists():
        raise SystemExit(f"Missing local runtime contract marker: {local_contract_path}")
    contract_path = vm_dir / "docs/contracts/vm-compatibility.json"
    if not contract_path.exists():
        raise SystemExit(f"Missing VM contract file: {contract_path}")

    local_contract = json.loads(local_contract_path.read_text(encoding="utf-8"))
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    vm_contract_version = str(contract.get("contract_version", "")).strip()
    expected_contract_version = str(local_contract.get("contract_version", "")).strip()
    if vm_contract_version != expected_contract_version:
        raise SystemExit(
            "VM contract version mismatch: "
            f"vm={vm_contract_version!r} local={expected_contract_version!r}"
        )

    lane = os.environ.get("VM_COMPAT_LANE", "").strip().lower()
    if lane == "pinned":
        expected_pin = str(local_contract.get("vm_main_pin", "")).strip()
        if not expected_pin:
            raise SystemExit("Pinned lane requires vm_main_pin in contracts/runtime-contract.json")
        vm_head = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=vm_dir, text=True).strip()
        )
        if vm_head != expected_pin:
            raise SystemExit(
                "Pinned lane VM commit mismatch: "
                f"vm={vm_head} expected={expected_pin}"
            )

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
