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


import os
import threading
from json import dumps
from typing import Callable

from .config import Config
from .custom_types import COLORS, Callerinfo, Levels, Message
from .module import Module
from .targets import Target, TerminalTarget
from .utils import (CustomEncoder, colorize, get_caller_info,
                    get_executable_formatted, get_time, replace_newline,
                    split_long_string)


class Logger:
    """
    Logger class to manage the logging system of an application
    """

    __instance : 'Logger|None' = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Logger, cls).__new__(cls)

        return cls.__instance

    def __init__(self):
        self.config = Config(
            show_process_name = False,
            show_threads_name = False,
            show_pid = False
        )

        #configuring default target
        default_target = Target(TerminalTarget.STDOUT)
        default_target["level"] = Levels.INFO

#---------------------------------------- Internal methods ----------------------------------------


    def __print(self, level : Levels, msg : Message, caller_info : Callerinfo): #pylint: disable=W0238
        for target in Target.list():
            self.__print_in_target(level, msg, caller_info, target)

    def __print_in_target(self, msg_level : Levels, msg : Message, caller_info : Callerinfo, target : Target):
        if Module.exist(*caller_info):
            name = Module.get(*caller_info).get_complete_name()
            module_level = Module.get_level(name)
        else:
            module_level = Module.get_default_level()

        # Check if the message level is below the effective level
        if msg_level < module_level or msg_level < target["level"]:
            return

        result = f"{COLORS.RESET}" if target.type == Target.Type.TERMINAL else ""

        # add the current time
        result += self.__log_element_time(target)

        # add the process name if needed
        result += self.__log_element_process_name(target)

        # add the process ID if needed
        result += self.__log_element_pid(target)

        # add the thread name if needed
        result += self.__log_element_thread_name(target)

        # add the level of the message
        result += self.__log_element_level(msg_level, target)

        # add the module name if needed
        result += self.__log_element_module(caller_info, target)

        # add the message
        result += self.__log_element_message(msg, caller_info)

        target(result+"\n")

    def __log_element_time(self, target : Target) -> str:
        if target.type == Target.Type.TERMINAL:
            return f"[{COLORS.BLUE}{get_time()}{COLORS.RESET}]"
        # if the target is a file, we don't need to color the output
        return f"[{get_time()}]"

    def __log_element_process_name(self, target : Target) -> str:
        if self.config['show_process_name']:
            if target.type == Target.Type.TERMINAL:
                return f" [{COLORS.CYAN}{get_executable_formatted().center(20)}{COLORS.RESET}]"
            return f" [{get_executable_formatted().center(20)}]"
        return ""

    def __log_element_pid(self, target : Target) -> str:
        if self.config['show_pid']:
            pid = f"{os.getpid():^8d}"
            if target.type == Target.Type.TERMINAL:
                return f" [ {COLORS.MAGENTA}{pid}{COLORS.RESET} ]"
            return f" [ {pid} ]"
        return ""

    def __log_element_thread_name(self, target : Target) -> str:
        if self.config['show_threads_name']:
            name = threading.current_thread().name.center(30)
            if target.type == Target.Type.TERMINAL:
                return f" [ {COLORS.CYAN}{name}{COLORS.RESET} ]"
            return f" [ {name} ]"
        return ""

    def __log_element_level(self, level : Levels, target : Target) -> str:
        if target.type == Target.Type.TERMINAL:
            return f" [{level.color()}{level}{COLORS.RESET}]"
        return f" [{level}]"

    def __log_element_module(self, caller_info : Callerinfo, target : Target) -> str:
        result = ""
        if Module.exist(*caller_info):
            for module in Module.get(*caller_info).get_complete_path():
                if target.type == Target.Type.TERMINAL:
                    result += f" [ {colorize(COLORS.BLUE, module.center(15))} ]"
                else:
                    result += f" [ {module.center(15)} ]"
        return result

    def __log_element_message(self, msg : Message, caller_info : Callerinfo) -> str:
        if not isinstance(msg, str):
            msg = dumps(msg, indent=4, cls=CustomEncoder)
        indent = 32
        if Module.exist(*caller_info):
            # add 20 for each module name
            indent += 20 * len(Module.get(*caller_info).get_complete_path())
        if self.config['show_process_name']:
            indent += 20
        if self.config['show_pid']:
            indent += 8
        if self.config['show_threads_name']:
            indent += 30
        return f" {replace_newline(msg, indent)}"

    def __print_message_in_target(self, msg : Message, color : COLORS, target : Target):
        if target.type == Target.Type.TERMINAL:
            target(f"{color}{msg}{COLORS.RESET}\n")
        else:
            target(str(msg) + "\n")

    def __print_message(self, msg : Message, color : COLORS): #pylint: disable=W0238
        for target in Target.list():
            self.__print_message_in_target(msg, color, target)


