#!/usr/bin/env python3
# Timestamp: 2026-02-09
# File: src/figrecipe/colors/_PARAMS.py

"""Color parameter definitions — RGB, RGBA, HEX palettes."""

# RGB
RGB = {
    "white": [255, 255, 255],
    "black": [0, 0, 0],
    "blue": [0, 128, 192],
    "red": [255, 70, 50],
    "pink": [255, 150, 200],
    "green": [20, 180, 20],
    "yellow": [230, 160, 20],
    "gray": [128, 128, 128],
    "grey": [128, 128, 128],
    "purple": [200, 50, 255],
    "lightblue": [20, 200, 200],
    "brown": [128, 0, 0],
    "navy": [0, 0, 100],
    "orange": [228, 94, 50],
}

RGB_NORM = {
    k: [round(r / 255, 2), round(g / 255, 2), round(b / 255, 2)]
    for k, (r, g, b) in RGB.items()
}

# RGBA
DEF_ALPHA = 0.9
RGBA = {k: [r, g, b, DEF_ALPHA] for k, (r, g, b) in RGB.items()}
RGBA_NORM = {k: [r, g, b, DEF_ALPHA] for k, (r, g, b) in RGB_NORM.items()}
RGBA_NORM_FOR_CYCLE = {
    k: v for k, v in RGBA_NORM.items() if k not in ["white", "grey", "black"]
}

# HEX
HEX = {
    "blue": "#0080C0",
    "red": "#FF4632",
    "pink": "#FF96C8",
    "green": "#14B414",
    "yellow": "#E6A014",
    "gray": "#808080",
    "grey": "#808080",
    "purple": "#C832FF",
    "lightblue": "#14C8C8",
    "brown": "#800000",
    "navy": "#000064",
    "orange": "#E45E32",
}

PARAMS = dict(
    RGB=RGB,
    RGBA=RGBA,
    RGBA_NORM=RGBA_NORM,
    RGBA_NORM_FOR_CYCLE=RGBA_NORM_FOR_CYCLE,
    HEX=HEX,
)

# EOF
