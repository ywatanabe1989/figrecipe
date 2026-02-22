#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Minimal Django settings for standalone figrecipe editor.

Used when running the editor without a parent Django project.
"""

import os
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "figrecipe-standalone-dev-key-not-for-production",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "0.0.0.0"]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "figrecipe._django",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "figrecipe._django.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
            ],
        },
    },
]

# No database needed for standalone editor
DATABASES = {}

STATIC_URL = "/static/"
STATICFILES_DIRS = [str(BASE_DIR / "static")]

# Temp directory for session files
FIGRECIPE_TEMP_DIR = Path(tempfile.gettempdir()) / "figrecipe_editor"
