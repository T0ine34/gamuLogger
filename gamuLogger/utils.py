"""
Utility functions for the logger module
"""


import inspect
import os
import sys
from datetime import datetime
from json import JSONEncoder
from typing import Any

from .custom_types import COLORS, Callerinfo, Stack


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
    else:
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


def split_long_string(string: str, length: int = 100) -> str:
    """Split a long string into multiple lines, on spaces."""
    result: list[str] = []
    if len(string) <= length:
        return string

    lines = string.split('\n')  # Split by existing newlines first
    for line in lines:
        words = line.split(' ')  # Split each line into words
        current_line = []
        for word in words:
            if len(word) > length:
                raise ValueError("A word is longer than the maximum length")
            if len(' '.join(current_line)) + len(word) + (1 if current_line else 0) > length:
                result.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            result.append(' '.join(current_line))
    return '\n'.join(result)

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


def get_executable_formatted():
    """
    Returns the formatted string of the current executable and its arguments.
    If the executable is a Python interpreter, it includes the script name.
    Otherwise, it only includes the executable name.
    """
    executable_name = os.path.basename(sys.executable)
    if "python" in executable_name.lower():
        return f"{executable_name} {' '.join(sys.argv)}"
    return f"{executable_name}"
