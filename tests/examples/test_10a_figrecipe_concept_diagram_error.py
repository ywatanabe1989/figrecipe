"""Compile-only smoke for examples/10a_figrecipe_concept_diagram_error.py (PS303)."""

import subprocess
import sys
from pathlib import Path

EXAMPLE = (
    Path(__file__).resolve().parents[2]
    / "examples"
    / "10a_figrecipe_concept_diagram_error.py"
)


def test_exists():
    assert EXAMPLE.exists(), f"missing example: {EXAMPLE}"


def test_compiles():
    subprocess.run([sys.executable, "-m", "py_compile", str(EXAMPLE)], check=True)
