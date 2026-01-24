#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MCP tools for diagram creation and manipulation."""

from typing import Any, Dict, Optional


def register_diagram_tools(mcp):
    """Register diagram tools with the MCP server."""

    @mcp.tool
    def diagram_create(
        spec_dict: Optional[Dict[str, Any]] = None,
        spec_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a diagram from a YAML specification file or dictionary.

        Parameters
        ----------
        spec_dict : dict, optional
            Dictionary with diagram specification.
        spec_path : str, optional
            Path to YAML specification file.

        Returns
        -------
        dict
            Result with 'mermaid' and 'graphviz' output strings.
        """
        from .._diagram import Diagram

        if spec_path:
            d = Diagram.from_yaml(spec_path)
        elif spec_dict:
            d = Diagram.from_dict(spec_dict)
        else:
            raise ValueError("Either spec_dict or spec_path must be provided")

        return {
            "mermaid": d.to_mermaid(),
            "graphviz": d.to_graphviz(),
            "nodes": len(d.spec.nodes),
            "edges": len(d.spec.edges),
            "success": True,
        }

    @mcp.tool
    def diagram_compile_mermaid(
        spec_dict: Optional[Dict[str, Any]] = None,
        spec_path: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compile diagram specification to Mermaid format.

        Parameters
        ----------
        spec_dict : dict, optional
            Dictionary with diagram specification.
        spec_path : str, optional
            Path to YAML specification file.
        output_path : str, optional
            Path to save .mmd file.

        Returns
        -------
        dict
            Result with 'mermaid' output and 'output_path'.
        """
        from .._diagram import Diagram

        if spec_path:
            d = Diagram.from_yaml(spec_path)
        elif spec_dict:
            d = Diagram.from_dict(spec_dict)
        else:
            raise ValueError("Either spec_dict or spec_path must be provided")

        mermaid = d.to_mermaid(output_path)

        return {"mermaid": mermaid, "output_path": output_path, "success": True}

    @mcp.tool
    def diagram_compile_graphviz(
        spec_dict: Optional[Dict[str, Any]] = None,
        spec_path: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Compile diagram specification to Graphviz DOT format.

        Parameters
        ----------
        spec_dict : dict, optional
            Dictionary with diagram specification.
        spec_path : str, optional
            Path to YAML specification file.
        output_path : str, optional
            Path to save .dot file.

        Returns
        -------
        dict
            Result with 'graphviz' output and 'output_path'.
        """
        from .._diagram import Diagram

        if spec_path:
            d = Diagram.from_yaml(spec_path)
        elif spec_dict:
            d = Diagram.from_dict(spec_dict)
        else:
            raise ValueError("Either spec_dict or spec_path must be provided")

        graphviz = d.to_graphviz(output_path)

        return {"graphviz": graphviz, "output_path": output_path, "success": True}

    @mcp.tool
    def diagram_list_presets() -> Dict[str, Any]:
        """List available diagram presets (workflow, decision, pipeline, scientific).

        Returns
        -------
        dict
            Dictionary with preset names and descriptions.
        """
        from .._diagram import list_presets as list_diagram_presets

        presets = list_diagram_presets()
        return {"presets": presets, "count": len(presets)}

    @mcp.tool
    def diagram_get_preset(preset_name: str) -> Dict[str, Any]:
        """Get a diagram preset configuration by name.

        Parameters
        ----------
        preset_name : str
            Name of the preset (workflow, decision, pipeline, scientific).

        Returns
        -------
        dict
            Preset configuration including mermaid/graphviz settings.
        """
        from .._diagram import get_preset

        preset = get_preset(preset_name)
        return {
            "name": preset_name,
            "mermaid_direction": preset.mermaid_direction,
            "mermaid_theme": preset.mermaid_theme,
            "graphviz_rankdir": preset.graphviz_rankdir,
            "graphviz_ranksep": preset.graphviz_ranksep,
            "graphviz_nodesep": preset.graphviz_nodesep,
            "emphasis_styles": preset.emphasis_styles,
        }

    @mcp.tool
    def diagram_split(
        spec_path: str,
        max_nodes_per_part: int = 10,
        strategy: str = "by_groups",
    ) -> Dict[str, Any]:
        """Split a large diagram into smaller parts for multi-column layouts.

        Parameters
        ----------
        spec_path : str
            Path to YAML specification file.
        max_nodes_per_part : int
            Maximum nodes per part (default: 10).
        strategy : str
            Split strategy: 'by_groups' or 'by_articulation'.

        Returns
        -------
        dict
            Result with split diagram parts.
        """
        from .._diagram import Diagram

        d = Diagram.from_yaml(spec_path)
        parts = d.split(max_nodes=max_nodes_per_part, strategy=strategy)

        return {
            "parts": [
                {
                    "title": p.spec.title,
                    "nodes": len(p.spec.nodes),
                    "edges": len(p.spec.edges),
                    "mermaid": p.to_mermaid(),
                }
                for p in parts
            ],
            "num_parts": len(parts),
            "success": True,
        }

    @mcp.tool
    def diagram_get_paper_modes() -> Dict[str, Any]:
        """Get available paper layout modes and their constraints.

        Returns
        -------
        dict
            Paper modes with width constraints.
        """
        return {
            "modes": {
                "single_column": {
                    "max_width_mm": 170,
                    "description": "Full page width for single-column layouts",
                },
                "double_column": {
                    "max_width_mm": 85,
                    "description": "Half page width for two-column layouts",
                },
            },
            "paper_modes": {
                "draft": "Full details, visible bidirectional arrows, medium spacing",
                "publication": "Compact layout, return edges hidden, tight spacing",
            },
        }

    @mcp.tool
    def diagram_render(
        spec_dict: Optional[Dict[str, Any]] = None,
        spec_path: Optional[str] = None,
        output_path: str = "",
        format: str = "png",
        backend: str = "auto",
        scale: float = 2.0,
    ) -> Dict[str, Any]:
        """Render diagram to image file (PNG, SVG, PDF).

        Parameters
        ----------
        spec_dict : dict, optional
            Dictionary with diagram specification.
        spec_path : str, optional
            Path to YAML specification file.
        output_path : str
            Path to save the output image file.
        format : str
            Output format: 'png', 'svg', or 'pdf'.
        backend : str
            Rendering backend: 'mermaid-cli', 'graphviz', 'mermaid.ink', or 'auto'.
        scale : float
            Scale factor for output (default: 2.0).

        Returns
        -------
        dict
            Result with 'output_path' and 'success'.
        """
        from .._diagram import Diagram

        if not output_path:
            raise ValueError("output_path is required")

        if spec_path:
            d = Diagram.from_yaml(spec_path)
        elif spec_dict:
            d = Diagram.from_dict(spec_dict)
        else:
            raise ValueError("Either spec_dict or spec_path must be provided")

        # Use Diagram.render() method - same as CLI
        result_path = d.render(output_path, format=format, backend=backend, scale=scale)

        return {
            "output_path": str(result_path),
            "format": format,
            "backend": backend,
            "success": True,
        }

    @mcp.tool
    def diagram_get_backends() -> Dict[str, Any]:
        """List available rendering backends and their status.

        Returns
        -------
        dict
            Dictionary with backend availability, installation instructions,
            and supported formats.
        """
        from .._diagram import get_available_backends

        backends = get_available_backends()
        available_count = sum(1 for b in backends.values() if b["available"])

        return {
            "backends": backends,
            "available_count": available_count,
            "total_count": len(backends),
        }
