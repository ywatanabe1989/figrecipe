"""Compile-only smoke for examples/11_complete_figure.py (PS303)."""

import subprocess
import sys
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "11_complete_figure.py"


def test_exists():
    assert EXAMPLE.exists(), f"missing example: {EXAMPLE}"


def test_compiles():
    subprocess.run([sys.executable, "-m", "py_compile", str(EXAMPLE)], check=True)
