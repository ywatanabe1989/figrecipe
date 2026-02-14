#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Graphviz rendering backend."""

import shutil
import subprocess
import tempfile
from pathlib import Path


def _check_graphviz() -> bool:
    """Check if graphviz (dot) is available."""
    return shutil.which("dot") is not None


def _render_with_graphviz(
    dot_content: str,
    output_path: Path,
    format: str,
) -> Path:
    """Render using graphviz (dot)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
        f.write(dot_content)
        dot_path = f.name

    try:
        format_arg = format if format != "png" else "png"
        cmd = ["dot", f"-T{format_arg}", dot_path, "-o", str(output_path)]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    finally:
        Path(dot_path).unlink(missing_ok=True)


__all__ = ["_check_graphviz", "_render_with_graphviz"]
