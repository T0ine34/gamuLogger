#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pyright: reportUnusedImport=false

"""
GamuLogger - A simple and powerful logging library for Python

Antoine Buirey 2025
"""

from .gamu_logger import Logger
from .custom_types import COLORS, Levels
from .targets import Target, TerminalTarget
from .argparse_config import config_argparse, config_logger
from .function import (
    trace,
    debug,
    info,
    warning,
    error,
    fatal,
    message,
    debug_func,
    trace_func,
    chrono
)
