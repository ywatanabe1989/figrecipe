#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Image processing for hitmap generation."""

from typing import Any, Dict

import numpy as np
from matplotlib.image import AxesImage

from .._colors import id_to_rgb


def process_images(
    ax,
    ax_idx: int,
    element_id: int,
    color_map: Dict[str, Any],
    ax_info: Dict[str, Any],
    original_props: Dict[str, Any] = None,
) -> int:
    """Process images on an axes.

    Replaces image data with solid hitmap color so pixel-based element
    detection works for composed figures that embed panels via imshow.

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

            rgb = id_to_rgb(element_id)

            # Replace image data with solid hitmap color for pixel detection
            if original_props is not None:
                original_data = img.get_array()
                original_props[key] = {"data": original_data.copy()}

                # Build solid-color array matching original shape
                shape = original_data.shape
                solid = np.zeros((*shape[:2], 3), dtype=np.uint8)
                solid[:, :, 0] = rgb[0]
                solid[:, :, 1] = rgb[1]
                solid[:, :, 2] = rgb[2]
                img.set_data(solid)
                img.set_clim(0, 255)

            color_map[key] = {
                "id": element_id,
                "type": "image",
                "label": label,
                "ax_index": ax_idx,
                "rgb": list(rgb),
                "call_id": call_id,
            }
            element_id += 1

    return element_id


__all__ = ["process_images"]

# EOF
