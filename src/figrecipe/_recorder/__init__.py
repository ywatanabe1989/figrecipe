#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recording infrastructure for figrecipe."""

from ._core import AxesRecord, CallRecord, FigureRecord, Recorder
from ._utils import process_args

__all__ = [
    "Recorder",
    "CallRecord",
    "AxesRecord",
    "FigureRecord",
    "process_args",
]

# EOF
