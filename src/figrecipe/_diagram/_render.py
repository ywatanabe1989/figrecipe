#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-01-24
# File: figrecipe/_diagram/_render.py

"""
Render diagrams to image files (PNG, SVG, PDF).

Supports multiple backends:
- mermaid-cli (mmdc): Best quality, requires Node.js
- graphviz (dot): Good for DOT format, requires graphviz
- mermaid.ink: Online API, no installation needed
"""

import base64
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._diagram import Diagram


def _check_mermaid_cli() -> bool:
    """Check if mermaid-cli (mmdc) is available."""
    return shutil.which("mmdc") is not None


def _check_graphviz() -> bool:
    """Check if graphviz (dot) is available."""
    return shutil.which("dot") is not None


def _render_with_mermaid_cli(
    mermaid_content: str,
    output_path: Path,
    format: str,
    scale: float,
) -> Path:
    """Render using mermaid-cli (mmdc)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
        f.write(mermaid_content)
        mmd_path = f.name

    try:
        cmd = [
            "mmdc",
            "-i",
            mmd_path,
            "-o",
            str(output_path),
            "-s",
            str(scale),
            "-b",
            "transparent",
        ]
        if format == "pdf":
            cmd.extend(["-e", "pdf"])

        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    finally:
        Path(mmd_path).unlink(missing_ok=True)


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


def _render_with_mermaid_ink(
    mermaid_content: str,
    output_path: Path,
    format: str,
) -> Path:
    """Render using mermaid.ink online API."""
    # Encode the Mermaid content
    encoded = base64.urlsafe_b64encode(mermaid_content.encode()).decode()

    # Build URL
    if format == "svg":
        url = f"https://mermaid.ink/svg/{encoded}"
    else:
        url = f"https://mermaid.ink/img/{encoded}"

    # Download the image
    with urllib.request.urlopen(url, timeout=30) as response:
        content = response.read()

    output_path.write_bytes(content)
    return output_path


def render_diagram(
    diagram: "Diagram",
    path,
    format: str = "png",
    backend: str = "auto",
    scale: float = 2.0,
) -> Path:
    """
    Render a diagram to an image file.

    Parameters
    ----------
    diagram : Diagram
        The diagram to render.
    path : str or Path
        Output file path.
    format : str
        Output format: png, svg, pdf.
    backend : str
        Rendering backend: 'mermaid-cli', 'graphviz', 'mermaid.ink', 'auto'.
    scale : float
        Scale factor for output.

    Returns
    -------
    Path
        Path to the rendered file.
    """
    output_path = Path(path)
    format = format.lower()

    # Auto-detect backend
    if backend == "auto":
        if _check_mermaid_cli():
            backend = "mermaid-cli"
        elif _check_graphviz():
            backend = "graphviz"
        else:
            backend = "mermaid.ink"

    # Render based on backend
    if backend == "mermaid-cli":
        if not _check_mermaid_cli():
            raise RuntimeError(
                "mermaid-cli (mmdc) not found. Install with: npm install -g @mermaid-js/mermaid-cli"
            )
        mermaid_content = diagram.to_mermaid()
        return _render_with_mermaid_cli(mermaid_content, output_path, format, scale)

    elif backend == "graphviz":
        if not _check_graphviz():
            raise RuntimeError(
                "graphviz (dot) not found. Install with: apt install graphviz"
            )
        dot_content = diagram.to_graphviz()
        return _render_with_graphviz(dot_content, output_path, format)

    elif backend == "mermaid.ink":
        if format == "pdf":
            raise ValueError("mermaid.ink does not support PDF format")
        mermaid_content = diagram.to_mermaid()
        return _render_with_mermaid_ink(mermaid_content, output_path, format)

    else:
        raise ValueError(f"Unknown backend: {backend}")


def get_available_backends() -> dict:
    """Get available rendering backends and their status."""
    return {
        "mermaid-cli": {
            "available": _check_mermaid_cli(),
            "install": "npm install -g @mermaid-js/mermaid-cli",
            "formats": ["png", "svg", "pdf"],
        },
        "graphviz": {
            "available": _check_graphviz(),
            "install": "apt install graphviz",
            "formats": ["png", "svg", "pdf"],
        },
        "mermaid.ink": {
            "available": True,  # Always available (online)
            "install": "No installation needed (online API)",
            "formats": ["png", "svg"],
        },
    }
