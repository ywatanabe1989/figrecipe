Plot Gallery
============

FigRecipe supports all standard matplotlib plot types. Below are examples of each plot type with the declarative specification format used by the MCP server.

Basic Plots
-----------

Line Plot
^^^^^^^^^

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, ax = fr.subplots()
   x = np.linspace(0, 10, 100)
   ax.plot(x, np.sin(x), label="sin(x)", id="sine")
   ax.plot(x, np.cos(x), label="cos(x)", id="cosine")
   ax.set_xlabel("X")
   ax.set_ylabel("Y")
   ax.set_title("Line Plot")
   ax.legend()

MCP Specification:

.. code-block:: yaml

   figure:
     figsize: [6, 4]
   plots:
     - type: line
       x: [0, 1, 2, 3, 4, 5]
       y: [0, 1, 4, 9, 16, 25]
       label: "quadratic"
   xlabel: "X"
   ylabel: "Y"
   title: "Line Plot"

Scatter Plot
^^^^^^^^^^^^

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, ax = fr.subplots()
   np.random.seed(42)
   x = np.random.randn(50)
   y = x + np.random.randn(50) * 0.5
   ax.scatter(x, y, c=x, cmap="viridis", s=50, id="data")
   ax.set_xlabel("X")
   ax.set_ylabel("Y")
   ax.set_title("Scatter Plot")

MCP Specification:

.. code-block:: yaml

   plots:
     - type: scatter
       x: [1, 2, 3, 4, 5]
       y: [2, 4, 1, 5, 3]
       c: [0.1, 0.3, 0.5, 0.7, 0.9]
       cmap: viridis
       s: 50
   xlabel: "X"
   ylabel: "Y"

Bar Plot
^^^^^^^^

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, ax = fr.subplots()
   categories = ["A", "B", "C", "D", "E"]
   values = [23, 45, 12, 67, 34]
   ax.bar(categories, values, color="steelblue", id="bars")
   ax.set_xlabel("Category")
   ax.set_ylabel("Value")
   ax.set_title("Bar Plot")

MCP Specification:

.. code-block:: yaml

   plots:
     - type: bar
       x: ["A", "B", "C", "D"]
       height: [10, 20, 15, 25]
       color: steelblue
   xlabel: "Category"
   ylabel: "Value"

Statistical Plots
-----------------

Histogram
^^^^^^^^^

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, ax = fr.subplots()
   np.random.seed(42)
   data = np.random.randn(1000)
   ax.hist(data, bins=30, alpha=0.7, color="steelblue", edgecolor="white", id="hist")
   ax.set_xlabel("Value")
   ax.set_ylabel("Frequency")
   ax.set_title("Histogram")

Box Plot
^^^^^^^^

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, ax = fr.subplots()
   np.random.seed(42)
   data = [np.random.randn(100) + i for i in range(4)]
   ax.boxplot(data, labels=["A", "B", "C", "D"], id="boxplot")
   ax.set_xlabel("Group")
   ax.set_ylabel("Value")
   ax.set_title("Box Plot")

Violin Plot
^^^^^^^^^^^

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, ax = fr.subplots()
   np.random.seed(42)
   data = [np.random.randn(100) + i for i in range(4)]
   ax.violinplot(data, positions=[1, 2, 3, 4], id="violin")
   ax.set_xticks([1, 2, 3, 4])
   ax.set_xticklabels(["A", "B", "C", "D"])
   ax.set_xlabel("Group")
   ax.set_ylabel("Value")
   ax.set_title("Violin Plot")

2D Plots
--------

Heatmap / Imshow
^^^^^^^^^^^^^^^^

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, ax = fr.subplots()
   np.random.seed(42)
   data = np.random.randn(10, 10)
   im = ax.imshow(data, cmap="coolwarm", id="heatmap")
   fig.fig.colorbar(im, ax=ax._ax)
   ax.set_title("Heatmap")

