#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for figrecipe diagram module."""

import tempfile
from pathlib import Path

import figrecipe as fr
from figrecipe._diagram import (
    Diagram,
    DiagramType,
    get_preset,
    list_presets,
)


class TestDiagramCreation:
    """Test diagram creation and basic operations."""

    def test_create_empty_diagram(self):
        """Test creating an empty diagram."""
        d = Diagram(type="workflow", title="Test")
        assert d.spec.type == DiagramType.WORKFLOW
        assert d.spec.title == "Test"
        assert len(d.spec.nodes) == 0
        assert len(d.spec.edges) == 0

    def test_add_nodes(self):
        """Test adding nodes to diagram."""
        d = Diagram(type="pipeline")
        d.add_node("input", "Input Data")
        d.add_node("output", "Output", shape="rounded", emphasis="success")

        assert len(d.spec.nodes) == 2
        assert d.spec.nodes[0].id == "input"
        assert d.spec.nodes[0].label == "Input Data"
        assert d.spec.nodes[1].emphasis == "success"

    def test_add_edges(self):
        """Test adding edges between nodes."""
        d = Diagram(type="workflow")
        d.add_node("a", "Node A")
        d.add_node("b", "Node B")
        d.add_edge("a", "b", label="flow")

        assert len(d.spec.edges) == 1
        assert d.spec.edges[0].source == "a"
        assert d.spec.edges[0].target == "b"
        assert d.spec.edges[0].label == "flow"

    def test_diagram_types(self):
        """Test all diagram types can be created."""
        for dtype in ["workflow", "decision", "pipeline", "hierarchy", "comparison"]:
            d = Diagram(type=dtype)
            assert d.spec.type == DiagramType(dtype)


class TestMermaidCompilation:
    """Test Mermaid output generation."""

    def test_basic_mermaid_output(self):
        """Test basic Mermaid output."""
        d = Diagram(type="workflow")
        d.add_node("a", "Start")
        d.add_node("b", "End")
        d.add_edge("a", "b")

        mermaid = d.to_mermaid()
        assert "graph" in mermaid
        assert 'a["Start"]' in mermaid
        assert 'b["End"]' in mermaid
        assert "a --> b" in mermaid

    def test_mermaid_with_labels(self):
        """Test Mermaid edges with labels."""
        d = Diagram(type="pipeline")
        d.add_node("x", "X")
        d.add_node("y", "Y")
        d.add_edge("x", "y", label="transform")

        mermaid = d.to_mermaid()
        assert '|"transform"|' in mermaid

    def test_mermaid_save_to_file(self):
        """Test saving Mermaid to file."""
        d = Diagram(type="workflow")
        d.add_node("a", "Test")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.mmd"
            d.to_mermaid(path)
            assert path.exists()
            content = path.read_text()
            assert 'a["Test"]' in content


class TestGraphvizCompilation:
    """Test Graphviz DOT output generation."""

    def test_basic_graphviz_output(self):
        """Test basic Graphviz output."""
        d = Diagram(type="workflow")
        d.add_node("a", "Start")
        d.add_node("b", "End")
        d.add_edge("a", "b")

        dot = d.to_graphviz()
        assert "digraph" in dot
        assert 'a [label="Start"' in dot
        assert 'b [label="End"' in dot
        assert "a -> b" in dot

    def test_graphviz_save_to_file(self):
        """Test saving Graphviz to file."""
        d = Diagram(type="workflow")
        d.add_node("a", "Test")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.dot"
            d.to_graphviz(path)
            assert path.exists()
            content = path.read_text()
            assert 'a [label="Test"' in content


class TestYAMLSerialization:
    """Test YAML import/export."""

    def test_yaml_export(self):
        """Test exporting diagram to YAML."""
        d = Diagram(type="pipeline", title="Test Pipeline")
        d.add_node("a", "A")
        d.add_node("b", "B")
        d.add_edge("a", "b")

        yaml_str = d.to_yaml()
        assert "type: pipeline" in yaml_str
        assert "title: Test Pipeline" in yaml_str

    def test_yaml_roundtrip(self):
        """Test YAML export/import roundtrip."""
        d = Diagram(type="workflow", title="Test")
        d.add_node("x", "Node X", emphasis="primary")
        d.add_node("y", "Node Y")
        d.add_edge("x", "y", label="connect")

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.yaml"
            d.to_yaml(path)

            d2 = Diagram.from_yaml(path)
            assert d2.spec.type == DiagramType.WORKFLOW
            assert d2.spec.title == "Test"
            assert len(d2.spec.nodes) == 2
            assert len(d2.spec.edges) == 1


