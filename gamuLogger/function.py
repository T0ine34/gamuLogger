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

from typing import Callable, Any, TypeVar
from datetime import datetime

from .gamu_logger import Logger
from .utils import get_caller_info, COLORS
from .custom_types import Message

T = TypeVar('T')

trace : Callable[[Message], None] = Logger.trace
debug : Callable[[Message], None] = Logger.debug
info : Callable[[Message], None] = Logger.info
warning : Callable[[Message], None] = Logger.warning
error : Callable[[Message], None] = Logger.error
fatal : Callable[[Message], None] = Logger.fatal
message : Callable[[Message, COLORS], None] = Logger.message


def trace_func(use_chrono : bool = False) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to print trace messages before and after the function call
    usage:
    ```python
    @trace_func(use_chrono=False)
    def my_function(arg1, arg2, kwarg1=None):
        return arg1+arg2

    my_function("value1", "value2", kwarg1="value3")
    ```
    will print:
    ```
    [datetime] [   TRACE   ] Calling my_function with\n\t\t\t   | args: (value1, value2)\n\t\t\t   | kwargs: {'kwarg1': 'value3'}
    [datetime] [   TRACE   ] Function my_function returned "value1value2"
    ```

    note: this decorator does nothing if the Logger level is not set to trace
    """
    def pre_wrapper(func : Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args : Any, **kwargs : Any) -> T:
            Logger.trace(f"Calling {func.__name__} with\nargs: {args}\nkwargs: {kwargs}", get_caller_info())
            start = None
            if use_chrono:
                start = datetime.now()
            result = func(*args, **kwargs)
            if use_chrono and start is not None:
                end = datetime.now()
                time_delta = str(end - start).split(".", maxsplit=1)[0]
                Logger.trace(f"Function {func.__name__} took {time_delta} to execute and returned \"{result}\"", get_caller_info())
            else:
                Logger.trace(f"Function {func.__name__} returned \"{result}\"", get_caller_info())
            return result
        return wrapper
    return pre_wrapper


def debug_func(use_chrono : bool = False) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to print trace messages before and after the function call
    usage:
    ```python
    @trace_func
    def my_function(arg1, arg2, kwarg1=None):
        return arg1+arg2

    my_function("value1", "value2", kwarg1="value3")
    ```
    will print:
    ```log
    [datetime] [   DEBUG   ] Calling my_function with\n\t\t\t   | args: (value1, value2)\n\t\t\t   | kwargs: {'kwarg1': 'value3'}
    [datetime] [   DEBUG   ] Function my_function returned "value1value2"
    ```

    note: this decorator does nothing if the Logger level is not set to debug or trace
    """

    def pre_wrapper(func : Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args : Any, **kwargs : Any) -> T:
            Logger.debug(f"Calling {func.__name__} with\nargs: {args}\nkwargs: {kwargs}", get_caller_info())
            start = None
            if use_chrono:
                start = datetime.now()
            result = func(*args, **kwargs)
            if use_chrono and start is not None:
                end = datetime.now()
                time_delta = str(end - start).split(".", maxsplit=1)[0]
                Logger.debug(f"Function {func.__name__} took {time_delta} to execute and returned \"{result}\"", get_caller_info())
            else:
                Logger.debug(f"Function {func.__name__} returned \"{result}\"", get_caller_info())
            return result
        return wrapper
    return pre_wrapper


def chrono(func : Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to print the execution time of a function
    usage:
    ```python
    @chrono
    def my_function(arg1, arg2, kwarg1=None):
        return arg1+arg2

    my_function("value1", "value2", kwarg1="value3")
    ```
    will print:
    ```log
    [datetime] [   DEBUG   ] Function my_function took 0.0001s to execute
    ```
    """

    def wrapper(*args : Any, **kwargs : Any) -> T:
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        debug(f"Function {func.__name__} took {end-start} to execute")
        return result
    return wrapper
