Quick Start
===========

Creating Your First Reproducible Figure
---------------------------------------

FigRecipe wraps matplotlib with automatic recording. Use the standard matplotlib API:

.. code-block:: python

    import figrecipe as fr
    import numpy as np

    # Create figure with recording
    fig, ax = fr.subplots()

    # Use standard matplotlib methods
    x = np.linspace(0, 2 * np.pi, 100)
    ax.plot(x, np.sin(x), label="sin(x)", color="blue", id="sine")
    ax.plot(x, np.cos(x), label="cos(x)", color="red", id="cosine")

    ax.set_xlabel("X (radians)")
    ax.set_ylabel("Y")
    ax.set_title("Trigonometric Functions")
    ax.legend()

    # Save creates: plot.png + plot.yaml
    fr.save(fig, "trig_plot.png")

.. image:: _static/quickstart_trig.png
   :width: 400px
   :align: center
   :alt: Trigonometric plot example

Bundle Format (Recommended for Sharing)
---------------------------------------

For sharing reproducible figures, use the **ZIP bundle format**:

.. code-block:: python

    import figrecipe as fr
    import numpy as np

    fig, ax = fr.subplots()
    x = np.array([1, 2, 3, 4, 5])
    y = x ** 2
    ax.scatter(x, y, id="data")
    ax.set_title("Quadratic Data")

    # Save as self-contained ZIP bundle
    fr.save(fig, "figure.zip")

.. image:: _static/quickstart_bundle.png
   :width: 400px
   :align: center
   :alt: Bundle format example

**Bundle Structure:**

::

    figure.zip
    ├── spec.json         # WHAT to plot (semantic specification)
    ├── style.json        # HOW it looks (colors, fonts, sizes)
    ├── data.csv          # Immutable source data
    └── exports/
        ├── figure.png
        └── figure_hitmap.png

**Load and Reproduce from Bundle:**

.. code-block:: python

    # Load components separately
    spec, style, data = fr.load_bundle("figure.zip")

    # Or reproduce directly
    fig, ax = fr.reproduce_bundle("figure.zip")

Saving Figures
--------------

All three save methods are equivalent for RecordingFigures:

.. code-block:: python

    # These produce identical output (same DPI, crop, recipe):
    fr.save(fig, "plot.png")       # Explicit API
    fig.savefig("plot.png")        # Delegates to fr.save()

    # In a @stx.session context:
    stx.io.save(fig, "plot.png")   # SciTeX universal I/O

Use whichever style you prefer — they all go through the same pipeline
with style-based DPI, auto-crop, and recipe generation.

.. warning::

    Never bypass the wrapper with ``fig.fig.savefig()`` — that accesses
    the raw matplotlib figure and skips DPI, crop, and recipe logic.

Output Files
------------

FigRecipe creates different outputs depending on format:

**PNG/YAML format** (for development):

::

    plot.png               # The figure image
    plot.yaml              # Recipe for reproduction
    plot_data/             # Data CSV files

**ZIP bundle** (for sharing):

::

    plot.zip               # Self-contained bundle with all data

Reproducing a Figure
--------------------

Recreate any figure from its recipe:

.. code-block:: python

    import figrecipe as fr

    # From YAML recipe
    fig, ax = fr.reproduce("trig_plot.yaml")

    # Save reproduced figure (pixel-identical to original)
    fr.save(fig, "reproduced.png")

    # From ZIP bundle
    fig, ax = fr.reproduce_bundle("figure.zip")

    # Optionally modify and save again
    ax.set_title("Modified Title")
    fr.save(fig, "modified.png")

CLI Commands
------------

FigRecipe provides a comprehensive CLI:

.. code-block:: bash

    # Show help
    figrecipe --help

    # Reproduce a figure
    figrecipe reproduce trig_plot.yaml -o reproduced.png

    # Validate reproduction fidelity
    figrecipe validate trig_plot.yaml

    # Compare two images
    figrecipe diff original.png reproduced.png

    # Launch GUI editor
    figrecipe gui trig_plot.yaml

