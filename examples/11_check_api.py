#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-26 06:29:46 (ywatanabe)"
# File: /home/ywatanabe/proj/figrecipe/GITIGNORED/api_check.py


"""Top-level docstring here"""

# Imports
import scitex as stx

import figrecipe as fr

# # Parameters
# CONFIG = stx.io.load_configs() # For imported files using `./config/*.yaml`


# Functions and Classes
@stx.session
def main(
    # arg1,
    # kwarg1="value1",
    CONFIG=stx.session.INJECTED,
    plt=stx.session.INJECTED,
    COLORS=stx.session.INJECTED,
    rng=stx.session.INJECTED,
    logger=stx.session.INJECTED,
):
    """Help message for `$ python __file__ --help`"""
    fr_df = stx.introspect.inspect_module(fr)
    stx.io.save(fr_df, "figrecipe.csv")

    fig, ax = fr.subplots()

    fig_df = stx.introspect.inspect_module(fig)
    stx.io.save(fig_df, "fig.csv")

    ax_df = stx.introspect.inspect_module(ax)
    stx.io.save(ax_df, "ax.csv")

    _fig, axes = fr.subplots(2, 2)

    axes_df = stx.introspect.inspect_module(axes)
    stx.io.save(axes_df, "axes.csv")
    return 0


if __name__ == "__main__":
    main()

# EOF
