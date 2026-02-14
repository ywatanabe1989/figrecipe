#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mermaid rendering backends."""

import base64
import shutil
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path


def _check_mermaid_cli() -> bool:
    """Check if mermaid-cli (mmdc) is available."""
    return shutil.which("mmdc") is not None


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


__all__ = ["_check_mermaid_cli", "_render_with_mermaid_cli", "_render_with_mermaid_ink"]
