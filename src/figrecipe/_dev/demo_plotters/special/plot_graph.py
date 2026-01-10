#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""graph: network/graph visualization demo."""


def plot_graph(plt, rng, ax=None):
    """Graph/network visualization demo.

    Demonstrates: ax.graph() with NetworkX
    """
    try:
        import networkx as nx
    except ImportError:
        # If networkx not available, create a simple placeholder
        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig
        ax.text(0.5, 0.5, "networkx not installed", ha="center", va="center")
        ax.set_title("graph")
        ax.axis("off")
        return fig, ax

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure() if hasattr(ax, "get_figure") else ax.fig

    # Create a sample graph
    G = nx.karate_club_graph()

    # Add node attributes for visualization
    for node in G.nodes():
        G.nodes[node]["size"] = G.degree(node) * 10
        G.nodes[node]["label"] = str(node)

    # Draw the graph
    ax.graph(
        G,
        layout="spring",
        seed=42,
        node_size="size",
        node_color="#0080c0",
        node_alpha=0.8,
        edge_color="gray",
        edge_alpha=0.3,
        labels=False,
        id="network",
    )

    ax.set_title("graph")
    return fig, ax


# EOF
