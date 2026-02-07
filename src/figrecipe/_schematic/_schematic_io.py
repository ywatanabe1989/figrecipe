#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Serialization and deserialization for Schematic diagrams."""

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ._schematic import Schematic


def schematic_to_dict(info: "Schematic") -> Dict[str, Any]:
    """Convert schematic specification to dictionary for serialization.

    Parameters
    ----------
    info : Schematic
        The schematic to serialize.

    Returns
    -------
    dict
        Dictionary representation suitable for YAML recipe.
    """
    return {
        "title": info.title,
        "width_mm": info.width_mm,
        "height_mm": info.height_mm,
        "xlim": list(info.xlim),
        "ylim": list(info.ylim),
        "boxes": [
            {
                "id": box.id,
                "title": box.title,
                "subtitle": box.subtitle,
                "content": box.content,
                "emphasis": box.emphasis,
                "shape": box.shape,
                "fill_color": box.fill_color,
                "border_color": box.border_color,
                "title_color": box.title_color,
                "padding_mm": box.padding_mm,
                "margin_mm": box.margin_mm,
            }
            for box in info._boxes.values()
        ],
        "containers": [
            {
                "id": cid,
                "title": cont.get("title"),
                "children": cont.get("children", []),
                "emphasis": cont.get("emphasis", "muted"),
                "fill_color": cont.get("fill_color"),
                "border_color": cont.get("border_color"),
            }
            for cid, cont in info._containers.items()
        ],
        "arrows": [
            {
                "source": arrow.source,
                "target": arrow.target,
                "source_anchor": arrow.source_anchor,
                "target_anchor": arrow.target_anchor,
                "label": arrow.label,
                "style": arrow.style,
                "color": arrow.color,
                "curve": arrow.curve,
                "linewidth_mm": arrow.linewidth_mm,
            }
            for arrow in info._arrows
        ],
        "positions": {
            pid: {
                "x_mm": pos.x_mm,
                "y_mm": pos.y_mm,
                "width_mm": pos.width_mm,
                "height_mm": pos.height_mm,
            }
            for pid, pos in info._positions.items()
        },
    }


def schematic_from_dict(data: Dict[str, Any]) -> "Schematic":
    """Create Schematic from dictionary (recipe reproduction).

    Parameters
    ----------
    data : dict
        Dictionary from to_dict() or YAML recipe.

    Returns
    -------
    Schematic
        Reconstructed schematic.
    """
    from ._schematic import ArrowSpec, BoxSpec, PositionSpec, Schematic

    width_mm = data.get("width_mm", 200.0)
    height_mm = data.get("height_mm", 120.0)

    schematic = Schematic(
        title=data.get("title"),
        width_mm=width_mm,
        height_mm=height_mm,
    )

    # Restore expanded limits if available (auto_layout may have expanded them)
    if "xlim" in data:
        schematic.xlim = tuple(data["xlim"])
    if "ylim" in data:
        schematic.ylim = tuple(data["ylim"])

    # Restore positions first
    for pid, pos in data.get("positions", {}).items():
        schematic._positions[pid] = PositionSpec(
            x_mm=pos.get("x_mm", 0.0),
            y_mm=pos.get("y_mm", 0.0),
            width_mm=pos.get("width_mm", 0.0),
            height_mm=pos.get("height_mm", 0.0),
        )

    # Restore boxes
    for box_data in data.get("boxes", []):
        schematic._boxes[box_data["id"]] = BoxSpec(
            id=box_data["id"],
            title=box_data["title"],
            subtitle=box_data.get("subtitle"),
            content=box_data.get("content", []),
            emphasis=box_data.get("emphasis", "normal"),
            shape=box_data.get("shape", "rounded"),
            fill_color=box_data.get("fill_color"),
            border_color=box_data.get("border_color"),
            title_color=box_data.get("title_color"),
            padding_mm=box_data.get("padding_mm", 5.0),
            margin_mm=box_data.get("margin_mm", 0.0),
        )

    # Restore containers
    for cont_data in data.get("containers", []):
        schematic._containers[cont_data["id"]] = {
            "title": cont_data.get("title"),
            "children": cont_data.get("children", []),
            "emphasis": cont_data.get("emphasis", "muted"),
            "fill_color": cont_data.get("fill_color"),
            "border_color": cont_data.get("border_color"),
        }

    # Restore arrows
    for arrow_data in data.get("arrows", []):
        schematic._arrows.append(
            ArrowSpec(
                source=arrow_data["source"],
                target=arrow_data["target"],
                source_anchor=arrow_data.get("source_anchor", "auto"),
                target_anchor=arrow_data.get("target_anchor", "auto"),
                label=arrow_data.get("label"),
                style=arrow_data.get("style", "solid"),
                color=arrow_data.get("color"),
                curve=arrow_data.get("curve", 0.0),
                linewidth_mm=arrow_data.get("linewidth_mm", 0.5),
            )
        )

    return schematic


__all__ = ["schematic_to_dict", "schematic_from_dict"]
