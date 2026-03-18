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
