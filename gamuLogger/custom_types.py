#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ###############################################################################################
#                                   PYLINT
# Disable C0301 = Line too long (80 chars by line is not enough)
# pylint: disable=line-too-long
# ###############################################################################################

"""
Utility class for the logger module
"""

import inspect
from enum import Enum
from typing import Protocol



class COLORS(Enum):
    """
    usage:
    ```python
    print(COLORS.RED + "This is red text" + COLORS.RESET)
    print(COLORS.GREEN + "This is green text" + COLORS.RESET)
    print(COLORS.YELLOW + "This is yellow text" + COLORS.RESET)
    ```
    """
    RED = '\033[91m'
    DARK_RED = '\033[91m\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    NONE = ''

    def __str__(self):
        return self.value

    def __add__(self, other : object):
        """
        Allow to concatenate a string with a color, example:
        ```python
        print(COLORS.RED + "This is red text" + COLORS.RESET)
        ```
        or using an f-string:
        ```python
        print(f"{COLORS.RED}This is red text{COLORS.RESET}")
        ```
        """
        return f"{self}{other}"

    def __radd__(self, other : object):
        """
        Allow to concatenate a string with a color, example:
        ```python
        print(COLORS.RED + "This is red text" + COLORS.RESET)
        ```
        or using an f-string:
        ```python
        print(f"{COLORS.RED}This is red text{COLORS.RESET}")
        ```
        """
        return f"{other}{self}"

    def __repr__(self):
        return self.value

class Levels(Enum):
    """
    ## list of Levels:
    - TRACE:   this level is used to print very detailed information, it may contain sensitive information
    - DEBUG:        this level is used to print debug information, it may contain sensitive information
    - INFO:         this level is used to print information about the normal execution of the program
    - WARNING:      this level is used to print warnings about the execution of the program (non-blocking, but may lead to errors)
    - ERROR:        this level is used to print errors that may lead to the termination of the program
    - FATAL:     this level is used to print fatal errors that lead to the termination of the program, typically used in largest except block
    """

    TRACE = 0       # this level is used to print very detailed information, it may contain sensitive information
    DEBUG = 1       # this level is used to print debug information, it may contain sensitive information
    INFO = 2        # this level is used to print information about the normal execution of the program
    WARNING = 3     # this level is used to print warnings about the execution of the program (non-blocking, but may lead to errors)
    ERROR = 4       # this level is used to print errors that may lead to the termination of the program
    FATAL = 5       # this level is used to print fatal errors that lead to the termination of the program, typically used in largest except block
    NONE = 6        # this level is used to disable all logging

    @staticmethod
    def from_string(level : str) -> 'Levels': #pylint: disable=R0911
        """
        Convert a string to a Levels enum.
        The string can be any case (lower, upper, mixed).
        """
        match level.lower():
            case 'trace':
                return Levels.TRACE
            case 'debug':
                return Levels.DEBUG
            case 'info':
                return Levels.INFO
            case 'warning':
                return Levels.WARNING
            case 'error':
                return Levels.ERROR
            case 'fatal':
                return Levels.FATAL
            case 'none':
                return Levels.NONE
            case _:
                return Levels.INFO

    def __str__(self) -> str:
        """
        Return the string representation of the level,
        serialized to 9 characters (centered with spaces)
        """
        match self:
            case Levels.TRACE:
                return '  TRACE  '
            case Levels.DEBUG:
                return '  DEBUG  '
            case Levels.INFO:
                return '  INFO   '
            case Levels.WARNING:
                return ' WARNING '
            case Levels.ERROR:
                return '  ERROR  '
            case Levels.FATAL:
                return '  FATAL  '
            case Levels.NONE:
                raise ValueError("NONE level is not a valid level for string representation")

    def __int__(self):
        return self.value

    def __le__(self, other : 'Levels'):
        return self.value <= other.value

    def color(self) -> COLORS:
        """
        Return the color associated with the level.
        - TRACE: BLUE
        - DEBUG: MAGENTA
        - INFO: GREEN
        - WARNING: YELLOW
        - ERROR: RED
        - FATAL: DARK_RED
        """
        match self:
            case Levels.TRACE:
                return COLORS.CYAN
            case Levels.DEBUG:
                return COLORS.BLUE
            case Levels.INFO:
                return COLORS.GREEN
            case Levels.WARNING:
                return COLORS.YELLOW
            case Levels.ERROR:
                return COLORS.RED
            case Levels.FATAL:
                return COLORS.DARK_RED
            case Levels.NONE:
                raise ValueError("NONE level is not a valid level for color")


class SupportsStr(Protocol): #pylint: disable=R0903
    """
    A protocol that defines a __str__ method.
    """
    def __str__(self) -> str: ...


type Callerinfo = tuple[str, str]

type Message = str|SupportsStr

type Stack = list[inspect.FrameInfo]


class LoggerException(BaseException):
    """
    A class that represents an exception in the logger system.
    """
