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
import sys
import threading
from enum import Enum
from typing import Any, Callable, Protocol


class Module:
    """
    A class that represents a module in the logger system.
    It is used to keep track of the modules that are being logged.
    """
    __instances : dict[tuple[str|None, str|None], 'Module'] = {}
    def __init__(self,
                 name : str,
                 parent : 'Module|None' = None,
                 file : str|None = None,
                 function : str|None = None
                ):
        self.parent = parent
        self.name = name
        self.file = file
        self.function = function

        Module.__instances[(self.file, self.function)] = self

    def get_complete_name(self) -> str:
        """
        Get the complete name of the module, including the parent modules.
        """
        if self.parent is None:
            return self.name
        return f'{self.parent.get_complete_name()}.{self.name}'

    def get_complete_path(self) -> list[str]:
        """
        Get the complete path of the module, including the parent modules.
        """
        if self.parent is None:
            return [self.name]
        return self.parent.get_complete_path() + [self.name]

    @staticmethod
    def get(filename : str, function : str) -> 'Module':
        """
        Get the module instance by its filename and function name.
        If the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
        """
        functions = function.split('.')
        for i in range(len(functions), 0, -1):
            # if the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
            if (filename, '.'.join(functions[:i])) in Module.__instances:
                return Module.__instances[(filename, '.'.join(functions[:i]))]
        if (filename, '<module>') in Module.__instances:
            return Module.__instances[(filename, '<module>')]
        raise ValueError(f"No module found for file {filename} and function {function}")

    @staticmethod
    def exist(filename : str, function : str) -> bool:
        """
        Check if the module instance exists by its filename and function name.
        If the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
        """
        functions = function.split('.')
        for i in range(len(functions), 0, -1):
            # if the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
            if (filename, '.'.join(functions[:i])) in Module.__instances:
                return True
        if (filename, '<module>') in Module.__instances:
            return True
        return False

    @staticmethod
    def exist_exact(filename : str, function : str) -> bool:
        """
        Check if the module instance exists by its filename and function name.
        """
        return (filename, function) in Module.__instances


    @staticmethod
    def delete(filename : str, function : str):
        """
        Delete the module instance by its filename and function name.
        """
        if Module.exist_exact(filename, function):
            # del Module.__instances[(filename, function)]
            Module.__instances.pop((filename, function), None)
        else:
            raise ValueError(f"No module found for file {filename} and function {function}")

    @staticmethod
    def get_by_name(name : str) -> 'Module':
        """
        Get the module instance by its name.
        """
        for module in Module.__instances.values():
            if module.get_complete_name() == name:
                return module
        raise ValueError(f"No module found for name {name}")

    @staticmethod
    def exist_by_name(name : str) -> bool:
        """
        Check if the module instance exists by its name.
        """
        return any(
            module.get_complete_name() == name
            for module in Module.__instances.values()
        )

    @staticmethod
    def delete_by_name(name : str):
        """
        Delete the module instance by its name.
        """
        if not Module.exist_by_name(name):
            raise ValueError(f"No module found for name {name}")
        module = Module.get_by_name(name)
        del Module.__instances[(module.file, module.function)]


    @staticmethod
    def clear():
        """
        Clear all the module instances.
        """
        Module.__instances = {}

    @staticmethod
    def new(name : str, file : str|None = None, function : str|None = None) -> 'Module':
        """
        Create a new module instance by its name, file and function.
        If the module already exists, it will return the existing instance.
        If the module is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
        and create the parent modules if they don't exist.
        """
        if Module.exist_by_name(name):
            existing = Module.get_by_name(name)
            if file == existing.file and function == existing.function:
                return existing
            raise ValueError(f"Module {name} already exists with file {existing.file} and function {existing.function}")

        if '.' in name:
            parent_name, module_name = name.rsplit('.', 1)
            if not Module.exist_by_name(parent_name):
                #create the parent module
                parent = Module.new(parent_name, file, function)
            else:
                #get the parent module
                parent = Module.get_by_name(parent_name)
            return Module(module_name, parent, file, function)
        return Module(name, None, file, function)

    @staticmethod
    def all() -> dict[tuple[str|None, str|None], 'Module']:
        """
        Get all the module instances.
        """
        return Module.__instances


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
    - CRITICAL:     this level is used to print critical errors that lead to the termination of the program, typically used in largest except block
    """

    TRACE = 0       # this level is used to print very detailed information, it may contain sensitive information
    DEBUG = 1       # this level is used to print debug information, it may contain sensitive information
    INFO = 2        # this level is used to print information about the normal execution of the program
    WARNING = 3     # this level is used to print warnings about the execution of the program (non-blocking, but may lead to errors)
    ERROR = 4       # this level is used to print errors that may lead to the termination of the program
    CRITICAL = 5    # this level is used to print critical errors that lead to the termination of the program, typically used in largest except block


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
            case 'critical':
                return Levels.CRITICAL
            case _:
                return Levels.INFO

    def __str__(self) -> str:
        """
        Return the string representation of the level,
        serialized to 10 characters (centered with spaces)
        """
        match self:
            case Levels.TRACE:
                return '  TRACE   '
            case Levels.DEBUG:
                return '  DEBUG   '
            case Levels.INFO:
                return '   INFO   '
            case Levels.WARNING:
                return ' WARNING  '
            case Levels.ERROR:
                return '  ERROR   '
            case Levels.CRITICAL:
                return ' CRITICAL '

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
        - CRITICAL: DARK_RED
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
            case Levels.CRITICAL:
                return COLORS.DARK_RED

class TerminalTarget(Enum):
    """
    Enum for the terminal targets.
    - STDOUT: standard output (sys.stdout)
    - STDERR: standard error (sys.stderr)
    """
    STDOUT = 30
    STDERR = 31

    def __str__(self) -> str:
        match self:
            case TerminalTarget.STDOUT:
                return 'stdout'
            case TerminalTarget.STDERR:
                return 'stderr'

    @staticmethod
    def from_string(target : str) -> 'TerminalTarget':
        """
        Convert a string to a TerminalTarget enum.
        The string can be any case (lower, upper, mixed).
        """
        match target.lower():
            case 'stdout':
                return TerminalTarget.STDOUT
            case 'stderr':
                return TerminalTarget.STDERR
            case _:
                raise ValueError(f"Invalid terminal target: {target}")

class Target:
    """
    A class that represents a target for the logger.
    """
    __instances : dict[str, 'Target'] = {}

    class Type(Enum):
        """
        Enum for the target types.
        - FILE: file target (a function that takes a string as input and writes it to a file)
        - TERMINAL: terminal target (sys.stdout or sys.stderr)
        """
        FILE = 20
        TERMINAL = 21

        def __str__(self) -> str:
            match self:
                case Target.Type.FILE:
                    return 'file'
                case Target.Type.TERMINAL:
                    return 'terminal'

    def __new__(cls, target : Callable[[str], None] | TerminalTarget, name : str|None = None):
        if name is None:
            if isinstance(target, TerminalTarget):
                name = name if name is not None else str(target)
            elif hasattr(target, '__name__'):
                name = target.__name__
            else:
                raise ValueError("The target must be a function or a TerminalTarget; use Target.from_file(file) to create a file target")
        if target in cls.__instances:
            return cls.__instances[name]
        instance = super().__new__(cls)
        cls.__instances[name] = instance
        return instance

    def __init__(self, target : Callable[[str], None] | TerminalTarget, name : str|None = None):

        if isinstance(target, TerminalTarget):
            match target:
                case TerminalTarget.STDOUT:
                    self.target = sys.stdout.write
                case TerminalTarget.STDERR:
                    self.target = sys.stderr.write
            self.__type = Target.Type.TERMINAL
            self.__name = name if name is not None else str(target)
        elif hasattr(target, '__call__'):
            self.__type = Target.Type.FILE
            self.__name = name if name is not None else target.__name__
            self.target = target
        else:
            raise ValueError("The target must be a function or a TerminalTarget; use Target.from_file(file) to create a file target")


        self.properties : dict[str, Any] = {}
        self.__lock = threading.Lock()

    @staticmethod
    def from_file(file : str) -> 'Target':
        """
        Create a Target from a file.
        The file will be created if it does not exist.
        """
        def write_to_file(string : str):
            with open(file, 'a', encoding="utf-8") as f:
                f.write(string)
        with open(file, 'w', encoding="utf-8") as f: # clear the file
            f.write('')
        return Target(write_to_file, file)

    def __call__(self, string : str):
        with self.__lock: # prevent multiple threads to write at the same time
            self.target(string)

    def __str__(self) -> str:
        return self.__name

    def __repr__(self) -> str:
        return f"Target({self.__name})"

    def __getitem__(self, key: str) -> Any:
        return self.properties[key]

    def __setitem__(self, key: str, value: Any):
        self.properties[key] = value

    def __delitem__(self, key: str):
        del self.properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.properties

    @property
    def type(self) -> 'Target.Type':
        """
        Get the type of the target.
        """
        return self.__type

    @property
    def name(self) -> str:
        """
        Get the name of the target.
        """
        return self.__name

    @name.setter
    def name(self, name : str):
        old_name = self.__name
        self.__name = name
        del Target.__instances[old_name]
        Target.__instances[name] = self

    def delete(self):
        """
        Delete the target from the logger system.
        This will remove the target from the list of targets and free the memory.
        """
        Target.unregister(self)


    @staticmethod
    def get(name : str | TerminalTarget) -> 'Target':
        """
        Get the target instance by its name.
        """
        name = str(name)
        if Target.exist(name):
            return Target.__instances[name]
        else:
            raise ValueError(f"Target {name} does not exist")

    @staticmethod
    def exist(name : str | TerminalTarget) -> bool:
        """
        Check if the target instance exists by its name.
        """
        name = str(name)
        return name in Target.__instances

    @staticmethod
    def list() -> list['Target']:
        """
        Get the list of all targets.
        """
        return list(Target.__instances.values())

    @staticmethod
    def clear():
        """
        Clear all the target instances.
        """
        Target.__instances = {}

    @staticmethod
    def register(target : 'Target'):
        """
        Register a target instance in the logger system.
        """
        Target.__instances[target.name] = target

    @staticmethod
    def unregister(target : 'Target|str'):
        """
        Unregister a target instance from the logger system.
        Target can be a Target instance or a string (name of the target).
        """
        name = target if isinstance(target, str) else target.name
        if Target.exist(name):
            Target.__instances.pop(name, None)
        else:
            raise ValueError(f"Target {name} does not exist")

class LoggerConfig:
    """
    A class that represents the configuration of the logger.
    """
    def __init__(self):
        self.show_threads_name = False
        self.show_process_name = False


    def clear(self):
        """
        Clear the logger config.
        """
        self.show_threads_name = False
        self.show_process_name = False


    def __getitem__(self, key: str) -> Any:
        match key:
            case 'show_threads_name':
                return self.show_threads_name
            case 'show_process_name':
                return self.show_process_name
            case _:
                raise KeyError(f"Parameter {key} not found")

    def __setitem__(self, key: str, value: Any):
        match key:
            case 'show_threads_name':
                self.show_threads_name = value
            case 'show_process_name':
                self.show_process_name = value
            case _:
                raise KeyError(f"Parameter {key} not found")

    def __str__(self):
        return f"LoggerConfig(show_threads_name={self.show_threads_name}, show_process_name={self.show_process_name})"


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
