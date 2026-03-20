#!/usr/bin/env python3
# -*- coding: utf-8 -*-
try:
    from scitex_app._django import ScitexAppConfig
except ImportError:
    from django.apps import AppConfig as ScitexAppConfig


class FigRecipeEditorConfig(ScitexAppConfig):
    name = "figrecipe._django"
    label = "figrecipe_editor"
    verbose_name = "FigRecipe Editor"


class ScitexAppChatConfig(ScitexAppConfig):
    """AppConfig that registers scitex_app._chat models under 'scitex_app' label.

    The ChatSession and ChatMessage models declare app_label='scitex_app',
    so this config uses that label for Django model discovery.
    """

    name = "scitex_app._chat"
    label = "scitex_app"
    verbose_name = "SciTeX Chat Sessions"
