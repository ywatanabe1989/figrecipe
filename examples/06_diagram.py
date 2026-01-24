#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Example: Create diagrams with figrecipe.

Demonstrates programmatic diagram creation and YAML specification loading.
Outputs to Mermaid (.mmd) and Graphviz (.dot) formats.
"""

from pathlib import Path

import figrecipe as fr

# Output directory
OUT_DIR = Path(__file__).parent / "06_diagram_out"
OUT_DIR.mkdir(exist_ok=True)


def example_programmatic():
    """Create a diagram programmatically."""
    # Create a pipeline diagram
    d = fr.Diagram(type="pipeline", title="Data Processing Pipeline")

    # Add nodes with semantic emphasis
    d.add_node("input", "Raw Data", shape="stadium")
    d.add_node("clean", "Data Cleaning", emphasis="primary")
    d.add_node("transform", "Feature Engineering", emphasis="primary")
    d.add_node("model", "ML Model", emphasis="success", shape="rounded")
    d.add_node("output", "Predictions", shape="stadium")

    # Add edges with optional labels
    d.add_edge("input", "clean", label="validate")
    d.add_edge("clean", "transform")
    d.add_edge("transform", "model", label="train")
    d.add_edge("model", "output")

    # Export to multiple formats
    mermaid_path = OUT_DIR / "pipeline.mmd"
    graphviz_path = OUT_DIR / "pipeline.dot"
    yaml_path = OUT_DIR / "pipeline.yaml"
    png_path = OUT_DIR / "pipeline.png"

    mermaid_content = d.to_mermaid(mermaid_path)
    d.to_graphviz(graphviz_path)
    d.to_yaml(yaml_path)

    # Render to PNG (requires mermaid-cli or uses mermaid.ink)
    try:
        d.render(png_path, format="png")
        print(f"Created: {png_path}")
    except RuntimeError as e:
        print(f"PNG rendering skipped: {e}")

    print(f"Created: {mermaid_path}")
    print(f"Created: {graphviz_path}")
    print(f"Created: {yaml_path}")
    print("\nMermaid output:")
    print(mermaid_content)

    return d


def example_scientific():
    """Create a scientific workflow diagram."""
    # Note: "scientific" preset is applied via compile functions internally
    # when using workflow type with publication-style emphasis
    d = fr.Diagram(type="workflow", title="Experiment Workflow")

    # Typical scientific workflow
    d.add_node("hypothesis", "Hypothesis")
    d.add_node("design", "Experimental Design", emphasis="primary")
    d.add_node("collect", "Data Collection")
    d.add_node("analyze", "Statistical Analysis", emphasis="primary")
    d.add_node("results", "Results", emphasis="success")
    d.add_node("publish", "Publication", emphasis="success")

    # Define flow
    d.add_edge("hypothesis", "design")
    d.add_edge("design", "collect")
    d.add_edge("collect", "analyze")
    d.add_edge("analyze", "results")
    d.add_edge("results", "publish")

    # Feedback loop
    d.add_edge("results", "hypothesis", label="refine", style="dashed")

    mermaid_path = OUT_DIR / "scientific_workflow.mmd"
    d.to_mermaid(mermaid_path)
    print(f"\nCreated scientific diagram: {mermaid_path}")

    return d


def example_decision_tree():
    """Create a decision tree diagram."""
    d = fr.Diagram(type="decision", title="Model Selection")

    # Decision nodes
    d.add_node("start", "Data Type?", shape="diamond")
    d.add_node("numeric", "Sample Size?", shape="diamond")
    d.add_node("categorical", "# Categories?", shape="diamond")

    # Outcome nodes
    d.add_node("linear", "Linear Regression", emphasis="success")
    d.add_node("tree", "Decision Tree", emphasis="success")
    d.add_node("chi2", "Chi-Square Test", emphasis="success")
    d.add_node("fisher", "Fisher's Exact", emphasis="success")

    # Decision paths
    d.add_edge("start", "numeric", label="Continuous")
    d.add_edge("start", "categorical", label="Categorical")
    d.add_edge("numeric", "linear", label="n > 30")
    d.add_edge("numeric", "tree", label="n <= 30")
    d.add_edge("categorical", "chi2", label="> 2")
    d.add_edge("categorical", "fisher", label="= 2")

    mermaid_path = OUT_DIR / "decision_tree.mmd"
    d.to_mermaid(mermaid_path)
    print(f"\nCreated decision tree: {mermaid_path}")

    return d


def example_from_yaml():
    """Load and modify a diagram from YAML specification."""
    # First create a YAML spec
    yaml_content = """
title: Neural Network Architecture
type: workflow
column: single

nodes:
  - id: input
    label: Input Layer
    shape: stadium
  - id: conv1
    label: Conv2D (32)
    emphasis: primary
  - id: pool1
    label: MaxPool
  - id: conv2
    label: Conv2D (64)
    emphasis: primary
  - id: pool2
    label: MaxPool
  - id: flatten
    label: Flatten
  - id: dense
    label: Dense (128)
    emphasis: primary
  - id: output
    label: Softmax
    shape: stadium
    emphasis: success

edges:
  - source: input
    target: conv1
  - source: conv1
    target: pool1
  - source: pool1
    target: conv2
  - source: conv2
    target: pool2
  - source: pool2
    target: flatten
  - source: flatten
    target: dense
  - source: dense
    target: output
"""
    yaml_path = OUT_DIR / "neural_net_spec.yaml"
    yaml_path.write_text(yaml_content)

    # Load and convert
    d = fr.Diagram.from_yaml(yaml_path)
    mermaid_path = OUT_DIR / "neural_net.mmd"
    d.to_mermaid(mermaid_path)

    print(f"\nLoaded from YAML and created: {mermaid_path}")
    print(f"  Nodes: {len(d.spec.nodes)}")
    print(f"  Edges: {len(d.spec.edges)}")

    return d


def list_presets():
    """Show available diagram presets."""
    from figrecipe._diagram import list_presets

    print("\nAvailable diagram presets:")
    for name, desc in list_presets().items():
        print(f"  {name}: {desc}")


if __name__ == "__main__":
    print("=" * 60)
    print("FigRecipe Diagram Examples")
    print("=" * 60)

    list_presets()

    print("\n" + "-" * 60)
    print("1. Programmatic Pipeline Diagram")
    print("-" * 60)
    example_programmatic()

    print("\n" + "-" * 60)
    print("2. Scientific Workflow (SCITEX style)")
    print("-" * 60)
    example_scientific()

    print("\n" + "-" * 60)
    print("3. Decision Tree")
    print("-" * 60)
    example_decision_tree()

    print("\n" + "-" * 60)
    print("4. Load from YAML Specification")
    print("-" * 60)
    example_from_yaml()

    print("\n" + "=" * 60)
    print(f"All outputs saved to: {OUT_DIR}")
    print("=" * 60)