Contour Plot
^^^^^^^^^^^^

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, ax = fr.subplots()
   x = np.linspace(-3, 3, 100)
   y = np.linspace(-3, 3, 100)
   X, Y = np.meshgrid(x, y)
   Z = np.sin(X) * np.cos(Y)
   cs = ax.contourf(X, Y, Z, levels=20, cmap="viridis", id="contour")
   fig.fig.colorbar(cs, ax=ax._ax)
   ax.set_xlabel("X")
   ax.set_ylabel("Y")
   ax.set_title("Contour Plot")

Multi-Panel Layouts
-------------------

Subplots
^^^^^^^^

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, axes = fr.subplots(2, 2, figsize=(8, 6))
   x = np.linspace(0, 10, 100)

   axes[0, 0].plot(x, np.sin(x), id="sin")
   axes[0, 0].set_title("Sine")

   axes[0, 1].plot(x, np.cos(x), color="orange", id="cos")
   axes[0, 1].set_title("Cosine")

   axes[1, 0].plot(x, np.exp(-x/5) * np.sin(x), color="green", id="damped")
   axes[1, 0].set_title("Damped Sine")

   axes[1, 1].plot(x, np.tan(x), color="red", id="tan")
   axes[1, 1].set_ylim(-5, 5)
   axes[1, 1].set_title("Tangent")

   fig.fig.tight_layout()

Statistical Annotations
-----------------------

FigRecipe supports statistical significance annotations with brackets and p-values:

.. plot::
   :include-source:

   import figrecipe as fr
   import numpy as np

   fig, ax = fr.subplots()
   np.random.seed(42)

   groups = ["Control", "Treatment A", "Treatment B"]
   means = [10, 15, 12]
   stds = [2, 3, 2.5]

   x = np.arange(len(groups))
   bars = ax.bar(x, means, yerr=stds, capsize=5, color=["gray", "steelblue", "coral"], id="bars")
   ax.set_xticks(x)
   ax.set_xticklabels(groups)
   ax.set_ylabel("Value")
   ax.set_title("Group Comparison with Statistics")

   # Add significance brackets manually
   y_max = max(means) + max(stds) + 2
   ax.plot([0, 0, 1, 1], [y_max, y_max+0.5, y_max+0.5, y_max], 'k-', lw=1)
   ax.text(0.5, y_max+0.7, "**", ha='center', va='bottom', fontsize=12)

MCP Specification with Statistics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

   plots:
     - type: bar
       x: [0, 1, 2]
       height: [10, 15, 12]
       yerr: [2, 3, 2.5]
       color: ["gray", "steelblue", "coral"]
       capsize: 5

   stat_annotations:
     - group1_idx: 0
       group2_idx: 1
       p_value: 0.003
       test: "t-test"

   xlabel: "Group"
   ylabel: "Value"
   title: "Statistical Comparison"

CSV Column Workflow
-------------------

FigRecipe can read data directly from CSV files:

.. code-block:: yaml

   # Reference CSV columns instead of inline data
   plots:
     - type: scatter
       data_file: "experiment_data.csv"
       x_column: "time_seconds"
       y_column: "signal_amplitude"
       label: "Experiment 1"

   xlabel: "Time (s)"
   ylabel: "Amplitude"
   title: "CSV Data Workflow"

Supported Plot Types
--------------------

FigRecipe supports all standard matplotlib axes methods:

**Line/Curve:**
- ``plot`` - Basic line plot
- ``step`` - Step plot
- ``fill`` - Filled polygon
- ``fill_between`` - Fill between curves
- ``errorbar`` - Error bar plot

**Points:**
- ``scatter`` - Scatter plot

**Bars:**
- ``bar`` - Vertical bar plot
- ``barh`` - Horizontal bar plot

**Distribution:**
- ``hist`` - Histogram
- ``hist2d`` - 2D histogram
- ``boxplot`` / ``box`` - Box plot
- ``violinplot`` / ``violin`` - Violin plot

**2D/Image:**
- ``imshow`` - Image display
- ``matshow`` - Matrix display
- ``heatmap`` - Heatmap (alias)
- ``pcolormesh`` - Pseudocolor mesh
- ``contour`` - Contour lines
- ``contourf`` - Filled contours

**Special:**
- ``pie`` - Pie chart
- ``stem`` - Stem plot
- ``eventplot`` - Event plot
- ``hexbin`` - Hexagonal binning
