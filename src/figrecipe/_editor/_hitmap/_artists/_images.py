#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Image processing for hitmap generation."""

from typing import Any, Dict

from matplotlib.image import AxesImage

from .._colors import id_to_rgb


def process_images(
    ax,
    ax_idx: int,
    element_id: int,
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
) -> int:
    """Process images on an axes.

    Returns updated element_id.
    """
    ax_call_ids = ax_info.get("call_ids", {})

    imshow_ids = list(ax_call_ids.get("imshow", []))
    specgram_ids = list(ax_call_ids.get("specgram", []))
    contourf_ids = list(ax_call_ids.get("contourf", []))

    image_idx = 0

    for i, img in enumerate(ax.images):
        if isinstance(img, AxesImage):
            if not img.get_visible():
                continue

            key = f"ax{ax_idx}_image{i}"

            call_id = None
            label = f"image_{i}"

            if image_idx < len(imshow_ids):
                call_id = imshow_ids[image_idx]
                label = call_id
            elif image_idx < len(specgram_ids):
                call_id = specgram_ids[image_idx]
                label = call_id
            elif image_idx < len(contourf_ids):
                call_id = contourf_ids[image_idx]
                label = call_id

            image_idx += 1

            color_map[key] = {
                "id": element_id,
                "type": "image",
                "label": label,
                "ax_index": ax_idx,
                "rgb": list(id_to_rgb(element_id)),
                "call_id": call_id,
            }
            element_id += 1

    return element_id


__all__ = ["process_images"]

# EOF
