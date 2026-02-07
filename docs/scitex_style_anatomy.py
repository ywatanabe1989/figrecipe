#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-07 19:53:04 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/docs/scitex_style_anatomy.py


"""Generate SCITEX style anatomy diagram showing all configurable elements.

Outputs:
    docs/scitex_style_anatomy.jpg
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import numpy as np
import scitex as stx

import figrecipe as fr

OUTPUT_DIR = Path(__file__).parent

PALETTE = [
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


@stx.session
def main(CONFIG=stx.session.INJECTED, logger=stx.session.INJECTED):
    """Create SCITEX style anatomy diagram with multiple plot types."""
    fr.load_style("SCITEX")

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

    ax_line, ax_scatter, ax_bar = axes[0]
    ax_box, ax_hist, ax_pie = axes[1]

    np.random.seed(42)

    # === Panel A: Line plot with error bands ===
    x = np.linspace(0, 4, 50)
    y1 = np.sin(x * 1.5) + 1
    y2 = np.cos(x * 1.5) + 1
    ax_line.plot(x, y1, label="sin(x)", linewidth=1.5, color=PALETTE[0])
    ax_line.plot(x, y2, label="cos(x)", linewidth=1.5, color=PALETTE[1])
    ax_line.fill_between(x, y1 - 0.15, y1 + 0.15, alpha=0.2, color=PALETTE[0])
    ax_line.set_xlabel("Time")
    ax_line.set_ylabel("Signal")
    ax_line.set_title("Line Plot")
    ax_line.legend(loc="upper right", fontsize=5)

    # === Panel B: Scatter plot ===
    n = 40
    x_scatter = np.random.randn(n)
    y_scatter = x_scatter * 0.8 + np.random.randn(n) * 0.5
    ax_scatter.scatter(x_scatter, y_scatter, s=25, color=PALETTE[0], label="Data")
    ax_scatter.set_xlabel("X value")
    ax_scatter.set_ylabel("Y value")
    ax_scatter.set_title("Scatter Plot")
    ax_scatter.legend(loc="upper right", fontsize=5)

    # === Panel C: Bar plot with stat annotations ===
    categories = ["A", "B", "C", "D"]
    values = [3.2, 4.5, 2.8, 5.1]
    errors = [0.3, 0.4, 0.2, 0.5]
    ax_bar.bar(categories, values, yerr=errors, capsize=3, color=PALETTE[:4])
    ax_bar.set_xlabel("Category")
    ax_bar.set_ylabel("Value")
    ax_bar.set_title("Bar Plot")

    from figrecipe._wrappers._stat_annotation import draw_stat_annotation

    draw_stat_annotation(ax_bar, 0, 1, text="**", p_value=0.005, style="stars")
    draw_stat_annotation(ax_bar, 2, 3, text="*", p_value=0.02, style="stars")

    # === Panel D: Box plot ===
    box_categories = ["Ctrl", "Exp1", "Exp2", "Exp3"]
    data_box = [np.random.randn(30) + i for i in range(4)]
    bp = ax_box.boxplot(data_box, patch_artist=True, tick_labels=box_categories)
    for i, (patch, color) in enumerate(zip(bp["boxes"], PALETTE[:4])):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax_box.set_xlabel("Group")
    ax_box.set_ylabel("Value")
    ax_box.set_title("Box Plot")

    draw_stat_annotation(ax_box, 1, 2, text="***", p_value=0.0005, style="stars")

    # === Panel E: Pie chart (SCITEX color palette) ===
    names = [
        "blue",
        "red",
        "green",
        "yellow",
        "purple",
        "cyan",
        "orange",
        "pink",
    ]
    rgbs = [
        f"({int(c[1:3], 16)},{int(c[3:5], 16)},{int(c[5:7], 16)})" for c in PALETTE[:8]
    ]
    labels = [f"{n}\n{r}" for n, r in zip(names, rgbs)]
    result = ax_pie.pie(
        [1] * 8,
        colors=PALETTE[:8],
        labels=labels,
        labeldistance=1.3,
        startangle=90,
        counterclock=False,
        textprops={"fontsize": 4.5},
    )
    texts = result[1]
    for txt, c in zip(texts, PALETTE[:8]):
        txt.set_color(c)
        txt.set_fontweight("bold")
    ax_pie.set_title("SCITEX Colors")

    # === Panel F: Histogram ===
    data_hist = np.random.randn(500)
    ax_hist.hist(
        data_hist,
        bins=20,
        edgecolor="black",
        linewidth=0.5,
        alpha=0.7,
        color=PALETTE[0],
        label="Sample",
    )
    ax_hist.set_xlabel("Value")
    ax_hist.set_ylabel("Count")
    ax_hist.set_title("Histogram")
    ax_hist.legend(loc="upper right", fontsize=5)

    fig.suptitle("SCITEX Style Anatomy", fontsize=10, fontweight="bold")

    # === Annotation overlay ===
    fig_ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    fig_ax.set_xlim(0, 1)
    fig_ax.set_ylim(0, 1)
    fig_ax.axis("off")

    ann_color = "#0080C0"
    dim_color = "#E74C3C"

    add_annotation(
        fig_ax,
        "title_pt: 8",
        xy=(0.20, 0.90),
        xytext=(0.03, 0.96),
        color=ann_color,
    )
    add_annotation(
        fig_ax,
        "suptitle_pt: 9",
        xy=(0.50, 0.96),
        xytext=(0.75, 0.98),
        color=ann_color,
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
        fig_ax,
        "trace_mm: 0.12",
        xy=(0.22, 0.75),
        xytext=(0.02, 0.85),
        color=ann_color,
    )
    add_annotation(
        fig_ax,
        "scatter_mm: 0.8",
        xy=(0.52, 0.75),
        xytext=(0.55, 0.96),
        color=ann_color,
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

    out = Path(CONFIG.SDIR_OUT) if CONFIG else OUTPUT_DIR
    output_path = out / "scitex_style_anatomy.jpg"
    fr.save(fig, output_path, verbose=True, validate=False)
    print(f"\nSaved: {output_path}")
    return output_path


if __name__ == "__main__":
    main()

# EOF
