#!/usr/bin/env python3
"""Deliver the LUMARIS travel poster to /output/entry.png.

The poster is pre-rendered in this repository as entry.png (see render.py,
which draws it from scratch with Pillow). This program copies it to
$MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png when unset) and verifies
the copy byte for byte, so a bad copy can never pass as the entry.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
EXPECTED_SHA256 = "21b2c1c1b25dabe63adb3bf518f1f52f976594311e84b18d8a29f5c5461757e3"
MAX_BYTES = 1_048_576


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "entry.png"

    if not SOURCE.exists():
        # Fallback: render the poster on the spot (deterministic).
        import render
        render.main()

    shutil.copyfile(SOURCE, out)
    data = out.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    print(f"wrote {out} {len(data)} bytes sha256={digest}")
    if len(data) > MAX_BYTES:
        print(f"error: entry.png is {len(data)} bytes, over the 1 MiB cap",
              file=sys.stderr)
        return 1
    if EXPECTED_SHA256 != "PLACEHOLDER" and digest != EXPECTED_SHA256:
        print("error: entry.png does not match the shipped render",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
