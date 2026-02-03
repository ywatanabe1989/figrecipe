#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-02 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/07_figrecipe_concept_diagram.py

"""FigRecipe Concept Diagram - For Researchers.

Creates a visual explanation of FigRecipe's core concepts:
- Separation of DATA (what to show) from STYLE (how to show)
- Auto-recording from Python code to YAML recipe
- Validation and reproduction workflow

Usage:
    python 07_figrecipe_concept_diagram.py

Output:
    07_figrecipe_concept_diagram_out/figrecipe_concept.png (200 dpi)
    07_figrecipe_concept_diagram_out/figrecipe_concept.svg (vector)
"""

from pathlib import Path

import matplotlib.pyplot as plt
import scitex as stx
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# Colors - muted, professional (Material Design inspired)
_COLORS = {
    "code": "#E3F2FD",
    "code_border": "#1976D2",
    "recipe": "#FFF8E1",
    "recipe_border": "#FF8F00",
    "data": "#E8F5E9",
    "data_border": "#388E3C",
    "style": "#F3E5F5",
    "style_border": "#7B1FA2",
    "figure": "#FFEBEE",
    "figure_border": "#C62828",
    "text": "#212121",
    "subtext": "#616161",
}


def _add_box(ax, xy, w, h, face, edge, lw=2, rounding=0.2):
    """Add a rounded box patch."""
    box = FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle=f"round,pad=0.05,rounding_size={rounding}",
        facecolor=face,
        edgecolor=edge,
        linewidth=lw,
    )
    ax.add_patch(box)
    return box


def _add_text(ax, x, y, text, **kwargs):
    """Add centered text with defaults."""
    defaults = {"ha": "center", "va": "center", "color": _COLORS["text"]}
    defaults.update(kwargs)
    ax.text(x, y, text, **defaults)


def _draw_code_section(ax):
    """Draw the Python Code box."""
    _add_box(ax, (0.5, 5.8), 2.5, 1.4, _COLORS["code"], _COLORS["code_border"])
    _add_text(
        ax,
        1.75,
        6.7,
        "Python Code",
        fontsize=11,
        fontweight="bold",
        color=_COLORS["code_border"],
    )
    _add_text(
        ax,
        1.75,
        6.25,
        "import figrecipe as fr",
        fontsize=8,
        family="monospace",
        color=_COLORS["subtext"],
    )
    _add_text(
        ax,
        1.75,
        5.95,
        "ax.plot(x, y)",
        fontsize=8,
        family="monospace",
        color=_COLORS["subtext"],
    )

    # Arrow to Recipe
    arrow = FancyArrowPatch(
        (3.0, 6.5),
        (4.3, 6.5),
        arrowstyle="-|>",
        mutation_scale=15,
        color="#757575",
        linewidth=2,
    )
    ax.add_patch(arrow)
    _add_text(
        ax,
        3.65,
        6.75,
        "auto-record",
        fontsize=8,
        color=_COLORS["subtext"],
        fontstyle="italic",
    )


def _draw_recipe_section(ax):
    """Draw the Recipe (YAML) box."""
    _add_box(
        ax, (4.3, 5.5), 3.4, 2.0, _COLORS["recipe"], _COLORS["recipe_border"], lw=2.5
    )
    _add_text(
        ax,
        6.0,
        7.1,
        "Recipe (YAML)",
        fontsize=12,
        fontweight="bold",
        color=_COLORS["recipe_border"],
    )
    _add_text(ax, 6.0, 6.6, "Structure + Plot Calls", fontsize=9)
    _add_text(
        ax,
        6.0,
        6.15,
        "version, environment",
        fontsize=8,
        color=_COLORS["subtext"],
        fontstyle="italic",
    )
    _add_text(
        ax,
        6.0,
        5.75,
        "Reproducible specification",
        fontsize=8,
        color=_COLORS["recipe_border"],
        fontweight="bold",
    )


def _draw_separation_section(ax):
    """Draw the DATA/STYLE separation section."""
    # Container
    _add_box(ax, (0.5, 2.2), 7.2, 2.8, "#ECEFF1", "#455A64", lw=2.5, rounding=0.25)
    _add_text(
        ax,
        4.1,
        4.7,
        "Key Innovation: Separation of Concerns",
        fontsize=11,
        fontweight="bold",
        color="#37474F",
    )

    # DATA box
    _add_box(
        ax,
        (0.8, 2.5),
        3.0,
        1.9,
        _COLORS["data"],
        _COLORS["data_border"],
        lw=2.5,
        rounding=0.15,
    )
    _add_text(
        ax,
        2.3,
        4.0,
        "DATA",
        fontsize=13,
        fontweight="bold",
        color=_COLORS["data_border"],
    )
    _add_text(ax, 2.3, 3.55, "CSV / NPZ files", fontsize=9)
    _add_text(
        ax,
        2.3,
        3.1,
        "Scientific Meaning",
        fontsize=10,
        fontweight="bold",
        color="#2E7D32",
    )
    _add_text(
        ax,
        2.3,
        2.7,
        "WHAT to show",
        fontsize=9,
        fontstyle="italic",
        color=_COLORS["subtext"],
    )

    # STYLE box
    _add_box(
        ax,
        (4.4, 2.5),
        3.0,
        1.9,
        _COLORS["style"],
        _COLORS["style_border"],
        lw=2.5,
        rounding=0.15,
    )
    _add_text(
        ax,
        5.9,
        4.0,
        "STYLE",
        fontsize=13,
        fontweight="bold",
        color=_COLORS["style_border"],
    )
    _add_text(ax, 5.9, 3.55, "Presets / GUI editing", fontsize=9)
    _add_text(
        ax,
        5.9,
        3.1,
        "Visual Appearance",
        fontsize=10,
        fontweight="bold",
        color="#6A1B9A",
    )
    _add_text(
        ax,
        5.9,
        2.7,
        "HOW to show",
        fontsize=9,
        fontstyle="italic",
        color=_COLORS["subtext"],
    )

    # Arrows from Recipe
    ax.annotate(
        "",
        xy=(2.3, 4.4),
        xytext=(5.3, 5.5),
        arrowprops=dict(arrowstyle="-|>", color=_COLORS["data_border"], lw=2),
    )
    ax.annotate(
        "",
        xy=(5.9, 4.4),
        xytext=(6.3, 5.5),
        arrowprops=dict(arrowstyle="-|>", color=_COLORS["style_border"], lw=2),
    )


