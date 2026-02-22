#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.apps import AppConfig


class FigRecipeEditorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "figrecipe._django"
    label = "figrecipe_editor"
    verbose_name = "FigRecipe Editor"
