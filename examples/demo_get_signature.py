#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-23 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/examples/get_signature.py

"""Example: Extract matplotlib function signatures with deep inspection.

This script demonstrates the signature extraction functionality that parses
*args and **kwargs from docstrings and expands them to actual parameters.
"""

from pathlib import Path

from ruamel.yaml import YAML

from figrecipe._signatures import (
    get_defaults,
    get_signature,
    list_plotting_methods,
    validate_kwargs,
)


def main():
    """Generate SIGNATURES.yaml with all matplotlib plotting function signatures."""
    output_dir = Path(__file__).parent.parent / "outputs" / "examples"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "SIGNATURES.yaml"

    # Get all plotting methods
    methods = list_plotting_methods()
    print(f"Found {len(methods)} plotting methods")

    # Build signatures dict
    signatures = {}
    for method in methods:
        sig = get_signature(method)
        signatures[method] = {
            "args": sig["args"],
            "kwargs": {k: v for k, v in sig["kwargs"].items()},
        }

    # Save to YAML
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 120
    with open(output_path, "w") as f:
        yaml.dump(signatures, f)

    print(f"Saved: {output_path}")

    # Demo: Show a few examples
    print("\n" + "=" * 60)
    print("EXAMPLES")
    print("=" * 60)

    for method in ["plot", "scatter", "bar", "hist", "imshow"]:
        sig = get_signature(method)
        print(f"\n--- {method}() ---")
        print("Args:")
        for arg in sig["args"]:
            opt = " (optional)" if arg.get("optional") else ""
            print(f"  {arg['name']}: {arg.get('type')}{opt}")
        print(f"Kwargs: {len(sig['kwargs'])} parameters")
        # Show first 5 kwargs
        for i, (name, info) in enumerate(sig["kwargs"].items()):
            if i >= 5:
                print(f"  ... and {len(sig['kwargs']) - 5} more")
                break
            default = info.get("default", "N/A")
            print(f"  {name}: {info.get('type')} (default: {default})")

    # Demo: validate_kwargs
    print("\n" + "=" * 60)
    print("VALIDATE KWARGS EXAMPLE")
    print("=" * 60)
    result = validate_kwargs(
        "plot", {"color": "red", "linewidth": 2, "unknown_param": 123}
    )
    print("Input: {'color': 'red', 'linewidth': 2, 'unknown_param': 123}")
    print(f"Valid: {result['valid']}")
    print(f"Unknown: {result['unknown']}")

    # Demo: get_defaults
    print("\n" + "=" * 60)
    print("GET DEFAULTS EXAMPLE")
    print("=" * 60)
    defaults = get_defaults("plot")
    print(f"plot() has {len(defaults)} default values")
    for key in ["linestyle", "linewidth", "marker", "alpha", "label"]:
        print(f"  {key}: {defaults.get(key)}")

    return 0


if __name__ == "__main__":
    main()

# EOF
