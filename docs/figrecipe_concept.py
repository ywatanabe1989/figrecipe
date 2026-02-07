#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-02 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/07_figrecipe_concept_diagram.py

"""FigRecipe Concept Diagram - Visualize the core workflow.

Creates a diagram showing FigRecipe's architecture and workflow:
- Figure creation with automatic recording
- Recipe (YAML) generation
- Reproduction and editing cycle
- MCP server integration for AI agents
"""

from pathlib import Path

import figrecipe as fr


def create_figrecipe_workflow_diagram(output_dir):
    """Create the main FigRecipe workflow diagram."""
    d = fr.Diagram(type="workflow", title="FigRecipe Workflow")

    # Input sources
    d.add_node("python", "Python Code\nfr.subplots()", shape="stadium")
    d.add_node("mcp", "MCP Server\n(AI Agents)", shape="stadium")
    d.add_node("cli", "CLI\nfigrecipe plot", shape="stadium")

    # Core processing
    d.add_node("record", "Automatic\nRecording", emphasis="primary")
    d.add_node("figure", "matplotlib\nFigure", emphasis="primary")

    # Outputs
    d.add_node("image", "Image\n(.png/.pdf)", shape="rounded", emphasis="success")
    d.add_node("recipe", "Recipe\n(.yaml)", shape="rounded", emphasis="success")
    d.add_node("data", "Data\n(.csv)", shape="rounded", emphasis="success")

    # Reproduction cycle
    d.add_node("reproduce", "Reproduce\nfr.reproduce()", emphasis="primary")
    d.add_node("gui", "GUI Editor\nfr.gui()", emphasis="primary")

    # Edges - creation flow
    d.add_edge("python", "record")
    d.add_edge("mcp", "record")
    d.add_edge("cli", "record")
    d.add_edge("record", "figure")
    d.add_edge("figure", "image", label="fr.save()")
    d.add_edge("figure", "recipe")
    d.add_edge("figure", "data")

    # Edges - reproduction flow
    d.add_edge("recipe", "reproduce", style="dashed")
    d.add_edge("reproduce", "figure", style="dashed")
    d.add_edge("recipe", "gui", style="dashed")
    d.add_edge("gui", "recipe", label="edit", style="dashed")

    # Export
    d.to_mermaid(output_dir / "figrecipe_workflow.mmd")
    d.to_yaml(output_dir / "figrecipe_workflow.yaml")

    try:
        d.render(output_dir / "figrecipe_workflow.png", format="png")
    except RuntimeError:
        pass  # Rendering requires mermaid-cli

    return d


def create_recipe_structure_diagram(output_dir):
    """Create a diagram showing recipe structure."""
    d = fr.Diagram(type="workflow", title="Recipe Structure")

    # Recipe file
    d.add_node("recipe", "recipe.yaml", shape="stadium", emphasis="primary")

    # Components
    d.add_node("figure", "figure:\n  size, dpi", shape="rounded")
    d.add_node("axes", "axes:\n  ax_0_0, ax_0_1...", shape="rounded")
    d.add_node("calls", "calls:\n  plot, scatter...", shape="rounded")
    d.add_node("style", "style:\n  colors, fonts...", shape="rounded")

    # Data files
    d.add_node("data_dir", "recipe_data/", shape="stadium", emphasis="success")
    d.add_node("csv1", "plot_000_x.csv", shape="rounded")
    d.add_node("csv2", "plot_000_y.csv", shape="rounded")

    # Edges
    d.add_edge("recipe", "figure")
    d.add_edge("recipe", "axes")
    d.add_edge("recipe", "calls")
    d.add_edge("recipe", "style")
    d.add_edge("calls", "data_dir", label="data refs")
    d.add_edge("data_dir", "csv1")
    d.add_edge("data_dir", "csv2")

    d.to_mermaid(output_dir / "recipe_structure.mmd")

    return d


def create_mcp_integration_diagram(output_dir):
    """Create a diagram showing MCP server integration."""
    d = fr.Diagram(type="workflow", title="MCP Server Integration")

    # AI Agent
    d.add_node("agent", "AI Agent\n(Claude)", shape="stadium")

    # MCP Server
    d.add_node("mcp", "FigRecipe\nMCP Server", emphasis="primary")

    # Tools
    d.add_node("plt_plot", "plt_plot", shape="rounded")
    d.add_node("plt_compose", "plt_compose", shape="rounded")
    d.add_node("plt_reproduce", "plt_reproduce", shape="rounded")
    d.add_node("diagram", "diagram_*", shape="rounded")

    # Outputs
    d.add_node(
        "output", "Publication-Ready\nFigures", shape="stadium", emphasis="success"
    )

    # Edges
    d.add_edge("agent", "mcp", label="tool calls")
    d.add_edge("mcp", "plt_plot")
    d.add_edge("mcp", "plt_compose")
    d.add_edge("mcp", "plt_reproduce")
    d.add_edge("mcp", "diagram")
    d.add_edge("plt_plot", "output")
    d.add_edge("plt_compose", "output")

    d.to_mermaid(output_dir / "mcp_integration.mmd")

    return d


def main():
    """Generate all FigRecipe concept diagrams."""
    output_dir = Path(__file__).parent / "07_figrecipe_concept_diagram_out"
    output_dir.mkdir(exist_ok=True)

    print("Creating FigRecipe concept diagrams...")

    print("1. FigRecipe Workflow")
    create_figrecipe_workflow_diagram(output_dir)

    print("2. Recipe Structure")
    create_recipe_structure_diagram(output_dir)

    print("3. MCP Integration")
    create_mcp_integration_diagram(output_dir)

    print(f"\nAll diagrams saved to: {output_dir}")
    print("\nGenerated files:")
    for f in sorted(output_dir.glob("*")):
        print(f"  {f.name}")


if __name__ == "__main__":
    main()

# EOF