#---------------------------------------- Logging methods -----------------------------------------

    @classmethod
    def trace(cls, msg : Message, caller_info : Callerinfo|None = None):
        """
        Print a trace message to the standard output, in blue color

        Args:
            msg (Message): The message to print
            caller_info (Callerinfo|None): The caller info. If None, the caller info will be retrieved from the stack.
        """
        if caller_info is None: #pragma: no cover
            caller_info = get_caller_info()
        cls.get_instance().__print(Levels.TRACE, msg, caller_info) #pylint: disable=W0212

    @classmethod
    def debug(cls, msg : Message, caller_info : Callerinfo|None = None):
        """
        Print a debug message to the standard output, in magenta color

        Args:
            msg (Message): The message to print
            caller_info (Callerinfo|None): The caller info. If None, the caller info will be retrieved from the stack.
        """
        if caller_info is None: #pragma: no cover
            caller_info = get_caller_info()
        cls.get_instance().__print(Levels.DEBUG, msg, caller_info) #pylint: disable=W0212

    @classmethod
    def info(cls, msg : Message, caller_info : Callerinfo|None = None):
        """
        Print an info message to the standard output, in green color

        Args:
            msg (Message): The message to print
            caller_info (Callerinfo|None): The caller info. If None, the caller info will be retrieved from the stack.
        """
        if caller_info is None: #pragma: no cover
            caller_info = get_caller_info()
        cls.get_instance().__print(Levels.INFO, msg, caller_info) #pylint: disable=W0212

    @classmethod
    def warning(cls, msg : Message, caller_info : Callerinfo|None = None):
        """
        Print a warning message to the standard output, in yellow color

        Args:
            msg (Message): The message to print
            caller_info (Callerinfo|None): The caller info. If None, the caller info will be retrieved from the stack.
        """
        if caller_info is None: #pragma: no cover
            caller_info = get_caller_info()
        cls.get_instance().__print(Levels.WARNING, msg, caller_info) #pylint: disable=W0212

    @classmethod
    def error(cls, msg : Message, caller_info : Callerinfo|None = None):
        """
        Print an error message to the standard output, in red color

        Args:
            msg (Message): The message to print
            caller_info (Callerinfo|None): The caller info. If None, the caller info will be retrieved from the stack.
        """
        if caller_info is None: #pragma: no cover
            caller_info = get_caller_info()
        cls.get_instance().__print(Levels.ERROR, msg, caller_info) #pylint: disable=W0212

    @classmethod
    def fatal(cls, msg : Message, caller_info : Callerinfo|None = None):
        """
        Print a fatal message to the standard output, in red color

        Args:
            msg (Message): The message to print
            caller_info (Callerinfo|None): The caller info. If None, the caller info will be retrieved from the stack.
        """
        if caller_info is None: #pragma: no cover
            caller_info = get_caller_info()
        cls.get_instance().__print(Levels.FATAL, msg, caller_info) #pylint: disable=W0212

    @classmethod
    def message(cls, msg : Message, color : COLORS = COLORS.NONE):
        """
        Print a message to the standard output, in yellow color
        It is used to pass information to the user about the global execution of the program

        Args:
            msg (Message): The message to print
            color (COLORS): The color of the message. It can be one of the COLORS enum values.
        """
        cls.get_instance().__print_message(msg, color) #pylint: disable=W0212

