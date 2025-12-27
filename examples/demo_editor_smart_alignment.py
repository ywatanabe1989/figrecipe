#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-27 17:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/demo_editor_smart_alignment.py

"""Demo script for GUI editor with Smart Alignment feature.

Demonstrates:
- 2x2 multi-panel figure with diverse plot types
- Smart Align button to align panels automatically
- Dark mode toggle with preserved background color
- SCITEX style with proper dimensions
"""

import matplotlib

matplotlib.use("Agg")

import subprocess
import sys
import time

import numpy as np

sys.path.insert(0, "src")

import figrecipe as fr


def kill_port(port=8080):
    """Kill any process using the specified port."""
    subprocess.run(
        f"fuser -k {port}/tcp 2>/dev/null || lsof -ti :{port} | xargs -r kill -9",
        shell=True,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)


def create_demo_figure():
    """Create a 2x2 figure with diverse plot types for alignment demo."""
    # Use SCITEX default dimensions (40x28mm per axes)
    fig, axes = fr.subplots(2, 2)

    x = np.linspace(0, 2 * np.pi, 100)

    # Top-left: Line plot (Sine)
    axes[0, 0].plot(x, np.sin(x))
    axes[0, 0].set_title("Sine")
    axes[0, 0].set_xlabel("x")
    axes[0, 0].set_ylabel("y")

    # Top-right: Line plot (Cosine)
    axes[0, 1].plot(x, np.cos(x))
    axes[0, 1].set_title("Cosine")
    axes[0, 1].set_xlabel("x")
    axes[0, 1].set_ylabel("y")

    # Bottom-left: Bar chart
    categories = ["A", "B", "C", "D"]
    values = [2.5, 1.2, 1.8, 2.2]
    axes[1, 0].bar(categories, values)
    axes[1, 0].set_title("Bar")
    axes[1, 0].set_xlabel("Category")
    axes[1, 0].set_ylabel("Value")

    # Bottom-right: Scatter plot
    np.random.seed(42)
    x_scatter = np.random.rand(20) * 4
    y_scatter = x_scatter + np.random.randn(20) * 0.5
    axes[1, 1].scatter(x_scatter, y_scatter)
    axes[1, 1].set_title("Scatter")
    axes[1, 1].set_xlabel("x")
    axes[1, 1].set_ylabel("y")

    return fig


def main():
    """Main entry point."""
    port = 8080

    # Kill any existing process on port
    kill_port(port)

    # Load SCITEX style for publication-quality figures
    fr.load_style("SCITEX")

    # Create demo figure
    fig = create_demo_figure()

    print("=" * 60)
    print("Smart Alignment Demo")
    print("=" * 60)
    print()
    print("Features to try in the editor:")
    print("  1. Click 'Smart' button to auto-align all panels")
    print("  2. Toggle 'Dark Mode' to see dark theme with solid background")
    print("  3. Use alignment buttons to align selected panels")
    print("  4. Use distribute buttons for even spacing")
    print()
    print(f"Launching editor at http://127.0.0.1:{port}")
    print("(Use 0.0.0.0 for WSL2-to-Windows access)")
    print()

    # Launch editor (0.0.0.0 for WSL2 access from Windows browser)
    fr.edit(fig, port=port, host="0.0.0.0")


if __name__ == "__main__":
    main()

# EOF