MCP Server for AI Agents
------------------------

FigRecipe includes an MCP server for AI integration:

.. code-block:: bash

    # Start MCP server
    figrecipe mcp start

    # List available MCP tools
    figrecipe mcp list-tools

    # Install to Claude Code
    figrecipe mcp install --claude-code

Statistical Annotations
-----------------------

Add significance brackets:

.. code-block:: python

    import figrecipe as fr

    fig, ax = fr.subplots()
    ax.bar(["Control", "Treatment"], [10, 15], yerr=[1, 1.5])

    # Add significance annotation
    ax.add_stat_annotation(
        x1=0, x2=1,
        p_value=0.01,
        style="stars"  # Shows **
    )

    fr.save(fig, "stats_plot.png")

Multi-Panel Composition
-----------------------

Compose multiple figures:

.. code-block:: python

    import figrecipe as fr

    # Create individual panels
    fig1, ax1 = fr.subplots()
    ax1.plot([1, 2, 3], [1, 4, 9])
    fr.save(fig1, "panel_a.png")

    fig2, ax2 = fr.subplots()
    ax2.bar(["A", "B"], [10, 15])
    fr.save(fig2, "panel_b.png")

    # Compose into multi-panel figure
    fr.compose(
        sources=["panel_a.yaml", "panel_b.yaml"],
        output_path="composed.png",
        layout="horizontal",
        panel_labels=True
    )

Box-and-Arrow Diagrams
-----------------------

Create publication-quality diagrams with mm-based coordinates:

.. code-block:: python

    import figrecipe as fr

    s = fr.Diagram(title="EEG Analysis Pipeline", width_mm=170, height_mm=100)
    s.add_box("raw", "Raw EEG", subtitle="64 channels", emphasis="muted")
    s.add_box("filter", "Bandpass Filter", subtitle="0.5-45 Hz", emphasis="primary")
    s.add_box("ica", "ICA", subtitle="Artifact removal", emphasis="primary")
    s.add_arrow("raw", "filter")
    s.add_arrow("filter", "ica")
    s.auto_layout(layout="lr", gap_mm=15)

    fig, ax = fr.subplots()
    ax.diagram(s, id="pipeline")
    fr.save(fig, "pipeline.png")

.. image:: _static/quickstart_schematic_lr.png
   :width: 100%
   :align: center
   :alt: Left-to-right schematic pipeline

Top-to-bottom layouts work the same way:

.. code-block:: python

    s = fr.Diagram(title="Neural Network", width_mm=150, height_mm=250)
    s.add_box("input", "Input Layer", subtitle="784 neurons", emphasis="muted")
    s.add_box("conv", "Conv2D", subtitle="32 filters", emphasis="primary")
    s.add_box("out", "Output", subtitle="10 classes", emphasis="warning")
    s.add_arrow("input", "conv")
    s.add_arrow("conv", "out")
    s.auto_layout(layout="tb", gap_mm=10)

.. image:: _static/quickstart_schematic_tb.png
   :width: 40%
   :align: center
   :alt: Top-to-bottom schematic architecture

Diagram Validation Rules
^^^^^^^^^^^^^^^^^^^^^^^^

All rules are enforced automatically on render. When validation fails, figures are saved with a ``_FAILED`` suffix for inspection.

.. list-table::
   :header-rows: 1
   :widths: 10 50 20

   * - Rule
     - Check
     - Severity
   * - W
     - Width exceeds 185 mm (double-column max)
     - UserWarning
   * - R1
     - Container must enclose all children
     - ValueError
   * - R2
     - No two boxes may overlap
     - ValueError
   * - R3
     - Container title must clear children (5 mm zone)
     - UserWarning
   * - R4
     - Box text must fit within padded inner area
     - UserWarning
   * - R5
     - Text-to-text margin >= 2 mm
     - ValueError
   * - R6
     - Text-to-edge margin >= 2 mm
     - ValueError
   * - R7
     - Arrow visible-length ratio >= 90%
     - ValueError
   * - R8
     - Curved-arrow label on same side as arc
     - ValueError
