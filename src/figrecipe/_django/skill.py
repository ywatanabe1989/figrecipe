"""Skill registration for Figrecipe editor.

Registers with the SciTeX Cloud LLM skill system when running inside
the platform. Silently skips when running standalone (no llm_app available).
"""

try:
    from apps.llm_app.skills import Skill, register

    register(
        Skill(
            app_name="figrecipe",
            display_name="Figrecipe - Figure Editor",
            description=(
                "Interactive figure editor for creating and editing "
                "publication-ready matplotlib plots. Supports drag-and-drop "
                "layout, statistical annotations, and multi-panel composition."
            ),
            tool_prefixes=["plt_"],
            capabilities=[
                "Create publication-ready matplotlib figures",
                "Edit figure layout interactively",
                "Add statistical bracket annotations",
                "Compose multi-panel figures",
                "Export to PNG, SVG, PDF",
            ],
            page_patterns=["/figrecipe/"],
            url_prefix="/figrecipe/",
            module_description=(
                "Interactive figure editor: create and edit publication-ready "
                "matplotlib plots with drag-and-drop layout, statistical "
                "annotations, style presets, and multi-format export."
            ),
            mcp_tool_examples=["plt_plot", "plt_compose", "plt_crop", "plt_reproduce"],
        )
    )
except ImportError:
    # Running standalone (figrecipe gui) — no llm_app available
    pass
