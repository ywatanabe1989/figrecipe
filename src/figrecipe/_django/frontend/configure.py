#!/usr/bin/env python3
"""Configure figrecipe frontend build environment.

Creates a symlink from ./scitex-ui-types → scitex_ui's static directory,
so both TypeScript (tsconfig paths) and Vite (resolve.alias) can find
scitex-ui components from the pip-installed package.

Run once after install:
    python configure.py
"""

import os
import sys
from pathlib import Path

FRONTEND_DIR = Path(__file__).parent
LINK_NAME = FRONTEND_DIR / "scitex-ui-types"


def main() -> int:
    try:
        import scitex_ui

        static_dir = scitex_ui.get_static_dir()
    except ImportError:
        print("ERROR: scitex-ui is not installed.", file=sys.stderr)
        print("  pip install scitex-ui", file=sys.stderr)
        return 1

    if not static_dir.is_dir():
        print(f"ERROR: static dir not found: {static_dir}", file=sys.stderr)
        return 1

    # Remove stale symlink
    if LINK_NAME.is_symlink() or LINK_NAME.exists():
        LINK_NAME.unlink()

    os.symlink(str(static_dir), str(LINK_NAME))
    print(f"OK: {LINK_NAME.name} -> {static_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
