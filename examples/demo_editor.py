#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-24 07:32:26 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/demo_editor.py


"""Demo script for GUI editor with diverse plot types (subset).

For ALL plot types, see demo_editor_full.py

Usage:
    python demo_editor.py [PORT]
    python demo_editor.py 5051
"""

import matplotlib

matplotlib.use("Agg")

import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")

import figrecipe as fr
from figrecipe._dev.demo_plotters import get_representative_plots

output_path = Path(os.path.dirname(__file__))

# Use representative plots from each category (one per category)
SELECTED_PLOTTERS = get_representative_plots()
# Result: ['plot', 'scatter', 'bar', 'hist', 'imshow', 'contourf', 'specgram', 'quiver', 'pie']


def kill_port(port=5050):
    subprocess.run(
        f"fuser -k {port}/tcp 2>/dev/null || lsof -ti :{port} | xargs -r kill -9",
        shell=True,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    result = subprocess.run(f"lsof -i :{port}", shell=True, capture_output=True)
    if result.returncode == 0:
        subprocess.run(
            f"lsof -ti :{port} | xargs kill -9",
            shell=True,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)


def plot_figure():
    """Create a figure with diverse plot types."""
    from figrecipe._dev import get_plotter

    rng = np.random.default_rng(42)

    # Calculate grid size (3x4 for 12 plots)
    n_plots = len(SELECTED_PLOTTERS)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols

    # Let SCITEX style compute figure size (40x28mm per axis)
    fig, axes = fr.subplots(n_rows, n_cols)
    axes = axes.flatten()

    results = {}
    for idx, name in enumerate(SELECTED_PLOTTERS):
        ax = axes[idx]
        try:
            plotter = get_plotter(name)
            plotter(fr, rng, ax=ax)
            # Title already set by plotter with method name
            results[name] = {"success": True, "error": None}
        except Exception as e:
            ax.set_title(f"{name} (failed)")
            ax.text(0.5, 0.5, str(e)[:50], ha="center", va="center", fontsize=8)
            results[name] = {"success": False, "error": str(e)}

    # Hide unused axes
    for idx in range(n_plots, len(axes)):
        axes[idx].set_visible(False)

    # Report
    successes = sum(1 for r in results.values() if r["success"])
    print(f"Plotted {successes}/{len(results)} plot types successfully")
    if successes < len(results):
        for name, r in results.items():
            if not r["success"]:
                print(f"  - {name}: {r['error']}")

    return fig


def main(port=5050):
    kill_port(port)

    fr.load_style("SCITEX")

    fig = plot_figure()

    # validate_error_level="warning" needed as some plots have non-deterministic elements
    fr.save(fig, output_path / "demo_editor.png", validate_error_level="warning")

    fig, axes = fr.reproduce(output_path / "demo_editor.yaml")

    print(f"Launching editor on port {port}...")
    fr.edit(fig, host="0.0.0.0", port=port)  # 0.0.0.0 for WSL2-to-Windows access


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5050
    main(port)

# EOF
