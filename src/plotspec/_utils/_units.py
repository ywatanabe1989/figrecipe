#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit conversion utilities for plotspec.

Provides conversions between millimeters, inches, and points for precise
figure layout control.

Constants:
    - 1 inch = 25.4 mm
    - 1 inch = 72 points (PostScript points)
    - 1 mm = 72/25.4 points
"""

__all__ = ["mm_to_inch", "inch_to_mm", "mm_to_pt", "pt_to_mm"]

# Conversion constants
MM_PER_INCH = 25.4
PT_PER_INCH = 72.0


def mm_to_inch(mm: float) -> float:
    """Convert millimeters to inches.

    Parameters
    ----------
    mm : float
        Value in millimeters

    Returns
    -------
    float
        Value in inches

    Examples
    --------
    >>> mm_to_inch(25.4)
    1.0
    >>> mm_to_inch(40)  # Nature figure width
    1.5748031496062993
    """
    return mm / MM_PER_INCH


def inch_to_mm(inch: float) -> float:
    """Convert inches to millimeters.

    Parameters
    ----------
    inch : float
        Value in inches

    Returns
    -------
    float
        Value in millimeters

    Examples
    --------
    >>> inch_to_mm(1.0)
    25.4
    """
    return inch * MM_PER_INCH


def mm_to_pt(mm: float) -> float:
    """Convert millimeters to points (PostScript points).

    Parameters
    ----------
    mm : float
        Value in millimeters

    Returns
    -------
    float
        Value in points (1 pt = 1/72 inch)

    Examples
    --------
    >>> mm_to_pt(0.2)  # Typical line thickness
    0.5669291338582677
    >>> mm_to_pt(0.8)  # Typical tick length
    2.267716535433071
    """
    return mm * PT_PER_INCH / MM_PER_INCH


def pt_to_mm(pt: float) -> float:
    """Convert points to millimeters.

    Parameters
    ----------
    pt : float
        Value in points

    Returns
    -------
    float
        Value in millimeters

    Examples
    --------
    >>> pt_to_mm(1.0)
    0.3527777777777778
    """
    return pt * MM_PER_INCH / PT_PER_INCH


if __name__ == "__main__":
    # Test conversions
    print("Unit conversion tests:")
    print(f"  25.4 mm = {mm_to_inch(25.4):.4f} inch")
    print(f"  1 inch = {inch_to_mm(1.0):.1f} mm")
    print(f"  0.2 mm = {mm_to_pt(0.2):.4f} pt")
    print(f"  1 pt = {pt_to_mm(1.0):.4f} mm")
