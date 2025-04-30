#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pyright: reportUnusedImport=false

"""
GamuLogger - A simple and powerful logging library for Python

Antoine Buirey 2025
"""

from .argparse_config import config_argparse, config_logger
from .gamu_logger import (Levels, Logger, Module, Target, TerminalTarget,
                          chrono, debug, debug_func, error, fatal, info,
                          message, trace, trace_func, warning)
