#!/usr/bin/env python3
"""Run a VM canary artifact through the ctypes bridge."""

from __future__ import annotations

import sys
from pathlib import Path

from t81_python.vm_bridge import VMBridge


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_vm_canary.py <program.tisc.json>")

    program = Path(sys.argv[1]).resolve()
    bridge = VMBridge()
    bridge.load_file(program)
    status = bridge.run_to_halt()
    if status != 0:
        raise SystemExit(f"VM run failed with status={status}")

    if bridge.register(3) != 10:
        raise SystemExit(f"unexpected canary register result: r3={bridge.register(3)} expected=10")

    if bridge.state_hash() == 0:
        raise SystemExit("invalid state hash (0)")

    trace = bridge.trace()
    if not trace:
        raise SystemExit("empty trace")

    print("vm canary: ok")


if __name__ == "__main__":
    main()
