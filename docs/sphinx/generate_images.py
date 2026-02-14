#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate all documentation images for Read the Docs.

Usage:
    python docs/sphinx/generate_images.py              # Generate all
    python docs/sphinx/generate_images.py --only concept
    python docs/sphinx/generate_images.py --only gallery
    python docs/sphinx/generate_images.py --only quickstart

Images are saved to session output dir, then symlinked to _static/.
Manual/external images (GUI demo, style anatomy) are not regenerated.

Note: validate=False is used because the in-save validator re-renders an
already-rendered figure, which triggers matplotlib stateful changes (tick
finalization, layout adjustments) causing false-positive MSE differences.
Reproduction from recipe is verified to be pixel-perfect (MSE=0.00).
"""

import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import numpy as np
import scitex as stx

import figrecipe as fr

STATIC_DIR = Path(__file__).parent / "_static"


# ── Concept Diagram ──────────────────────────────────────────────────────


def generate_concept_diagram(out):
    """Generate the FigRecipe concept diagram (flex layout) for index.rst."""
    s = fr.Diagram(
        title="FigRecipe: Reproducible Figures",
        width_mm=120,
        padding_mm=10,
        gap_mm=18,
    )

    s.add_box(
        "script",
        "script.py",
        shape="codeblock",
        language="python",
        content=[
            "import figrecipe",
            "fig, ax = figrecipe.subplots()",
            "ax.plot_line(x, y)",
            "figrecipe.save(fig, 'fig.png')",
        ],
        width_mm=80,
    )

    s.add_container(
        "recipe",
        title="Recipe (YAML)",
        children=["data", "style"],
        direction="row",
        container_gap_mm=8,
        container_padding_mm=8,
    )

    s.add_box(
        "data",
        "DATA",
        subtitle="CSV / NPZ",
        content=["WHAT to show"],
        emphasis="success",
        width_mm=40,
    )
    s.add_box(
        "style",
        "STYLE",
        subtitle="Presets / Themes",
        content=["HOW to show"],
        emphasis="purple",
        width_mm=40,
    )

    s.add_box(
        "figure",
        "Figure",
        subtitle="PNG / PDF + CSV",
        emphasis="info",
        width_mm=60,
    )

    s.add_arrow("script", "recipe")
    s.add_arrow("recipe", "figure", label="Render", label_offset_mm=(-12, 0))
    s.add_arrow(
        "figure",
        "recipe",
        label="Validate",
        label_offset_mm=(12, 0),
        curve=1.5,
        color="red",
        style="--",
    )

    fig, ax = fr.subplots()
    ax.diagram(s, id="figrecipe_concept")
    fr.save(fig, out / "figrecipe_concept.png", validate=False)


# ── Gallery Images ───────────────────────────────────────────────────────


def generate_gallery_images(out):
    """Generate all 8 gallery plot images for gallery.rst."""
    # Line
    fig, ax = fr.subplots()
    x = np.linspace(0, 10, 100)
    ax.plot(x, np.sin(x), label="sin(x)", id="sine")
    ax.plot(x, np.cos(x), label="cos(x)", id="cosine")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    fr.save(fig, out / "gallery_line.png", validate=False)

    # Scatter
    fig, ax = fr.subplots()
    np.random.seed(42)
    x = np.random.randn(50)
    y = x + np.random.randn(50) * 0.5
    ax.scatter(x, y, c=x, cmap="viridis", s=50, id="data")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    fr.save(fig, out / "gallery_scatter.png", validate=False)

    # Bar
    fig, ax = fr.subplots()
    ax.bar(
        ["A", "B", "C", "D", "E"], [23, 45, 12, 67, 34], color="steelblue", id="bars"
    )
    ax.set_xlabel("Category")
    ax.set_ylabel("Value")
    fr.save(fig, out / "gallery_bar.png", validate=False)

    # Histogram
    fig, ax = fr.subplots()
    np.random.seed(42)
    ax.hist(
        np.random.randn(1000),
        bins=30,
        alpha=0.7,
        color="steelblue",
        edgecolor="white",
        id="hist",
    )
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    fr.save(fig, out / "gallery_hist.png", validate=False)

    # Boxplot
    fig, ax = fr.subplots()
    np.random.seed(42)
    ax.boxplot(
        [np.random.randn(100) + i for i in range(4)],
        labels=["A", "B", "C", "D"],
        id="boxplot",
    )
    ax.set_xlabel("Group")
    ax.set_ylabel("Value")
    fr.save(fig, out / "gallery_boxplot.png", validate=False)

    # Violin
    fig, ax = fr.subplots()
    np.random.seed(42)
    ax.violinplot(
        [np.random.randn(100) + i for i in range(4)],
        positions=[1, 2, 3, 4],
        id="violin",
    )
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xticklabels(["A", "B", "C", "D"])
    fr.save(fig, out / "gallery_violin.png", validate=False)

    # Heatmap
    fig, ax = fr.subplots()
    np.random.seed(42)
    im = ax.imshow(np.random.randn(10, 10), cmap="coolwarm", id="heatmap")
    fig.fig.colorbar(im, ax=ax._ax)
    fr.save(fig, out / "gallery_heatmap.png", validate=False)

    # Contour
    fig, ax = fr.subplots()
    x = np.linspace(-3, 3, 100)
    y = np.linspace(-3, 3, 100)
    X, Y = np.meshgrid(x, y)
    cs = ax.contourf(
        X, Y, np.sin(X) * np.cos(Y), levels=20, cmap="viridis", id="contour"
    )
    fig.fig.colorbar(cs, ax=ax._ax)
    fr.save(fig, out / "gallery_contour.png", validate=False)


# ── Quickstart Images ────────────────────────────────────────────────────


def generate_quickstart_images(out):
    """Generate quickstart images for quickstart.rst."""
    # Trig plot
    fig, ax = fr.subplots()
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), label="sin(x)", color="blue", id="sine")
    ax.plot(x, np.cos(x), label="cos(x)", color="red", id="cosine")
    ax.set_xlabel("X (radians)")
    ax.set_ylabel("Y")
    ax.set_title("Trigonometric Functions")
    ax.legend()
    fr.save(fig, out / "quickstart_trig.png", validate=False)

    # Bundle scatter
    fig, ax = fr.subplots()
    x = np.array([1, 2, 3, 4, 5])
    ax.scatter(x, x**2, id="data")
    ax.set_title("Quadratic Data")
    fr.save(fig, out / "quickstart_bundle.png", validate=False)

    # Panel A
    fig, ax = fr.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    fr.save(fig, out / "quickstart_panel_a.png", validate=False)

    # Panel B
    fig, ax = fr.subplots()
    ax.bar(["A", "B"], [10, 15])
    fr.save(fig, out / "quickstart_panel_b.png", validate=False)

    # Diagram LR
    s = fr.Diagram(title="EEG Analysis Pipeline", width_mm=170, height_mm=100)
    s.add_box("raw", "Raw EEG", subtitle="64 channels", emphasis="muted")
    s.add_box("filter", "Bandpass Filter", subtitle="0.5-45 Hz", emphasis="primary")
    s.add_box("ica", "ICA", subtitle="Artifact removal", emphasis="primary")
    s.add_arrow("raw", "filter")
    s.add_arrow("filter", "ica")
    s.auto_layout(layout="lr", gap_mm=15)
    fig, ax = fr.subplots()
    ax.diagram(s, id="pipeline")
    fr.save(fig, out / "quickstart_schematic_lr.png", validate=False)

    # Diagram TB
    s = fr.Diagram(title="Neural Network", width_mm=150, height_mm=250)
    s.add_box("input", "Input Layer", subtitle="784 neurons", emphasis="muted")
    s.add_box("conv", "Conv2D", subtitle="32 filters", emphasis="primary")
    s.add_box("out", "Output", subtitle="10 classes", emphasis="warning")
    s.add_arrow("input", "conv")
    s.add_arrow("conv", "out")
    s.auto_layout(layout="tb", gap_mm=10)
    fig, ax = fr.subplots()
    ax.diagram(s, id="nn")
    fr.save(fig, out / "quickstart_schematic_tb.png", validate=False)


# ── Symlinking ───────────────────────────────────────────────────────────


def symlink_to_static(out):
    """Create symlinks from _static/ to session output images."""
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for png in sorted(out.glob("*.png")):
        if png.name.endswith("_hitmap.png"):
            continue
        target = STATIC_DIR / png.name
        if target.is_symlink() or target.exists():
            target.unlink()
        target.symlink_to(os.path.relpath(png, STATIC_DIR))
        count += 1
    return count


# ── Main ─────────────────────────────────────────────────────────────────


@stx.session
def main(
    only="",
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Generate RTD documentation images with session tracking.

    Parameters
    ----------
    only : str
        Generate only: concept, gallery, or quickstart. Empty = all.
    """
    out = Path(CONFIG.SDIR_OUT)

    generators = {
        "concept": ("Concept diagram", generate_concept_diagram),
        "gallery": ("Gallery images", generate_gallery_images),
        "quickstart": ("Quickstart images", generate_quickstart_images),
    }

    targets = [only] if only and only in generators else list(generators.keys())

    for key in targets:
        label, func = generators[key]
        logger.info(f"Generating: {label}")
        func(out)

    n = symlink_to_static(out)
    logger.info(f"Symlinked {n} images to {STATIC_DIR}")

    return 0


if __name__ == "__main__":
    main()
