#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate SCITEX style anatomy diagram showing all configurable elements.

Similar to matplotlib's "Anatomy of a figure" but focused on SCITEX style settings,
with multiple plot types for visual appeal.
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import numpy as np

import figrecipe as fr

OUTPUT_DIR = Path(__file__).parent / "03_style_anatomy_out"

# SCITEX color palette
COLORS = [
    "#0080C0",  # blue
    "#FF4632",  # red
    "#14B414",  # green
    "#E6A014",  # yellow
    "#C832FF",  # purple
    "#14C8C8",  # lightblue
    "#E45E32",  # orange
    "#FF96C8",  # pink
]


def add_annotation(ax, text, xy, xytext, fontsize=6, color="#0080C0"):
    """Add annotation with arrow pointing to element."""
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        fontsize=fontsize,
        color=color,
        ha="center",
        va="center",
        arrowprops=dict(
            arrowstyle="-", color=color, lw=0.5, connectionstyle="arc3,rad=0"
        ),
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            edgecolor=color,
            linewidth=0.5,
            alpha=0.9,
        ),
    )


def main():
    """Create SCITEX style anatomy diagram with multiple plot types."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load SCITEX style
    fr.load_style("SCITEX")

    # Create 2x3 subplot figure with SCITEX default dimensions (40x28mm)
    fig, axes = fr.subplots(
        nrows=2,
        ncols=3,
        axes_width_mm=40,
        axes_height_mm=28,
        margin_left_mm=15,
        margin_right_mm=30,
        margin_bottom_mm=15,
        margin_top_mm=12,
    )

    # Flatten for easier access
    ax_line, ax_scatter, ax_bar = axes[0]
    ax_box, ax_violin, ax_hist = axes[1]

    np.random.seed(42)

    # === Panel A: Line plot with error bands ===
    x = np.linspace(0, 4, 50)
    y1 = np.sin(x * 1.5) + 1
    y2 = np.cos(x * 1.5) + 1
    ax_line.plot(x, y1, label="sin(x)", linewidth=1.5, color=COLORS[0])
    ax_line.plot(x, y2, label="cos(x)", linewidth=1.5, color=COLORS[1])
    ax_line.fill_between(x, y1 - 0.2, y1 + 0.2, alpha=0.3, color=COLORS[0])
    ax_line.set_xlabel("Time")
    ax_line.set_ylabel("Signal")
    ax_line.set_title("Line Plot")
    ax_line.legend(loc="upper right", fontsize=5)

    # === Panel B: Scatter plot ===
    n = 40
    x_scatter = np.random.randn(n)
    y_scatter = x_scatter * 0.8 + np.random.randn(n) * 0.5
    ax_scatter.scatter(x_scatter, y_scatter, s=25, color=COLORS[0], label="Data")
    ax_scatter.set_xlabel("X value")
    ax_scatter.set_ylabel("Y value")
    ax_scatter.set_title("Scatter Plot")
    ax_scatter.legend(loc="upper right", fontsize=5)

    # === Panel C: Bar plot with stat annotations ===
    categories = ["A", "B", "C", "D"]
    values = [3.2, 4.5, 2.8, 5.1]
    errors = [0.3, 0.4, 0.2, 0.5]
    ax_bar.bar(categories, values, yerr=errors, capsize=3, color=COLORS[:4])
    ax_bar.set_xlabel("Category")
    ax_bar.set_ylabel("Value")
    ax_bar.set_title("Bar Plot")

    # Add statistical annotation brackets
    from figrecipe._wrappers._stat_annotation import draw_stat_annotation

    draw_stat_annotation(ax_bar, 0, 1, text="**", p_value=0.005, style="stars")
    draw_stat_annotation(ax_bar, 2, 3, text="*", p_value=0.02, style="stars")

    # === Panel D: Box plot with categorical x-axis ===
    box_categories = ["Ctrl", "Exp1", "Exp2", "Exp3"]
    data_box = [np.random.randn(30) + i for i in range(4)]
    bp = ax_box.boxplot(data_box, patch_artist=True, tick_labels=box_categories)
    for i, (patch, color) in enumerate(zip(bp["boxes"], COLORS[:4])):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
        patch.set_label(box_categories[i] if i == 0 else None)
    ax_box.set_xlabel("Group")
    ax_box.set_ylabel("Value")
    ax_box.set_title("Box Plot")

    # Add stat annotation
    draw_stat_annotation(ax_box, 1, 2, text="***", p_value=0.0005, style="stars")

    # === Panel E: Violin plot with categorical x-axis ===
    violin_categories = ["G1", "G2", "G3"]
    data_violin = [np.random.randn(50) * (i + 1) * 0.5 for i in range(3)]
    parts = ax_violin.violinplot(data_violin, showmeans=False, showmedians=True)
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(COLORS[i])
        pc.set_alpha(0.7)
    ax_violin.set_xticks([1, 2, 3])
    ax_violin.set_xticklabels(violin_categories)
    ax_violin.set_xlabel("Group")
    ax_violin.set_ylabel("Distribution")
    ax_violin.set_title("Violin Plot")

    # === Panel F: Histogram ===
    data_hist = np.random.randn(500)
    ax_hist.hist(
        data_hist,
        bins=20,
        edgecolor="black",
        linewidth=0.5,
        alpha=0.7,
        color=COLORS[0],
        label="Sample",
    )
    ax_hist.set_xlabel("Value")
    ax_hist.set_ylabel("Count")
    ax_hist.set_title("Histogram")
    ax_hist.legend(loc="upper right", fontsize=5)

    # Add figure-level title
    fig.suptitle("SCITEX Style Anatomy", fontsize=10, fontweight="bold")

    # === Add annotation overlay ===
    fig_ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    fig_ax.set_xlim(0, 1)
    fig_ax.set_ylim(0, 1)
    fig_ax.axis("off")

    ann_color = "#0080C0"
    dim_color = "#E74C3C"

    # Style annotations
    add_annotation(
        fig_ax, "title_pt: 8", xy=(0.20, 0.90), xytext=(0.03, 0.96), color=ann_color
    )
    add_annotation(
        fig_ax, "suptitle_pt: 9", xy=(0.50, 0.96), xytext=(0.75, 0.98), color=ann_color
    )
    add_annotation(
        fig_ax,
        "axis_label_pt: 7",
        xy=(0.18, 0.58),
        xytext=(0.02, 0.70),
        color=ann_color,
    )
    add_annotation(
        fig_ax,
        "tick_label_pt: 7",
        xy=(0.10, 0.52),
        xytext=(0.02, 0.40),
        color=ann_color,
    )
    add_annotation(
        fig_ax,
        "legend_pt: 6\nframeon: false",
        xy=(0.32, 0.85),
        xytext=(0.40, 0.96),
        color=ann_color,
    )
    add_annotation(
        fig_ax, "trace_mm: 0.2", xy=(0.22, 0.75), xytext=(0.02, 0.85), color=ann_color
    )
    add_annotation(
        fig_ax, "scatter_mm: 0.8", xy=(0.52, 0.75), xytext=(0.55, 0.96), color=ann_color
    )
    add_annotation(
        fig_ax,
        "stat_annotation\nbracket + stars",
        xy=(0.72, 0.85),
        xytext=(0.92, 0.92),
        color=ann_color,
    )
    add_annotation(
        fig_ax,
        "boxplot.line_mm: 0.2",
        xy=(0.22, 0.30),
        xytext=(0.02, 0.18),
        color=ann_color,
    )
    add_annotation(
        fig_ax,
        "violin.alpha: 0.7",
        xy=(0.52, 0.28),
        xytext=(0.55, 0.10),
        color=ann_color,
    )
    add_annotation(
        fig_ax,
        "histogram.edge_mm: 0.2",
        xy=(0.82, 0.30),
        xytext=(0.92, 0.18),
        color=ann_color,
    )
    add_annotation(
        fig_ax,
        "spine_mm: 0.2",
        xy=(0.78, 0.58),
        xytext=(0.92, 0.65),
        color=ann_color,
    )

    # Dimension annotations (SCITEX default: 40x28mm)
    fig_ax.text(
        0.98,
        0.50,
        "axes:\n  width_mm: 40\n  height_mm: 28",
        fontsize=5,
        ha="right",
        va="center",
        color=dim_color,
        bbox=dict(boxstyle="round", facecolor="white", edgecolor=dim_color, alpha=0.9),
    )

    # Color palette
    for i, c in enumerate(COLORS[:8]):
        rect = matplotlib.patches.Rectangle(
            (0.85 + (i % 4) * 0.035, 0.02 + (i // 4) * 0.035),
            0.03,
            0.03,
            facecolor=c,
            edgecolor="none",
            transform=fig_ax.transAxes,
        )
        fig_ax.add_patch(rect)
    fig_ax.text(0.92, 0.09, "color palette", fontsize=5, ha="center", color="#666666")

    # Save
    output_path = OUTPUT_DIR / "scitex_anatomy.png"
    fr.save(fig, output_path, verbose=True, validate=False)

    print(f"\nSaved anatomy diagram to: {output_path}")
    return output_path


if __name__ == "__main__":
    main()
