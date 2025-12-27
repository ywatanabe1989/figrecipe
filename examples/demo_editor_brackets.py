#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo script showing stat annotation brackets on various plot types."""

import sys
from pathlib import Path

# Add src to path when running from examples directory
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np

import figrecipe as fr

# Load SCITEX style
fr.load_style("SCITEX")

# Get SCITEX color palette from style cache
from figrecipe.styles._style_loader import _STYLE_CACHE


def rgb_to_hex(rgb):
    """Convert RGB list to hex color string."""
    return "#{:02x}{:02x}{:02x}".format(*rgb)


colors = [rgb_to_hex(c) for c in _STYLE_CACHE.colors.palette]

# Create demo figure with 2x2 layout (SCITEX calculates size automatically)
fig, axes = fr.subplots(2, 2)

np.random.seed(42)

# Panel A: Bar chart with brackets
control = np.random.normal(3.2, 0.8, 50)
treatment = np.random.normal(5.1, 0.9, 48)

axes[0, 0].bar(
    [0, 1],
    [control.mean(), treatment.mean()],
    yerr=[
        control.std() / np.sqrt(len(control)),
        treatment.std() / np.sqrt(len(treatment)),
    ],
    color=[colors[0], colors[1]],  # SCITEX blue, red
    capsize=5,
)
axes[0, 0].set_xticks([0, 1])
axes[0, 0].set_xticklabels(["Control", "Treatment"])
axes[0, 0].set_ylabel("Response")
axes[0, 0].set_title("(A) Bar Chart")
axes[0, 0].add_stat_annotation(0, 1, p_value=0.003, y=6.5)

# Panel B: Box plot with brackets
groups_box = [np.random.normal(m, 0.8, 40) for m in [3.0, 4.5, 3.2]]
bp = axes[0, 1].boxplot(groups_box, positions=[0, 1, 2], patch_artist=True)
colors_3 = [colors[0], colors[1], colors[2]]  # SCITEX blue, red, green
for patch, color in zip(bp["boxes"], colors_3):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
axes[0, 1].set_xticks([0, 1, 2])
axes[0, 1].set_xticklabels(["Group A", "Group B", "Group C"])
axes[0, 1].set_ylabel("Value")
axes[0, 1].set_title("(B) Box Plot")
# Multiple comparisons with stacked brackets
axes[0, 1].add_stat_annotation(0, 1, p_value=0.001, y=7.0)
axes[0, 1].add_stat_annotation(0, 2, p_value=0.45, y=7.8)
axes[0, 1].add_stat_annotation(1, 2, p_value=0.008, y=6.2)

# Panel C: Violin plot with brackets
groups_violin = [np.random.normal(m, 1.0, 60) for m in [2.5, 4.0, 3.8]]
vp = axes[1, 0].violinplot(groups_violin, positions=[0, 1, 2], showmeans=True)
for i, body in enumerate(vp["bodies"]):
    body.set_facecolor(colors_3[i])
    body.set_alpha(0.7)
axes[1, 0].set_xticks([0, 1, 2])
axes[1, 0].set_xticklabels(["Low", "Medium", "High"])
axes[1, 0].set_ylabel("Distribution")
axes[1, 0].set_title("(C) Violin Plot")
axes[1, 0].add_stat_annotation(
    0, 1, p_value=0.0005, style="both", y=7.5
)  # Show both stars and p-value
axes[1, 0].add_stat_annotation(
    1, 2, p_value=0.12, style="p_value", y=6.5
)  # Show p-value only

# Panel D: Scatter with group means and brackets
x_scatter = np.array([0] * 30 + [1] * 30 + [2] * 30)
y_scatter = np.concatenate(
    [
        np.random.normal(2.5, 0.5, 30),
        np.random.normal(4.2, 0.6, 30),
        np.random.normal(3.0, 0.5, 30),
    ]
)
colors_scatter = [colors_3[i] for i in x_scatter]
axes[1, 1].scatter(
    x_scatter + np.random.uniform(-0.15, 0.15, len(x_scatter)),
    y_scatter,
    c=colors_scatter,
    alpha=0.6,
    s=30,
)
# Add mean markers
for i, (m, c) in enumerate(zip([2.5, 4.2, 3.0], colors_3)):
    axes[1, 1].scatter([i], [m], c=c, s=150, marker="_", linewidths=3, zorder=5)
axes[1, 1].set_xticks([0, 1, 2])
axes[1, 1].set_xticklabels(["X", "Y", "Z"])
axes[1, 1].set_ylabel("Measurement")
axes[1, 1].set_title("(D) Scatter Plot")
axes[1, 1].add_stat_annotation(0, 1, p_value=0.0001, y=5.8)
axes[1, 1].add_stat_annotation(0, 2, p_value=0.03, y=5.2)

# Save figure
output_dir = Path(__file__).parent / "outputs"
output_dir.mkdir(exist_ok=True)
fig.savefig(output_dir / "demo_editor_brackets.png", dpi=150, verbose=True)

print(f"\nDemo complete! Check {output_dir / 'demo_editor_brackets.png'}")
