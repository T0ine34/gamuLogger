#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pyright: reportUnusedImport=false

"""
GamuLogger - A simple and powerful logging library for Python

Antoine Buirey 2025
"""

from .gamu_logger import (Levels, Logger, Module, Target, TerminalTarget,
                          chrono, critical, debug, debug_func, error, info,
                          message, trace, trace_func, warning)
