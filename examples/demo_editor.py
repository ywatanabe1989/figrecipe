#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-23 15:10:00 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/demo_editor.py


"""Demo script for GUI editor with ALL supported plot types."""

# Force Agg backend BEFORE any matplotlib import to avoid Tkinter threading issues
import matplotlib

matplotlib.use("Agg")

import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "src")

import figrecipe as fr  # noqa: E402

output_path = Path(os.path.dirname(__file__))


def kill_port(port=5050):
    # Kill port first
    subprocess.run(
        f"fuser -k {port}/tcp 2>/dev/null || lsof -ti :{port} | xargs -r kill -9",
        shell=True,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    # Verify port is free
    result = subprocess.run(f"lsof -i :{port}", shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"Warning: Port {port} still in use, killing again...")
        subprocess.run(
            f"lsof -ti :{port} | xargs kill -9",
            shell=True,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)


def plot_figure():
    """Create a figure with ALL supported plot types using the registry."""
    from figrecipe._dev.demo_plotters import create_all_plots_figure

    # Create figure with all plots
    fig, axes, results = create_all_plots_figure(fr)

    # Report results
    successes = sum(1 for r in results.values() if r["success"])
    failures = sum(1 for r in results.values() if not r["success"])
    print(f"Plotted {successes}/{len(results)} plot types successfully")
    if failures > 0:
        print("Failed plots:")
        for name, r in results.items():
            if not r["success"]:
                print(f"  - {name}: {r['error']}")

    return fig


def main():
    kill_port()

    # Load SCITEX style FIRST
    fr.load_style("SCITEX")

    # Plot figure with all types
    fig = plot_figure()

    # Save and validate
    fr.save(fig, output_path / "figrecipe_test.png", validate_error_level="warning")

    # Reproduce
    fig, axes = fr.reproduce(output_path / "figrecipe_test.yaml")

    print("Launching editor on port 5050...")
    fr.edit(fig, open_browser=True, port=5050)


if __name__ == "__main__":
    main()

# EOF
