#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ###############################################################################################
#                                   PYLINT
# pylint: disable=line-too-long
# ###############################################################################################

"""
GamuLogger - A simple and powerful logging library for Python

Antoine Buirey 2025
"""

import inspect
import os
import re
import sys
from datetime import datetime
from json import JSONEncoder
from typing import Any

from .custom_types import COLORS, Callerinfo, Stack
from .regex import (RE_DATE, RE_DATETIME, RE_DAY, RE_HOUR, RE_MINUTE, RE_MONTH,
                    RE_PID, RE_SECOND, RE_TIME, RE_YEAR)


def get_caller_file_path(stack : Stack|None = None) -> str:
    """
    Returns the absolute filepath of the caller of the parent function
    """
    if stack is None:
        stack = inspect.stack()
    if len(stack) < 3:
        return os.path.abspath(stack[-1].filename)
    return os.path.abspath(stack[2].filename)


def get_caller_function_name(stack  : Stack|None = None) -> str:
    """
    Returns the name of the function that called this one,
    including the class name if the function is a method
    """
    if stack is None:
        stack = inspect.stack()
    if len(stack) < 3:
        return "<module>"
    caller = stack[2]
    caller_name = caller.function
    if caller_name == "<module>":
        return "<module>"

    parents = get_all_parents(caller.filename, caller.lineno)[::-1]
    if len(parents) <= 0:
        return caller_name
    if caller_name == parents[-1]:
        return '.'.join(parents)
    return '.'.join(parents) + '.' + caller_name


def get_caller_info(context : int = 1) -> Callerinfo:
    """
    Returns the file path and function name of the caller of the parent function
    """
    stack = inspect.stack(context)
    return get_caller_file_path(stack), get_caller_function_name(stack)


def get_time():
    """
    Returns the current time in the format YYYY-MM-DD HH:MM:SS
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def replace_newline(string : str, indent : int = 33):
    """
    Replace newlines in a string with a newline and an indent
    """
    return string.replace('\n', '\n' + (' ' * indent) + '| ')


class CustomEncoder(JSONEncoder):
    """
    Custom JSON encoder that handles enums and other objects
    """
    def default(self, o : Any) -> str:
        # if we serialize an enum, just return the name
        if hasattr(o, '_name_'):
            return o._name_ #pylint: disable=W0212

        if hasattr(o, '__dict__'):
            return o.__dict__
        if hasattr(o, '__str__'):
            return str(o)
        return super().default(o)


def get_all_parents(filepath : str, lineno : int) -> list[str]:
    """
    Get all parent classes of a class or method, based on indentation in the file
    """

    # Read
    with open(filepath, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    # Get the line
    line = lines[lineno-1]

    # Get the indentation
    indentation = len(line) - len(line.lstrip())

    # Get the parent classes
    parents : list[str] = []
    for i in range(lineno-1, 0, -1):
        line = lines[i]
        if len(line) - len(line.lstrip()) < indentation:
            indentation = len(line) - len(line.lstrip())
            if "class" in line:
                parents.append(line.strip()[:-1].split(' ')[1]) # Remove the ':'
            elif "def" in line:
                parents.append(line.strip()[:-1].split(' ')[1].split('(')[0])

    return parents


def colorize(color : COLORS, string : str):
    """
    Colorize a string with the given color
    """
    return f"{color}{string}{COLORS.RESET}"


def string2seconds(string : str) -> int:
    """Take a string like '1 hour', '2 minutes', '3 seconds', '21 days',
    '2 weeks', '1 month', or '3 years' and convert it to seconds.
    Accept multiple units in the same string, like '1 hour 2 minutes 3 seconds'.

    Args:
        string (str): The string to convert.

    Returns:
        int: The number of seconds represented by the string.
    """

    time_units = {
        'second': 1,
        'minute': 60,
        'hour': 3600,
        'day': 86400,
        'week': 604800,
        'month': 2592000,  # Approximate, as months vary in length (30 days)
        'year': 31536000,   # Approximate, as years vary in length (365.25 days)
    }

    parts = string.split()
    total_seconds = 0

    if not len(parts) % 2 == 0:
        raise ValueError("Invalid input format. Expected 'value unit' pairs.")
    for i in range(0, len(parts), 2):
        value, unit = parts[i], parts[i + 1].lower()
        if not value.isdigit():
            raise ValueError(f"Invalid value: {value}")
        if unit.endswith('s'):
            unit = unit[:-1]
        if unit not in time_units:
            raise ValueError(f"Unknown time unit: {unit}")

        total_seconds += int(value) * time_units[unit]

    return total_seconds

def string2bytes(string : str) -> int:
    """Take a string like '1 KB', '2 MB', '3 GB', '21 TB' and convert it to bytes.
    Accept multiple units in the same string, like '1 KB 2 MB 3 GB'.

    Args:
        string (str): The string to convert.

    Returns:
        int: The number of bytes represented by the string.
    """

    size_units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
        "PB": 1024**5,
        "BYTE": 1,
        "KILOBYTE": 1024,
        "MEGABYTE": 1024**2,
        "GIGABYTE": 1024**3,
        "TERABYTE": 1024**4,
        "PETABYTE": 1024**5,
    }

    parts = string.upper().split()
    total_bytes = 0
    for i in range(0, len(parts), 2):
        if not parts[i].isdigit():
            raise ValueError(f"Invalid value: {parts[i]}")
        if i + 1 >= len(parts):
            raise ValueError("Missing unit after value")
        value = int(parts[i])
        unit = parts[i + 1].upper()
        if unit.endswith('S'):
            unit = unit[:-1]  # Remove the trailing 's' for plural units
        if unit in size_units:
            total_bytes += value * size_units[unit]
        else:
            raise ValueError(f"Unknown size unit: {unit}")
    return total_bytes

def schema2regex(schema : str) -> re.Pattern[str]:
    """
    Convert a schema string to a regex pattern.

    The schema can contain the following placeholders:
        - `${date}`: the current date in YYYY-MM-DD format
        - `${time}`: the current time in HH-MM-SS format
        - `${datetime}`: the current date and time in YYYY-MM-DD_HH-MM-SS format

        - `${year}`: the current year in YYYY format
        - `${month}`: the current month in MM format
        - `${day}`: the current day in DD format

        - `${hour}`: the current hour in HH format
        - `${minute}`: the current minute in MM format
        - `${second}`: the current second in SS format

        - `${pid}`: the current process id
    """
    # Define the regex patterns for each placeholder
    patterns = {
        "${date}": RE_DATE,
        "${time}": RE_TIME,
        "${datetime}": RE_DATETIME,
        "${year}": RE_YEAR,
        "${month}": RE_MONTH,
        "${day}": RE_DAY,
        "${hour}": RE_HOUR,
        "${minute}": RE_MINUTE,
        "${second}": RE_SECOND,
        "${pid}": RE_PID,
    }

    # Replace the placeholders with their regex patterns
    for placeholder, pattern in patterns.items():
        schema = schema.replace(placeholder, pattern)

    return re.compile(schema)