#---------------------------------------- Configuration methods -----------------------------------

    @classmethod
    def get_instance(cls) -> 'Logger':
        """
        Get the instance of the logger. If the instance does not exist, it will create it.
        Returns:
            Logger: The instance of the logger.
        """
        if cls.__instance is None:
            Logger()
        return cls.__instance # type: ignore

    @classmethod
    def set_level(cls, target_name: str, level : Levels):
        """
        Set the level of a target. This will change the level of the target and filter the messages that will be printed.
        Args:
            target_name (str): The name of the target. It can be a callable, a string or a Target object.
            level (Levels): The level of the target. It can be one of the Levels enum values.
        """
        cls.get_instance()
        target = Target.get(target_name)
        target["level"] = level

    @classmethod
    def set_module_level(cls, name : str, level : Levels):
        """
        Set the level of a module. This will change the level of the module and filter the messages that will be printed.
        Args:
            name (str): The name of the module. It can be a callable, a string or a Module object.
            level (Levels): The level of the module. It can be one of the Levels enum values.
        """
        cls.get_instance()
        Module.set_level(name, level)

    @classmethod
    def set_default_module_level(cls, level : Levels):
        """
        Set the default level of a module. This will change the level of the module and filter the messages that will be printed.
        Args:
            level (Levels): The level of the module. It can be one of the Levels enum values.
        """
        cls.get_instance()
        Module.set_default_level(level)

    @classmethod
    def set_module(cls, name : str|None):
        """
        Set the module name for the logger. This will be used to identify the module that generated the log message.
        All logging methods will use the module name of the most recent set module, in the order of scope.
        It mean that a module can be set for a whole file, a class, a function or a method.

        Args:
            name (str): The name of the module. If None, the module will be deleted.
        """
        cls.get_instance()
        caller_info = get_caller_info()
        if not name:
            Module.delete(*caller_info)
        elif any(len(token) > 15 for token in name.split(".")):
            raise ValueError("Each module name should be less than 15 characters")
        else:
            Module.new(name, *caller_info)

    @classmethod
    def show_threads_name(cls, value : bool = True):
        """
        Show the thread name in the log messages. This is useful to identify the thread that generated the log message.
        Args:
            value (bool): If True, the thread name will be shown. If False, it will not be shown.
        """
        cls.get_instance().config['show_threads_name'] = value

    @classmethod
    def show_process_name(cls, value : bool = True):
        """
        Show the process name in the log messages. This is useful to identify the process that generated the log message.
        Args:
            value (bool): If True, the process name will be shown. If False, it will not be shown.
        """
        cls.get_instance().config['show_process_name'] = value

    @classmethod
    def show_pid(cls, value : bool = True):
        """
        Show the process ID in the log messages. This is useful to identify the process that generated the log message.
        Args:
            value (bool): If True, the process ID will be shown. If False, it will not be shown.
        """
        cls.get_instance().config['show_pid'] = value

    @classmethod
    def add_target(cls, target_func : Callable[[str], None] | str | Target | TerminalTarget, level : Levels = Levels.INFO) -> str:
        """
        Add a target to the logger. This will register the target and add it to the list of targets.
        Args:
            target_func (Callable[[str], None] | str | Target | TerminalTarget): The target to add. It can be a callable, a string or a Target object.
            level (Levels): The level of the target. It can be one of the Levels enum values.
        Returns:
            str: The name of the target.
        """
        cls.get_instance()
        target : Target|None = None
        if isinstance(target_func, str):
            target = Target.from_file(target_func)
        elif isinstance(target_func, Target):
            target = target_func
        else:
            target = Target(target_func)
        cls.set_level(target.name, level)
        return target.name

    @staticmethod
    def remove_target(target_name : str):
        """
        Remove a target from the logger. This will unregister the target and remove it from the list of targets.
        Args:
            target_name (str): The name of the target to remove
        """
        Target.unregister(target_name)

    @classmethod
    def reset(cls):
        """
        Reset the logger to its default state. This will remove all targets and clear the configuration.
        """
        Target.clear()
        cls.get_instance().config.clear()

        #configuring default target
        default_target = Target(TerminalTarget.STDOUT)
        default_target["level"] = Levels.INFO
