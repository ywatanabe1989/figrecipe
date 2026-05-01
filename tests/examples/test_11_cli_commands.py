"""Syntax-only smoke for examples/11_cli_commands.sh (PS303)."""

import subprocess
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "11_cli_commands.sh"


def test_exists():
    assert EXAMPLE.exists(), f"missing example: {EXAMPLE}"


def test_bash_syntax():
    subprocess.run(["bash", "-n", str(EXAMPLE)], check=True)
