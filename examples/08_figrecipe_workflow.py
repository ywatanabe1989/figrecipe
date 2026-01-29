#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-26 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/07_figrecipe_workflow.py

"""
FigRecipe Complete Workflow Demo
================================

End-to-end demonstration of figrecipe's reproducible figure workflow:

1. Generate data (simulating analysis code)
2. Create figures with figrecipe
3. Save as YAML recipe + PNG
4. Reproduce from recipe
5. Compose multi-panel figures

This demonstrates the core value proposition:
- Full reproducibility via YAML recipes
- Separation of data from visualization
- Integration with analysis pipelines
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import scitex as stx


def step1_generate_data(output_dir, logger):
    """Step 1: Analysis code generates CSV data."""
    logger.info("Step 1: Generate CSV data (simulating analysis code)")

    # Simulate experiment data
    np.random.seed(42)
    n_points = 50

    time = np.linspace(0, 10, n_points)
    signal = np.sin(time) * np.exp(-time / 5) + np.random.normal(0, 0.1, n_points)
    fitted = np.sin(time) * np.exp(-time / 5)

    # Save to CSV
    df = pd.DataFrame(
        {"time_sec": time, "measured_signal": signal, "fitted_curve": fitted}
    )
    df.to_csv(output_dir / "experiment_data.csv", index=False)
    logger.info(f"Created: experiment_data.csv ({len(df)} rows)")

    # Also create group comparison data
    groups = []
    values = []
    for name, mean, std in [
        ("Control", 10, 2),
        ("Treatment A", 15, 2.5),
        ("Treatment B", 18, 3),
    ]:
        n = 30
        groups.extend([name] * n)
        values.extend(np.random.normal(mean, std, n).tolist())

    df_groups = pd.DataFrame({"group": groups, "measurement": values})
    df_groups.to_csv(output_dir / "group_comparison.csv", index=False)
    logger.info(f"Created: group_comparison.csv ({len(df_groups)} rows)")


def step2_create_mcp_spec(logger):
    """Step 2: Create MCP-compatible plot specification using CSV columns."""
    logger.info("Step 2: Create MCP plot specification (CSV column references)")

    # This is the spec format used by MCP plt_plot tool
    spec_line_plot = {
        "figure": {"width_mm": 80, "height_mm": 60, "style": "SCITEX"},
        "plots": [
            {
                "type": "scatter",
                "data_file": "experiment_data.csv",  # CSV file path
                "x": "time_sec",  # Column name (string, not array!)
                "y": "measured_signal",  # Column name
                "color": "blue",
                "alpha": 0.6,
                "label": "Measured",
            },
            {
                "type": "line",
                "data_file": "experiment_data.csv",
                "x": "time_sec",
                "y": "fitted_curve",
                "color": "red",
                "label": "Fitted",
            },
        ],
        "xlabel": "Time (s)",
        "ylabel": "Signal (mV)",
        "title": "Damped Oscillation",
        "legend": True,
    }

    logger.info("  data_file: experiment_data.csv")
    logger.info("  x column: time_sec")
    logger.info("  y columns: measured_signal, fitted_curve")

    return spec_line_plot


def step3_create_figure_from_spec(spec, output_dir, logger):
    """Step 3: Create figure using the spec (like MCP would do)."""
    logger.info("Step 3: Create figure from spec (MCP-style)")

    from figrecipe._api._plot import create_figure_from_spec

    result = create_figure_from_spec(
        spec=spec,
        output_path=str(output_dir / "csv_workflow_demo.png"),
        dpi=300,
        save_recipe=True,
    )

    logger.info(f"Created: {result['image_path']}")
    logger.info(f"Recipe:  {result['recipe_path']}")

    return result


def step4_demonstrate_python_api(output_dir, logger):
    """Step 4: Alternative - Direct Python API with CSV."""
    logger.info("Step 4: Alternative - Direct Python API")

    import figrecipe as fr

    # Load CSV data
    df = pd.read_csv(output_dir / "experiment_data.csv")

    # Create figure with standard matplotlib API
    fig, ax = fr.subplots(axes_width_mm=80, axes_height_mm=60)

    ax.scatter(
        df["time_sec"],
        df["measured_signal"],
        color="blue",
        alpha=0.6,
        label="Measured",
    )
    ax.plot(df["time_sec"], df["fitted_curve"], color="red", label="Fitted")

    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Signal (mV)")
    ax.set_title("Python API Demo")
    ax.legend()

    # Save creates: image + recipe + data CSVs
    fr.save(fig, output_dir / "python_api_demo.png")
    logger.info(
        "Created: python_api_demo.png + python_api_demo.yaml + python_api_demo_data/"
    )


def step5_show_output_structure(output_dir, logger):
    """Step 5: Show the output file structure."""
    logger.info("Step 5: Output file structure")

    for f in sorted(output_dir.iterdir()):
        if f.is_dir():
            logger.info(f"  {f.name}/")
            for sub in sorted(f.iterdir()):
                logger.info(f"    {sub.name}")
        else:
            size = f.stat().st_size
            logger.info(f"  {f.name} ({size:,} bytes)")


@stx.session
def main(
    CONFIG=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Run the complete CSV workflow demonstration."""
    output_path = Path(CONFIG.SDIR_OUT)

    # Change to output directory for relative paths
    os.chdir(output_path)

    logger.info("FigRecipe CSV Workflow Demo")
    logger.info("This demonstrates the RECOMMENDED pattern:")
    logger.info("  Analysis code → CSV → MCP plot spec → Figure")

    # Step 1: Generate data (like analysis code would)
    step1_generate_data(output_path, logger)

    # Step 2: Create MCP-compatible spec with CSV references
    spec = step2_create_mcp_spec(logger)

    # Step 3: Create figure from spec (MCP-style)
    step3_create_figure_from_spec(spec, output_path, logger)

    # Step 4: Alternative Python API
    step4_demonstrate_python_api(output_path, logger)

    # Step 5: Show output structure
    step5_show_output_structure(output_path, logger)

    logger.info("SUMMARY: CSV Workflow Benefits")
    logger.info("1. Data separate from visualization spec")
    logger.info("2. Easy to update data without changing spec")
    logger.info("3. Better integration with analysis code")
    logger.info("4. MCP can visualize any CSV file")
    logger.info("5. Full reproducibility via YAML recipes")

    return 0


if __name__ == "__main__":
    main()

# EOF
