#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared render dispatch for diagrams."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._graph import Diagram


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
    from .._graphviz._render import _check_graphviz, _render_with_graphviz
    from .._mermaid._render import (
        _check_mermaid_cli,
        _render_with_mermaid_cli,
        _render_with_mermaid_ink,
    )

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
    from .._graphviz._render import _check_graphviz
    from .._mermaid._render import _check_mermaid_cli

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


__all__ = ["render_diagram", "get_available_backends"]
