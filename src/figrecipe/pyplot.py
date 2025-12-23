#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drop-in replacement for matplotlib.pyplot with recording capabilities.

This module provides a convenient way to use figrecipe as a direct replacement
for matplotlib.pyplot. Simply change your import statement:

    # Before (standard matplotlib)
    import matplotlib.pyplot as plt

    # After (figrecipe with recording)
    import figrecipe.pyplot as plt

All your existing code will work unchanged, but figures created with
plt.subplots() will automatically have recording capabilities.

Examples
--------
>>> import figrecipe.pyplot as plt
>>> import numpy as np
>>>
>>> x = np.linspace(0, 10, 100)
>>> y = np.sin(x)
>>>
>>> fig, ax = plt.subplots()  # Recording-enabled
>>> ax.plot(x, y, color='red', id='sine_wave')
>>> fig.save_recipe('my_figure.yaml')  # Save as recipe
>>>
>>> # All other pyplot functions work as usual
>>> plt.show()
>>> plt.savefig('output.png')
"""

import matplotlib.pyplot as _plt
from matplotlib.pyplot import *  # noqa: F401, F403

from . import save as _ps_save

# Import figrecipe functionality
from . import subplots as _ps_subplots
from ._wrappers import RecordingFigure

# Override subplots with recording-enabled version
subplots = _ps_subplots


def figure(*args, **kwargs):
    """Create a new figure with optional recording support.

    This is a pass-through to matplotlib.pyplot.figure().
    For recording support, use subplots() instead.

    Parameters
    ----------
    *args, **kwargs
        Arguments passed to matplotlib.pyplot.figure().

    Returns
    -------
    matplotlib.figure.Figure
        The created figure.
    """
    return _plt.figure(*args, **kwargs)


def save(fig, path, **kwargs):
    """Save a figure (recipe for RecordingFigure, or standard save).

    Parameters
    ----------
    fig : RecordingFigure or Figure
        Figure to save. If RecordingFigure, saves as recipe.
        Otherwise, saves as image using savefig().
    path : str or Path
        Output path. Use .yaml for recipe format.
    **kwargs
        Additional arguments for save.

    Returns
    -------
    Path or tuple
        Saved path (and ValidationResult if validate=True).
    """
    if isinstance(fig, RecordingFigure):
        return _ps_save(fig, path, **kwargs)
    else:
        fig.savefig(path, **kwargs)
        return path


# Expose commonly used functions explicitly for IDE support
show = _plt.show
savefig = _plt.savefig


def close(fig=None):
    """Close a figure window.

    Parameters
    ----------
    fig : None, int, str, Figure, or RecordingFigure
        The figure to close. See matplotlib.pyplot.close() for details.
        RecordingFigure is automatically unwrapped to the underlying Figure.
    """
    if isinstance(fig, RecordingFigure):
        _plt.close(fig.fig)
    else:
        _plt.close(fig)


clf = _plt.clf
cla = _plt.cla
gcf = _plt.gcf
gca = _plt.gca
subplot = _plt.subplot
tight_layout = _plt.tight_layout
suptitle = _plt.suptitle
xlabel = _plt.xlabel
ylabel = _plt.ylabel
title = _plt.title
legend = _plt.legend
xlim = _plt.xlim
ylim = _plt.ylim
grid = _plt.grid
plot = _plt.plot
scatter = _plt.scatter
bar = _plt.bar
hist = _plt.hist
imshow = _plt.imshow
contour = _plt.contour
contourf = _plt.contourf
colorbar = _plt.colorbar
axhline = _plt.axhline
axvline = _plt.axvline
text = _plt.text
annotate = _plt.annotate
fill_between = _plt.fill_between
errorbar = _plt.errorbar
boxplot = _plt.boxplot
violinplot = _plt.violinplot
pie = _plt.pie
stem = _plt.stem
step = _plt.step
stackplot = _plt.stackplot
streamplot = _plt.streamplot
quiver = _plt.quiver
barbs = _plt.barbs
hexbin = _plt.hexbin
pcolormesh = _plt.pcolormesh
tripcolor = _plt.tripcolor
tricontour = _plt.tricontour
tricontourf = _plt.tricontourf
spy = _plt.spy
matshow = _plt.matshow
specgram = _plt.specgram
psd = _plt.psd
csd = _plt.csd
cohere = _plt.cohere
magnitude_spectrum = _plt.magnitude_spectrum
angle_spectrum = _plt.angle_spectrum
phase_spectrum = _plt.phase_spectrum
xcorr = _plt.xcorr
acorr = _plt.acorr
semilogy = _plt.semilogy
semilogx = _plt.semilogx
loglog = _plt.loglog
polar = _plt.polar
subplot2grid = _plt.subplot2grid
subplot_mosaic = _plt.subplot_mosaic
subplots_adjust = _plt.subplots_adjust
rc = _plt.rc
rcdefaults = _plt.rcdefaults
rcParams = _plt.rcParams
style = _plt.style
cm = _plt.cm
get_cmap = _plt.get_cmap
colormaps = _plt.colormaps


__all__ = [
    # Core functions (recording-enabled)
    "subplots",
    "figure",
    "save",
    # Display
    "show",
    "savefig",
    "close",
    "clf",
    "cla",
    # Getters
    "gcf",
    "gca",
    # Layout
    "subplot",
    "subplot2grid",
    "subplot_mosaic",
    "subplots_adjust",
    "tight_layout",
    # Labels and titles
    "suptitle",
    "xlabel",
    "ylabel",
    "title",
    "legend",
    # Limits
    "xlim",
    "ylim",
    # Grid
    "grid",
    # Plot types
    "plot",
    "scatter",
    "bar",
    "hist",
    "imshow",
    "contour",
    "contourf",
    "colorbar",
    "axhline",
    "axvline",
    "text",
    "annotate",
    "fill_between",
    "errorbar",
    "boxplot",
    "violinplot",
    "pie",
    "stem",
    "step",
    "stackplot",
    "streamplot",
    "quiver",
    "barbs",
    "hexbin",
    "pcolormesh",
    "tripcolor",
    "tricontour",
    "tricontourf",
    "spy",
    "matshow",
    "specgram",
    "psd",
    "csd",
    "cohere",
    "magnitude_spectrum",
    "angle_spectrum",
    "phase_spectrum",
    "xcorr",
    "acorr",
    # Log scale
    "semilogy",
    "semilogx",
    "loglog",
    "polar",
    # Configuration
    "rc",
    "rcdefaults",
    "rcParams",
    "style",
    # Colormaps
    "cm",
    "get_cmap",
    "colormaps",
]
