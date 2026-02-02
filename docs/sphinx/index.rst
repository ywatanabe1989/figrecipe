.. FigRecipe documentation master file

FigRecipe - Reproducible Scientific Figures
===========================================

**FigRecipe** is a framework for creating reproducible, style-editable scientific figures via YAML recipes. It wraps matplotlib with automatic recording, enabling figures to be reproduced, modified, and shared.

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/figrecipe

Key Features
------------

- **Automatic Recording**: All matplotlib calls automatically recorded to YAML
- **Reproducibility**: Recreate any figure from its recipe file
- **Style Editing**: Change styles without regenerating data
- **Data Preservation**: Plot data saved to CSV files
- **CSV Column Input**: Reference CSV columns in declarative specs
- **Statistical Annotations**: Add significance brackets with p-values
- **Multi-Panel Composition**: Combine figures with fr.compose()
- **MCP Integration**: AI agents can create figures via MCP server

Quick Example
-------------

Python API:

.. code-block:: python

    import figrecipe as fr
    import numpy as np

    # Create figure (auto-recording enabled)
    fig, ax = fr.subplots()

    # Standard matplotlib API
    x = np.linspace(0, 10, 100)
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()

    # Save creates image + recipe + data CSVs
    fr.save(fig, "my_plot.png")

CLI:

.. code-block:: bash

    # Reproduce a figure from recipe
    figrecipe reproduce my_plot.yaml -o reproduced.png

    # Launch GUI editor
    figrecipe gui my_plot.yaml

    # Validate reproduction fidelity
    figrecipe validate my_plot.yaml

MCP Server:

.. code-block:: bash

    # Start MCP server for AI agent integration
    figrecipe mcp start

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
