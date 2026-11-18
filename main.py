#!/usr/bin/env python3
"""Copy the front page image to the output directory.

The entry image is pre-rendered by generate_frontpage.py and shipped in
this repo as frontpage.png. This program places a copy at
/output/entry.png, or $MAKEFUN_OUTPUT_DIR/entry.png when that variable
is set. Standard library only; no network use.
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "frontpage.png"


def main():
    """Write the shipped front page to <output dir>/entry.png."""
    if not SOURCE.is_file():
        raise SystemExit(f"missing entry image: {SOURCE}")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(SOURCE, dest)
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
