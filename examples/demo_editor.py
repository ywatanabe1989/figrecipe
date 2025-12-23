#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-23 11:45:04 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/demo_editor.py


"""Test script for GUI editor with color cycle demo."""

# Force Agg backend BEFORE any matplotlib import to avoid Tkinter threading issues
import matplotlib

matplotlib.use("Agg")

import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np  # noqa: E402

import figrecipe as fr  # noqa: E402

sys.path.insert(0, "src")

output_path = Path(os.path.dirname(__file__))


def kill_port(port=5050):
    # Kill port 5050 first
    subprocess.run(
        "fuser -k 5050/tcp 2>/dev/null || lsof -ti :5050 | xargs -r kill -9",
        shell=True,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    # Verify port is free
    result = subprocess.run("lsof -i :5050", shell=True, capture_output=True)
    if result.returncode == 0:
        print("Warning: Port 5050 still in use, killing again...")
        subprocess.run(
            "lsof -ti :5050 | xargs kill -9",
            shell=True,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(1)


def plot_figure():
    fig, axes = fr.subplots(nrows=2, ncols=2)

    axes_flat = axes.flatten()

    x = np.linspace(0, 10, 100)

    # Color cycle demo: 2 lines + 3 scatters (no explicit s= to use SCITEX default 0.8mm)

    ## Axis 0
    axes_flat[0].plot(x, np.sin(x), label="line1")
    axes_flat[0].plot(x, np.cos(x), label="line2")
    axes_flat[0].scatter(x[::15], np.sin(x[::15]) + 0.2, label="scatter1")
    axes_flat[0].scatter(x[::15], np.cos(x[::15]) + 0.2, label="scatter2")
    axes_flat[0].scatter(x[::15], np.sin(x[::15]) - 0.2, label="scatter3")
    axes_flat[0].set_title("2 Lines + 3 Scatters")
    axes_flat[0].legend(fontsize=5)

    ## Axis 1
    axes_flat[1].bar(["A", "B", "C", "D"], [2, 3, 5, 4])
    axes_flat[1].set_title("Bar Plot")

    ## Axis 2
    axes_flat[2].boxplot(
        [np.random.randn(50) for _ in range(4)],
        id="bp1",
    )
    axes_flat[2].set_title("Box Plot")

    ## Axis 3
    axes_flat[3].violinplot([np.random.randn(50) for _ in range(4)], id="vp1")
    axes_flat[3].set_title("Violin Plot")

    return fig


def main():
    kill_port()

    # Load SCITEX style FIRST
    fr.load_style("SCITEX")

    # Plot figure
    fig = plot_figure()

    fr.save(fig, output_path / "figrecipe_test.png")

    # fig.savefig(output_path / "figrecipe_test.png") # This should show Saved: ... as well
    fig, axes = fr.reproduce(output_path / "figrecipe_test.png")
    # fig, axes = fr.reproduce(output_path / "figrecipe_test.yaml")

    # __import__("ipdb").set_trace()
    print("Launching editor on port 5050...")
    fr.edit(fig, open_browser=True, port=5050)

    # fr.edit(fig, open_browser=True, port=5050)
    # fr.edit(output_path / "figrecipe_test.yaml", open_browser=True, port=5050)


if __name__ == "__main__":
    main()

# EOF