def _draw_figure_section(ax):
    """Draw the Figure output box."""
    _add_box(
        ax, (8.5, 4.2), 3.0, 2.3, _COLORS["figure"], _COLORS["figure_border"], lw=2.5
    )
    _add_text(
        ax,
        10.0,
        6.1,
        "Figure",
        fontsize=13,
        fontweight="bold",
        color=_COLORS["figure_border"],
    )
    _add_text(ax, 10.0, 5.6, "PNG / PDF / SVG", fontsize=10)
    _add_text(
        ax,
        10.0,
        5.15,
        "Publication-ready",
        fontsize=9,
        color=_COLORS["subtext"],
        fontstyle="italic",
    )
    _add_text(
        ax,
        10.0,
        4.6,
        "Validated & Reproducible",
        fontsize=9,
        fontweight="bold",
        color="#388E3C",
    )

    # Arrows to Figure
    ax.annotate(
        "",
        xy=(8.5, 5.3),
        xytext=(7.7, 6.0),
        arrowprops=dict(arrowstyle="-|>", color=_COLORS["recipe_border"], lw=2),
    )
    ax.annotate(
        "",
        xy=(8.5, 4.8),
        xytext=(7.4, 3.5),
        arrowprops=dict(
            arrowstyle="-|>",
            color=_COLORS["data_border"],
            lw=2,
            connectionstyle="arc3,rad=0.2",
        ),
    )
    ax.annotate(
        "",
        xy=(8.5, 5.0),
        xytext=(7.4, 3.5),
        arrowprops=dict(
            arrowstyle="-|>",
            color=_COLORS["style_border"],
            lw=2,
            connectionstyle="arc3,rad=-0.1",
        ),
    )

    # Validation feedback loop
    ax.annotate(
        "",
        xy=(7.7, 6.3),
        xytext=(11.2, 5.3),
        arrowprops=dict(
            arrowstyle="-|>",
            color="#388E3C",
            lw=2,
            ls="--",
            connectionstyle="arc3,rad=-0.4",
        ),
    )
    _add_text(
        ax, 10.3, 6.5, "validate", fontsize=8, color="#388E3C", fontstyle="italic"
    )


def _draw_benefits_section(ax):
    """Draw the benefits section at bottom."""
    _add_box(ax, (0.5, 0.4), 11.0, 1.4, "#E0F7FA", "#00838F", rounding=0.2)
    _add_text(
        ax,
        6.0,
        1.5,
        "Benefits for Researchers",
        fontsize=11,
        fontweight="bold",
        color="#006064",
    )

    # Three benefits
    for x, title, desc in [
        (2.2, "Reproducibility", "Same recipe = Same figure"),
        (6.0, "Flexibility", "Change style, keep meaning"),
        (9.8, "Verification", "Pixel-level validation"),
    ]:
        _add_text(ax, x, 1.0, title, fontsize=10, fontweight="bold", color="#00695C")
        _add_text(ax, x, 0.65, desc, fontsize=8, color=_COLORS["subtext"])

    # Vertical separators
    ax.plot([4.0, 4.0], [0.55, 1.15], color="#B0BEC5", lw=1)
    ax.plot([8.0, 8.0], [0.55, 1.15], color="#B0BEC5", lw=1)


def create_figrecipe_concept_diagram(output_dir: Path = None, dpi: int = 200):
    """Create FigRecipe concept diagram explaining the separation of concerns.

    Parameters
    ----------
    output_dir : Path, optional
        Output directory. Defaults to script_out directory.
    dpi : int
        DPI for PNG output. Default 200.

    Returns
    -------
    tuple
        Paths to (png_file, svg_file)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / "07_figrecipe_concept_diagram_out"
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Set up figure
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect("equal")
    ax.axis("off")

    # Title
    _add_text(
        ax,
        6,
        7.6,
        "FigRecipe: Reproducible Scientific Figures",
        fontsize=16,
        fontweight="bold",
    )

    # Draw all sections
    _draw_code_section(ax)
    _draw_recipe_section(ax)
    _draw_separation_section(ax)
    _draw_figure_section(ax)
    _draw_benefits_section(ax)

    # Save
    plt.tight_layout()
    png_path = output_dir / "figrecipe_concept.png"
    svg_path = output_dir / "figrecipe_concept.svg"

    plt.savefig(
        png_path, dpi=dpi, bbox_inches="tight", facecolor="white", edgecolor="none"
    )
    plt.savefig(svg_path, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)

    print(f"Saved: {png_path}")
    print(f"Saved: {svg_path}")
    return png_path, svg_path


@stx.session
def main(
    dpi: int = 200,
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Create FigRecipe concept diagram."""
    OUT = Path(CONFIG.SDIR_OUT)
    png_path, svg_path = create_figrecipe_concept_diagram(output_dir=OUT, dpi=dpi)
    logger.info(f"Saved: {png_path}")
    logger.info(f"Saved: {svg_path}")
    return 0


if __name__ == "__main__":
    main()

# EOF
