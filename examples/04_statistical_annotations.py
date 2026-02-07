#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_statistical_notations_and_captions.py

Demonstrates statistical annotations (significance brackets) and caption generation.
"""

from pathlib import Path

import numpy as np
import scitex as stx

import figrecipe as fr


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Demonstrate statistical annotations and captions."""
    OUT = Path(CONFIG.SDIR_OUT)

    # Set up figure with subplots
    fig, axes = fr.subplots(1, 3, figsize=(180 / 25.4, 60 / 25.4))
    np.random.seed(42)

    # === Panel A: Basic statistical annotation ===
    ax = axes[0]
    groups = ["Control", "Treatment A", "Treatment B"]
    means = [2.1, 3.5, 4.2]
    stds = [0.8, 1.0, 0.9]
    x = np.arange(len(groups))

    # Plot bars (SCITEX: cap=0.8mm, line=0.12mm)
    ax.bar(
        x,
        means,
        yerr=stds,
        capsize=0.8 * 72 / 25.4,  # 0.8mm cap
        error_kw={"elinewidth": 0.12 * 72 / 25.4, "capthick": 0.12 * 72 / 25.4},
        id="bars_a",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Response")
    ax.set_title("Stars only")

    # Add statistical annotation brackets
    ax.add_stat_annotation(0, 1, y=5.0, p_value=0.032, style="stars", id="stat_0_1")
    ax.add_stat_annotation(1, 2, y=5.8, p_value=0.008, style="stars", id="stat_1_2")
    ax.add_stat_annotation(0, 2, y=6.6, p_value=0.001, style="stars", id="stat_0_2")

    # Set panel stats for caption generation
    ax.set_stats(
        {
            "n": 30,
            "comparisons": [
                {"name": "Ctrl vs A", "p_value": 0.032, "effect_size": 0.45},
                {"name": "A vs B", "p_value": 0.008, "effect_size": 0.62},
            ],
        }
    )

    # === Panel B: P-value style annotation ===
    ax = axes[1]
    means = [3.2, 4.1, 3.8]
    stds = [0.7, 0.9, 0.8]

    ax.bar(
        x,
        means,
        yerr=stds,
        capsize=0.8 * 72 / 25.4,
        error_kw={"elinewidth": 0.12 * 72 / 25.4, "capthick": 0.12 * 72 / 25.4},
        id="bars_b",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Score")
    ax.set_title("P-values")

    # P-value style annotations
    ax.add_stat_annotation(0, 1, y=5.5, p_value=0.023, style="p_value", id="pval_0_1")
    ax.add_stat_annotation(0, 2, y=6.3, p_value=0.156, style="p_value", id="pval_0_2")

    # === Panel C: Both stars and p-values ===
    ax = axes[2]
    means = [1.8, 2.9, 4.5]
    stds = [0.6, 0.8, 1.1]

    ax.bar(
        x,
        means,
        yerr=stds,
        capsize=0.8 * 72 / 25.4,
        error_kw={"elinewidth": 0.12 * 72 / 25.4, "capthick": 0.12 * 72 / 25.4},
        id="bars_c",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel("Level")
    ax.set_title("Stars + p-values")

    # Combined style
    ax.add_stat_annotation(0, 2, y=6.2, p_value=0.0003, style="both", id="both_0_2")

    # Add panel labels
    fig.add_panel_labels(["A", "B", "C"])

    # Save figure
    fr.save(fig, OUT / "stat_annotations.png", validate=False)

    # === Caption Generation Demo ===
    logger.info("=== Caption Generation Demo ===")

    # Generate panel caption from stats
    panel_stats = {"n": 30, "group": "Treatment group", "mean": 3.5, "std": 0.8}
    from figrecipe._wrappers._caption_generator import (
        generate_figure_caption,
        generate_panel_caption,
    )

    panel_caption = generate_panel_caption(label="A", stats=panel_stats)
    logger.info(f"Panel caption: {panel_caption}")

    # Generate figure caption with comparisons
    figure_stats = {
        "comparisons": [
            {"name": "Ctrl vs A", "p_value": 0.032, "effect_size": 0.45},
            {"name": "A vs B", "p_value": 0.008, "effect_size": 0.62},
        ]
    }
    fig_caption = generate_figure_caption(
        title="Treatment effects on response",
        panel_captions=["(A) Stars only.", "(B) P-values.", "(C) Combined."],
        stats=figure_stats,
        style="publication",
    )
    logger.info(f"Figure caption:\n{fig_caption}")

    logger.info(f"Output: {OUT / 'stat_annotations.png'}")

    return 0


if __name__ == "__main__":
    main()
