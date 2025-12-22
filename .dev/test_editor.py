#!/usr/bin/env python3
"""Test script for GUI editor with color cycle demo."""

import subprocess
import sys
import time

sys.path.insert(0, "src")

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
        "lsof -ti :5050 | xargs kill -9", shell=True, stderr=subprocess.DEVNULL
    )
    time.sleep(1)

import numpy as np  # noqa: E402

import figrecipe as fr  # noqa: E402

# Load SCITEX style FIRST
fr.load_style("SCITEX")

fig, axes = fr.subplots(nrows=2, ncols=2)

if hasattr(axes, "flatten"):
    axes_flat = axes.flatten()
elif isinstance(axes, list):
    axes_flat = (
        axes if not isinstance(axes[0], list) else [ax for row in axes for ax in row]
    )
else:
    axes_flat = [axes]

x = np.linspace(0, 10, 100)

# Color cycle demo: 2 lines + 3 scatters (no explicit s= to use SCITEX default 0.8mm)
axes_flat[0].plot(x, np.sin(x), label="line1")
axes_flat[0].plot(x, np.cos(x), label="line2")
axes_flat[0].scatter(x[::15], np.sin(x[::15]) + 0.2, label="scatter1")
axes_flat[0].scatter(x[::15], np.cos(x[::15]) + 0.2, label="scatter2")
axes_flat[0].scatter(x[::15], np.sin(x[::15]) - 0.2, label="scatter3")
axes_flat[0].set_title("2 Lines + 3 Scatters")
axes_flat[0].legend(fontsize=5)

axes_flat[1].bar(["A", "B", "C", "D"], [2, 3, 5, 4])
axes_flat[1].set_title("Bar Plot")

axes_flat[2].boxplot([np.random.randn(50) for _ in range(4)])
axes_flat[2].set_title("Box Plot")

axes_flat[3].violinplot([np.random.randn(50) for _ in range(4)])
axes_flat[3].set_title("Violin Plot")

print("Launching editor on port 5050...")
fr.edit(fig, open_browser=True, port=5050)
