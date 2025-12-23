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
    # constrained_layout=True comes from SCITEX style for proper sup* label positioning
    # 3x3 grid to show all plot types
    fig, axes = fr.subplots(nrows=3, ncols=3)

    axes_flat = axes.flatten()

    x = np.linspace(0, 10, 100)
    np.random.seed(42)

    # Panel labels (A, B, C, ...)
    panel_labels = "ABCDEFGHI"

    ## Axis 0: Lines + Scatters
    axes_flat[0].plot(x, np.sin(x), label="line1")
    axes_flat[0].plot(x, np.cos(x), label="line2")
    axes_flat[0].scatter(x[::15], np.sin(x[::15]) + 0.2, label="scatter1")
    axes_flat[0].scatter(x[::15], np.cos(x[::15]) + 0.2, label="scatter2")
    axes_flat[0].set_title("Lines + Scatters")
    axes_flat[0].set_xlabel("Time (s)")
    axes_flat[0].set_ylabel("Amplitude")
    axes_flat[0].legend(fontsize=5)

    ## Axis 1: Bar Plot
    axes_flat[1].bar(["A", "B", "C", "D"], [2, 3, 5, 4])
    axes_flat[1].set_title("Bar Plot")
    axes_flat[1].set_xlabel("Category")
    axes_flat[1].set_ylabel("Value")

    ## Axis 2: Histogram
    axes_flat[2].hist(np.random.randn(500), bins=20, edgecolor="black")
    axes_flat[2].set_title("Histogram")
    axes_flat[2].set_xlabel("Value")
    axes_flat[2].set_ylabel("Count")

    ## Axis 3: Box Plot
    axes_flat[3].boxplot([np.random.randn(50) for _ in range(4)], id="bp1")
    axes_flat[3].set_title("Box Plot")
    axes_flat[3].set_xlabel("Group")
    axes_flat[3].set_ylabel("Distribution")

    ## Axis 4: Violin Plot
    axes_flat[4].violinplot([np.random.randn(50) for _ in range(4)], id="vp1")
    axes_flat[4].set_title("Violin Plot")
    axes_flat[4].set_xlabel("Group")
    axes_flat[4].set_ylabel("Distribution")

    ## Axis 5: Errorbar
    x_err = np.arange(5)
    y_err = [2, 3, 5, 4, 3]
    yerr = [0.5, 0.3, 0.8, 0.4, 0.6]
    axes_flat[5].errorbar(x_err, y_err, yerr=yerr, fmt="o-", capsize=3)
    axes_flat[5].set_title("Errorbar")
    axes_flat[5].set_xlabel("X")
    axes_flat[5].set_ylabel("Y")

    ## Axis 6: Fill Between
    axes_flat[6].fill_between(x, np.sin(x) - 0.3, np.sin(x) + 0.3, alpha=0.3)
    axes_flat[6].plot(x, np.sin(x))
    axes_flat[6].set_title("Fill Between")
    axes_flat[6].set_xlabel("X")
    axes_flat[6].set_ylabel("Y")

    ## Axis 7: Heatmap (imshow)
    data = np.random.rand(5, 5)
    axes_flat[7].imshow(data, cmap="viridis", aspect="auto")
    axes_flat[7].set_title("Heatmap")
    axes_flat[7].set_xlabel("X")
    axes_flat[7].set_ylabel("Y")

    ## Axis 8: Step Plot
    x_step = np.arange(10)
    y_step = np.random.randint(1, 6, 10)
    axes_flat[8].step(x_step, y_step, where="mid")
    axes_flat[8].set_title("Step Plot")
    axes_flat[8].set_xlabel("X")
    axes_flat[8].set_ylabel("Y")

    # Add panel labels (A, B, C, ...) to each axes
    for i, ax in enumerate(axes_flat):
        fr.panel_label(ax, panel_labels[i])

    # Figure-level labels (fontsize comes from style automatically)
    fig.suptitle("Demo: All Plot Types")
    fig.supxlabel("Common X-axis Label")
    fig.supylabel("Common Y-axis Label")

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
