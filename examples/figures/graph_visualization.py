#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-10 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/figures/graph_visualization.py

"""Demo script for graph visualization features.

Shows various graph types and styling options using networkx integration.

Requirements:
    pip install figrecipe[graph]
    # or
    pip install networkx

Outputs saved to ./graph_visualization_out/*.{png,yaml}
"""

import matplotlib

matplotlib.use("Agg")

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")

import matplotlib.pyplot as plt

try:
    import networkx as nx
except ImportError:
    print("This example requires networkx. Install with: pip install networkx")
    sys.exit(1)

import figrecipe as fr

OUTPUT_DIR = Path(__file__).parent / "graph_visualization_out"


def close_fig(fig):
    """Close figure properly."""
    plt.close("all")


def example_basic_graph():
    """Basic graph with default styling."""
    G = nx.karate_club_graph()

    fig, ax = fr.subplots()
    ax.graph(G, seed=42, id="karate_basic")
    ax.set_title("Karate Club Graph (Basic)")

    return fig, "basic_graph"


def example_social_network():
    """Social network with community coloring."""
    G = nx.karate_club_graph()

    # Add community attribute
    for n in G.nodes():
        G.nodes[n]["community"] = 0 if n < 17 else 1
        G.nodes[n]["degree"] = G.degree(n)

    fig, ax = fr.subplots()
    ax.graph(
        G,
        preset="social",
        node_color="community",
        node_size="degree",
        colormap="tab10",
        seed=42,
        id="social_network",
    )
    ax.set_title("Social Network (Community Detection)")

    return fig, "social_network"


def example_citation_network():
    """Citation/dependency network."""
    G = nx.DiGraph()
    G.add_edges_from([
        ("Paper A", "Paper B"),
        ("Paper A", "Paper C"),
        ("Paper B", "Paper D"),
        ("Paper C", "Paper D"),
        ("Paper D", "Paper E"),
    ])

    fig, ax = fr.subplots()
    ax.graph(
        G,
        preset="citation",
        labels=True,
        seed=42,
        id="citation",
    )
    ax.set_title("Citation Network")

    return fig, "citation_network"


def example_hierarchical():
    """Hierarchical DAG layout."""
    G = nx.DiGraph()
    G.add_edges_from([
        ("root", "child1"),
        ("root", "child2"),
        ("child1", "grandchild1"),
        ("child1", "grandchild2"),
        ("child2", "grandchild3"),
    ])

    fig, ax = fr.subplots()
    ax.graph(
        G,
        layout="hierarchical",
        arrows=True,
        labels=True,
        node_color="#2ecc71",
        id="hierarchical",
    )
    ax.set_title("Hierarchical Layout (DAG)")

    return fig, "hierarchical"


def example_layouts():
    """Compare different layout algorithms."""
    G = nx.petersen_graph()

    layouts = ["spring", "circular", "kamada_kawai", "shell", "spectral", "spiral"]

    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.flatten()

    for ax, layout in zip(axes, layouts):
        # Use fr.subplots for recording, but for comparison we use matplotlib directly
        from figrecipe._graph import draw_graph

        draw_graph(ax, G, layout=layout, seed=42)
        ax.set_title(f"Layout: {layout}")

    fig.suptitle("Layout Algorithm Comparison (Petersen Graph)", fontsize=14)
    fig.tight_layout()

    return fig, "layouts_comparison"


def example_weighted_edges():
    """Graph with weighted edges."""
    G = nx.Graph()
    G.add_edge("A", "B", weight=1.0)
    G.add_edge("B", "C", weight=2.0)
    G.add_edge("C", "D", weight=3.0)
    G.add_edge("D", "A", weight=1.5)
    G.add_edge("A", "C", weight=2.5)

    fig, ax = fr.subplots()
    ax.graph(
        G,
        edge_width="weight",
        labels=True,
        node_size=300,
        seed=42,
        id="weighted_edges",
    )
    ax.set_title("Weighted Edges")

    return fig, "weighted_edges"


def example_minimal_style():
    """Minimal academic style."""
    G = nx.random_geometric_graph(30, 0.3, seed=42)

    fig, ax = fr.subplots()
    ax.graph(
        G,
        preset="minimal",
        seed=42,
        id="minimal_style",
    )
    ax.set_title("Minimal Style (Geometric Random Graph)")

    return fig, "minimal_style"


def example_roundtrip():
    """Demonstrate save/reproduce roundtrip."""
    G = nx.karate_club_graph()

    # Create and save
    fig, ax = fr.subplots()
    ax.graph(G, layout="spring", seed=42, node_color="#e74c3c", id="roundtrip_test")
    ax.set_title("Original Graph")

    recipe_path = OUTPUT_DIR / "roundtrip_test.yaml"
    fr.save(fig, recipe_path, validate=False, verbose=False)
    close_fig(fig)

    # Reproduce
    fig2, ax2 = fr.reproduce(recipe_path)

    return fig2, "roundtrip_reproduced"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fr.load_style("SCITEX")

    examples = [
        example_basic_graph,
        example_social_network,
        example_citation_network,
        example_hierarchical,
        example_weighted_edges,
        example_minimal_style,
        example_roundtrip,
        example_layouts,
    ]

    print("Generating graph visualization examples...")
    for example_func in examples:
        try:
            fig, name = example_func()
            out_path = OUTPUT_DIR / f"{name}.png"
            if hasattr(fig, "_recorder"):
                # RecordingFigure
                fr.save(fig, out_path, validate=False, verbose=False)
            else:
                # Regular matplotlib figure
                fig.savefig(out_path, dpi=150, bbox_inches="tight")
            print(f"  Saved: {out_path}")
            close_fig(fig)
        except Exception as e:
            print(f"  Failed: {example_func.__name__} - {e}")

    print(f"\nAll examples saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

# EOF