class TestPresets:
    """Test diagram presets."""

    def test_list_presets(self):
        """Test listing available presets."""
        presets = list_presets()
        assert "workflow" in presets
        assert "decision" in presets
        assert "pipeline" in presets
        assert "scientific" in presets

    def test_get_preset(self):
        """Test getting a specific preset."""
        preset = get_preset("workflow")
        assert preset.mermaid_direction in ["LR", "TB", "RL", "BT"]
        assert "primary" in preset.emphasis_styles

    def test_scientific_preset(self):
        """Test scientific preset has SCITEX colors."""
        preset = get_preset("scientific")
        # SCITEX blue
        assert "#0080C0" in preset.emphasis_styles["primary"]["fill"]


class TestDiagramSplit:
    """Test diagram splitting functionality."""

    def test_split_small_diagram(self):
        """Test that small diagrams don't get split."""
        d = Diagram(type="workflow")
        d.add_node("a", "A")
        d.add_node("b", "B")
        d.add_edge("a", "b")

        parts = d.split(max_nodes=10)
        assert len(parts) == 1

    def test_split_large_diagram(self):
        """Test splitting a large diagram."""
        d = Diagram(type="workflow")
        # Create 15 nodes in a chain
        for i in range(15):
            d.add_node(f"n{i}", f"Node {i}")
        for i in range(14):
            d.add_edge(f"n{i}", f"n{i + 1}")

        # Create groups to enable splitting
        d.set_group("group1", [f"n{i}" for i in range(7)])
        d.set_group("group2", [f"n{i}" for i in range(7, 15)])

        parts = d.split(max_nodes=8, strategy="by_groups")
        # Should split based on groups
        assert len(parts) >= 1


class TestFromMermaid:
    """Test parsing existing Mermaid files."""

    def test_parse_simple_mermaid(self):
        """Test parsing simple Mermaid content."""
        mermaid_content = """graph LR
    A["Start"]
    B["Process"]
    C["End"]
    A --> B
    B --> C
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.mmd"
            path.write_text(mermaid_content)

            d = Diagram.from_mermaid(path)
            assert len(d.spec.nodes) >= 3
            assert len(d.spec.edges) >= 2


class TestDiagramImport:
    """Test that Diagram is properly exported from figrecipe."""

    def test_diagram_in_figrecipe_namespace(self):
        """Test Diagram is accessible from main figrecipe import."""
        assert hasattr(fr, "Diagram")
        d = fr.Diagram(type="workflow")
        assert d is not None


class TestDiagramRender:
    """Test diagram rendering to image files."""

    def test_get_available_backends(self):
        """Test getting available backends."""
        from figrecipe._diagram._render import get_available_backends

        backends = get_available_backends()
        assert "mermaid-cli" in backends
        assert "graphviz" in backends
        assert "mermaid.ink" in backends

        # mermaid.ink should always be available
        assert backends["mermaid.ink"]["available"] is True
        assert "png" in backends["mermaid.ink"]["formats"]
        assert "svg" in backends["mermaid.ink"]["formats"]

    def test_render_with_mermaid_ink(self):
        """Test rendering via mermaid.ink online API."""
        import urllib.error

        import pytest

        d = Diagram(type="workflow")
        d.add_node("a", "Start")
        d.add_node("b", "End")
        d.add_edge("a", "b")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "diagram.png"
            try:
                result = d.render(output_path, backend="mermaid.ink")
                assert result.exists()
                # Check it's a valid image (mermaid.ink returns JPEG for /img endpoint)
                content = result.read_bytes()
                # JPEG magic: b'\xff\xd8\xff' or PNG magic: b'\x89PNG'
                is_jpeg = content[:3] == b"\xff\xd8\xff"
                is_png = content[:4] == b"\x89PNG"
                assert is_jpeg or is_png, f"Expected image format, got: {content[:4]}"
            except urllib.error.HTTPError as e:
                pytest.skip(f"mermaid.ink API unavailable: {e}")

    def test_render_svg_format(self):
        """Test rendering to SVG format."""
        import urllib.error

        import pytest

        d = Diagram(type="pipeline")
        d.add_node("x", "X")
        d.add_node("y", "Y")
        d.add_edge("x", "y")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "diagram.svg"
            try:
                result = d.render(output_path, format="svg", backend="mermaid.ink")
                assert result.exists()
                content = result.read_text()
                assert "<svg" in content
            except urllib.error.HTTPError as e:
                pytest.skip(f"mermaid.ink API unavailable: {e}")
