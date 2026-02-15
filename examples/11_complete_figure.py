#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complete scientific figure: plot + diagram + composition.

Demonstrates the full FigRecipe workflow in one script:
1. Panel A: Line plot (ERP waveform, two conditions)
2. Panel B: Bar chart (group comparison with error bars)
3. Panel C: Diagram (data processing pipeline)
4. Compose all panels into a single multi-panel figure

Outputs:
    ./11_complete_figure_out/panel_a.yaml
    ./11_complete_figure_out/panel_b.yaml
    ./11_complete_figure_out/panel_c.yaml
    ./11_complete_figure_out/complete_figure.png
"""

import matplotlib

matplotlib.use("Agg")

from pathlib import Path

import numpy as np
import scitex as stx

import figrecipe as fr


def create_panel_a(output_dir: Path, logger):
    """Panel A: ERP waveform line plot."""
    t = np.linspace(-0.2, 0.8, 250)
    # Simulated ERP: N100 + P300
    erp_ctrl = -2 * np.exp(-((t - 0.1) ** 2) / 0.002) + 3 * np.exp(
        -((t - 0.35) ** 2) / 0.01
    )
    erp_task = -3 * np.exp(-((t - 0.1) ** 2) / 0.002) + 5 * np.exp(
        -((t - 0.30) ** 2) / 0.008
    )
    erp_ctrl += np.random.default_rng(42).normal(0, 0.3, len(t))
    erp_task += np.random.default_rng(43).normal(0, 0.3, len(t))

    fig, ax = fr.subplots()
    ax.plot(t, erp_ctrl, label="Control", id="erp_ctrl")
    ax.plot(t, erp_task, label="Task", id="erp_task")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude (uV)")
    ax.set_title("ERP Waveforms")
    ax.legend()

    path = output_dir / "panel_a.yaml"
    fr.save(fig, path, validate=False, verbose=False)
    logger.info(f"  Panel A saved: {path}")
    return path


def create_panel_b(output_dir: Path, logger):
    """Panel B: Group comparison bar chart."""
    groups = ["Control", "Mild", "Moderate", "Severe"]
    means = [85, 72, 58, 41]
    errors = [4, 5, 6, 7]

    fig, ax = fr.subplots()
    ax.bar(groups, means, yerr=errors, id="comparison")
    ax.set_xlabel("Group")
    ax.set_ylabel("Score")
    ax.set_title("Cognitive Score by Group")

    path = output_dir / "panel_b.yaml"
    fr.save(fig, path, validate=False, verbose=False)
    logger.info(f"  Panel B saved: {path}")
    return path


def create_panel_c(output_dir: Path, logger):
    """Panel C: Data processing pipeline diagram."""
    s = fr.Diagram(title="Processing Pipeline", width_mm=160, height_mm=60)
    s.add_box("raw", "Raw EEG", emphasis="muted")
    s.add_box("preproc", "Preprocessing", emphasis="primary")
    s.add_box("feature", "Feature Extraction", emphasis="primary")
    s.add_box("model", "Classification", emphasis="success")
    s.add_box("result", "Results", emphasis="warning")
    s.add_arrow("raw", "preproc")
    s.add_arrow("preproc", "feature")
    s.add_arrow("feature", "model")
    s.add_arrow("model", "result")
    s.auto_layout(layout="lr", gap_mm=10)

    fig, ax = fr.subplots()
    ax.diagram(s, id="pipeline")

    path = output_dir / "panel_c.yaml"
    fr.save(fig, path, validate=False, verbose=False)
    logger.info(f"  Panel C saved: {path}")
    return path


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    rngg=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Complete figure: plot + diagram + composition."""
    OUT = Path(CONFIG.SDIR_OUT)

    # Create individual panels
    logger.info("Creating panels...")
    panel_a = create_panel_a(OUT, logger)
    panel_b = create_panel_b(OUT, logger)
    panel_c = create_panel_c(OUT, logger)

    # --- Compose: A and B on top, C spanning full bottom ---
    logger.info("Composing figure...")
    fig, axes = fr.compose(
        canvas_size_mm=(180, 130),
        sources={
            str(panel_a): {"xy_mm": (0, 0), "size_mm": (85, 60)},
            str(panel_b): {"xy_mm": (90, 0), "size_mm": (85, 60)},
            str(panel_c): {"xy_mm": (0, 68), "size_mm": (175, 55)},
        },
        panel_labels=True,
        label_style="uppercase",
    )
    fr.save(fig, OUT / "complete_figure.png", verbose=True, validate=False)

    logger.info(f"All outputs saved to: {OUT}/")
    return 0


if __name__ == "__main__":
    main()

# EOF
