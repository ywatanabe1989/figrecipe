#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pure Mermaid rendering — delegate to mermaid-cli or mermaid.ink."""

import warnings
from pathlib import Path

from ._diagram._render import (
    _check_mermaid_cli,
    _render_with_mermaid_cli,
    _render_with_mermaid_ink,
)


class Mermaid:
    """Render Mermaid diagram code to image files.

    Parameters
    ----------
    code : str
        Raw Mermaid diagram code.

    Examples
    --------
    >>> m = Mermaid("graph TD; A-->B;")
    >>> m.render("output.png")
    """

    def __init__(self, code: str):
        self.code = code.strip()

    def render(self, output, format="png", scale=2.0, backend="auto"):
        """Render to image file.

        Parameters
        ----------
        output : str or Path
            Output file path.
        format : str
            Output format: 'png', 'svg', 'pdf'.
        scale : float
            Scale factor (mermaid-cli only).
        backend : str
            'auto', 'mermaid-cli', or 'mermaid.ink'.

        Returns
        -------
        Path
            Path to rendered file.
        """
        output_path = Path(output)
        format = format.lower()

        if backend == "auto":
            if _check_mermaid_cli():
                backend = "mermaid-cli"
            else:
                backend = "mermaid.ink"
                warnings.warn(
                    "mermaid-cli (mmdc) not found, falling back to mermaid.ink online API",
                    stacklevel=2,
                )

        if backend == "mermaid-cli":
            if not _check_mermaid_cli():
                raise RuntimeError(
                    "mermaid-cli (mmdc) not found. Install with: npm install -g @mermaid-js/mermaid-cli"
                )
            return _render_with_mermaid_cli(self.code, output_path, format, scale)

        elif backend == "mermaid.ink":
            if format == "pdf":
                raise ValueError("mermaid.ink does not support PDF format")
            return _render_with_mermaid_ink(self.code, output_path, format)

        else:
            raise ValueError(f"Unknown backend: {backend}")

    @staticmethod
    def is_available():
        """Check if mermaid-cli (mmdc) is installed."""
        return _check_mermaid_cli()

    def __repr__(self):
        return f"Mermaid({len(self.code)} chars)"
