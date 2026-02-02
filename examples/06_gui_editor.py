#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo script for GUI editor with diverse plot types.

Usage:
    python 03_editor.py [PORT] [--all]
    python 03_editor.py 5051
    python 03_editor.py 5050 --all   # Launch with all plot types
"""

import matplotlib

matplotlib.use("Agg")

import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import figrecipe as fr
from figrecipe._dev.demo_plotters import get_representative_plots


def kill_port(port=5050):
    """Kill any process using the specified port."""
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


def plot_figure(all_plots=False):
    """Create a figure with diverse plot types.

    Parameters
    ----------
    all_plots : bool
        If True, show all available plot types. If False (default),
        show only representative plots (one per category).
    """
    from figrecipe._dev import get_plotter
    from figrecipe._dev.demo_plotters import list_plots

    rng = np.random.default_rng(42)

    # Use all plots or representative plots based on flag
    if all_plots:
        SELECTED_PLOTTERS = list_plots()
    else:
        SELECTED_PLOTTERS = get_representative_plots()

    # Calculate grid size
    n_plots = len(SELECTED_PLOTTERS)
    n_cols = 3
    n_rows = (n_plots + n_cols - 1) // n_cols

    fig, axes = fr.subplots(n_rows, n_cols)
    axes = axes.flatten()

    results = {}
    for idx, name in enumerate(SELECTED_PLOTTERS):
        ax = axes[idx]
        try:
            plotter = get_plotter(name)
            plotter(fr, rng, ax=ax)
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


def main(port=5050, all_plots=False):
    kill_port(port)

    fr.load_style("SCITEX")

    fig = plot_figure(all_plots=all_plots)

    # Save temporarily for reproduction
    output_dir = Path("/tmp/figrecipe_editor_demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "editor_demo.png"

    fr.save(fig, output_path, validate_error_level="warning")

    # Reproduce and launch editor
    fig, axes = fr.reproduce(output_path)

    print(f"\nLaunching editor on port {port}...")
    print(f"Open http://localhost:{port} in your browser")
    fr.edit(fig, host="0.0.0.0", port=port)


if __name__ == "__main__":
    # Parse arguments
    port = 5050
    all_plots = False

    for arg in sys.argv[1:]:
        if arg == "--all":
            all_plots = True
        elif arg.isdigit():
            port = int(arg)

    main(port, all_plots=all_plots)

# EOF
