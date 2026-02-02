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
    ax.plot(x, np.sin(x), label="sin(x)", color="blue")
    ax.plot(x, np.cos(x), label="cos(x)", color="red")

    ax.set_xlabel("X (radians)")
    ax.set_ylabel("Y")
    ax.set_title("Trigonometric Functions")
    ax.legend()

    # Save creates: plot.png + plot.yaml + plot_data/
    fr.save(fig, "trig_plot.png")

Output Files
------------

FigRecipe automatically creates:

::

    trig_plot.png          # The figure image
    trig_plot.yaml         # Recipe for reproduction
    trig_plot_data/        # Data CSV files
      plot_000_x.csv         # X data from first plot call
      plot_000_y.csv         # Y data from first plot call
      plot_001_x.csv         # X data from second plot call
      plot_001_y.csv         # Y data from second plot call

Reproducing a Figure
--------------------

Recreate any figure from its recipe:

.. code-block:: python

    import figrecipe as fr

    # Reproduce from recipe
    fig, ax = fr.reproduce("trig_plot.yaml")

    # Optionally modify and save again
    ax.set_title("Modified Title")
    fr.save(fig, "modified_plot.png")

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

    # Generate hitmap visualization
    figrecipe hitmap original.png reproduced.png

    # Launch GUI editor
    figrecipe gui trig_plot.yaml

    # Create figure from declarative spec
    figrecipe plot spec.yaml -o output.png

MCP Server for AI Agents
------------------------

FigRecipe includes an MCP server for AI integration:

.. code-block:: bash

    # Start MCP server
    figrecipe mcp run

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
    fig, axes = fr.compose(
        sources=["panel_a.yaml", "panel_b.yaml"],
        layout="horizontal",
        panel_labels=True
    )
    fr.save(fig, "composed.png")
