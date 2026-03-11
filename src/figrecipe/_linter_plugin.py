"""Linter plugin for figrecipe: figure/layout and plot rules (FM001-FM009, P001-P005).

Registered via entry point 'scitex_linter.plugins' so scitex-linter
discovers these rules automatically when figrecipe is installed.

FM rules flag inch-based matplotlib patterns and suggest mm-based alternatives.
P rules flag bare matplotlib calls and suggest scitex/figrecipe tracked variants.
"""


def get_plugin():
    """Return figrecipe linter rules, call mappings, axes hints, and checkers."""
    from scitex_linter._rules._base import Rule

    # ------------------------------------------------------------------
    # FM: Figure / Millimeter rules (FM001-FM009)
    # ------------------------------------------------------------------
    FM001 = Rule(
        id="STX-FM001",
        severity="warning",
        category="figure",
        message="`figsize=` detected — inch-based figure sizing is imprecise for publications",
        suggestion=(
            "Use mm-based sizing: `stx.plt.subplots(axes_width_mm=40, axes_height_mm=28)` "
            "or `fig, ax = fr.subplots(axes_width_mm=40, axes_height_mm=28)` for precise control."
        ),
        requires="figrecipe",
    )

    FM002 = Rule(
        id="STX-FM002",
        severity="warning",
        category="figure",
        message="`tight_layout()` detected — layout is unpredictable across plot types",
        suggestion=(
            "Use mm-based margins: `stx.plt.subplots(margin_left_mm=15, margin_bottom_mm=12)` "
            "for deterministic layout control."
        ),
        requires="figrecipe",
    )

    FM003 = Rule(
        id="STX-FM003",
        severity="warning",
        category="figure",
        message='`bbox_inches="tight"` detected — can crop important elements unpredictably',
        suggestion=(
            "Use `fr.save(fig, './plot.png')` or `stx.io.save(fig, './plot.png')` "
            "which handle cropping intelligently."
        ),
        requires="figrecipe",
    )

    FM004 = Rule(
        id="STX-FM004",
        severity="info",
        category="figure",
        message="`constrained_layout=True` detected — conflicts with mm-based layout control",
        suggestion="Use mm-based layout from `stx.plt.subplots()` instead of constrained_layout.",
        requires="figrecipe",
    )

    FM005 = Rule(
        id="STX-FM005",
        severity="info",
        category="figure",
        message="`subplots_adjust()` with hardcoded fractions — fragile across figure sizes",
        suggestion=(
            "Use mm-based spacing: `stx.plt.subplots(space_w_mm=8, space_h_mm=10)` "
            "for size-independent layout."
        ),
        requires="figrecipe",
    )

    FM006 = Rule(
        id="STX-FM006",
        severity="info",
        category="figure",
        message="`plt.savefig()` detected — no provenance tracking",
        suggestion=(
            "Use `fr.save(fig, './plot.png')` or `stx.io.save(fig, './plot.png')` "
            "for recipe tracking and provenance."
        ),
        requires="figrecipe",
    )

    FM007 = Rule(
        id="STX-FM007",
        severity="info",
        category="figure",
        message="`rcParams` direct modification detected — hard to maintain across figures",
        suggestion="Use figrecipe style presets: `fr.load_style('SCITEX')` for consistent styling.",
        requires="figrecipe",
    )

    FM008 = Rule(
        id="STX-FM008",
        severity="warning",
        category="figure",
        message="`set_size_inches()` detected — bypasses mm-based layout control",
        suggestion=(
            "Use mm-based sizing: `fr.subplots(axes_width_mm=40, axes_height_mm=28)` "
            "or `stx.plt.subplots(axes_width_mm=40, axes_height_mm=28)` for precise control."
        ),
        requires="figrecipe",
    )

    FM009 = Rule(
        id="STX-FM009",
        severity="warning",
        category="figure",
        message="`ax.set_position()` detected — conflicts with mm-based layout control",
        suggestion=(
            "Use mm-based margins: `fr.subplots(margin_left_mm=15, margin_bottom_mm=12)` "
            "or `stx.plt.subplots(margin_left_mm=15, margin_bottom_mm=12)` for deterministic layout."
        ),
        requires="figrecipe",
    )

    # ------------------------------------------------------------------
    # P: Plot rules (P001-P005)
    # ------------------------------------------------------------------
    P001 = Rule(
        id="STX-P001",
        severity="info",
        category="plot",
        message="`ax.plot()` — consider `ax.stx_line()` for automatic CSV data export",
        suggestion="Replace `ax.plot(x, y)` with `ax.stx_line(x, y)` for tracked plotting.",
        requires="scitex",
    )

    P002 = Rule(
        id="STX-P002",
        severity="info",
        category="plot",
        message="`ax.scatter()` — consider `ax.stx_scatter()` for automatic CSV data export",
        suggestion="Replace `ax.scatter(x, y)` with `ax.stx_scatter(x, y)` for tracked plotting.",
        requires="scitex",
    )

    P003 = Rule(
        id="STX-P003",
        severity="info",
        category="plot",
        message="`ax.bar()` — consider `ax.stx_bar()` for automatic sample size annotation",
        suggestion="Replace `ax.bar(x, y)` with `ax.stx_bar(x, y)` for tracked plotting.",
        requires="scitex",
    )

    P004 = Rule(
        id="STX-P004",
        severity="info",
        category="plot",
        message="`plt.show()` is non-reproducible in batch/CI environments",
        suggestion="Remove `plt.show()` — figures are auto-saved in session output directory.",
    )

    P005 = Rule(
        id="STX-P005",
        severity="info",
        category="plot",
        message="`print()` inside @stx.session — use `logger` for tracked logging",
        suggestion="Replace `print(msg)` with `logger.info(msg)` (injected by @stx.session).",
        requires="scitex",
    )

    # ------------------------------------------------------------------
    # FMChecker: AST-level checker for FM rules that need structural
    # analysis (e.g. figsize= kwarg, tight_layout(), rcParams[...] =).
    # Import is deferred so figrecipe can be installed without scitex-linter.
    # ------------------------------------------------------------------
    try:
        from scitex_linter._fm_checker import FMChecker

        checkers = [FMChecker]
    except ImportError:
        checkers = []

    return {
        "rules": [
            FM001,
            FM002,
            FM003,
            FM004,
            FM005,
            FM006,
            FM007,
            FM008,
            FM009,
            P001,
            P002,
            P003,
            P004,
            P005,
        ],
        "call_rules": {
            # FM rules via call patterns
            (None, "tight_layout"): FM002,
            (None, "subplots_adjust"): FM005,
            (None, "savefig"): FM006,
            (None, "set_size_inches"): FM008,
            (None, "set_position"): FM009,
            # P004: plt.show()
            (None, "show"): P004,
        },
        # Axes method hints: fired when bare ax.plot() / ax.scatter() / ax.bar()
        # is detected without an stx/fr prefix.
        "axes_hints": {
            "plot": P001,
            "scatter": P002,
            "bar": P003,
        },
        "checkers": checkers,
    }
