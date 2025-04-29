#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ###############################################################################################
#                                   PYLINT
# Disable C0301 = Line too long (80 chars by line is not enough)
# pylint: disable=line-too-long
# ###############################################################################################

"""
Targets for the logger.
"""

import os
import sys
import threading
from enum import Enum
from typing import Callable, Any
import re
import time

from.utils import string2seconds, string2bytes

RE_AGE_CONDITION = re.compile(r"age\s*(?P<operator>>|>=|<|<=)\s*(?P<value>\d+)\s*(?P<unit>(?:hour|minute|second|day|week|month|year)s?)")
RE_SIZE_CONDITION = re.compile(r"size\s*(?P<operator>>|>=|<|<=)\s*(?P<value>\d+)\s*(?P<unit>(?:KB|MB|GB|TB)s?)")
RE_NB_FILES_CONDITION = re.compile(r"nb_files\s*(?P<operator>>|>=|<|<=)\s*(?P<value>\d+)")

class WriteToFile: #pylint: disable=R0903
    """
    A class that writes to a file based on a schema.
    See the docstring of Target.from_file_schema for more details.
    """
    def __init__(self, folder : str, schema : str, switch_condition : tuple[str], delete_condition : tuple[str]):
        self.folder = folder

        # create the folder if it does not exist
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        self.schema = schema
        self.current_file = ""
        self.__create_new_file()

        for condition in switch_condition:
            if not any([RE_AGE_CONDITION.match(condition), RE_SIZE_CONDITION.match(condition)]):
                raise ValueError(f"Invalid switch condition: {condition}")
        self.switch_condition = switch_condition

        for condition in delete_condition:
            if not any([RE_AGE_CONDITION.match(condition), RE_NB_FILES_CONDITION.match(condition)]):
                raise ValueError(f"Invalid delete condition: {condition}")
        self.delete_condition = delete_condition

    def __create_new_file(self):
        """
        Create a new file based on the schema and the current time.
        """
        # get the current time
        current_time = time.localtime()
        # create the file name based on the schema
        file_name = self.schema.replace("${date}", f"{current_time.tm_year}-{current_time.tm_mon:02d}-{current_time.tm_mday:02d}")
        file_name = file_name.replace("${hour}", f"{current_time.tm_hour:02d}")
        file_name = file_name.replace("${minute}", f"{current_time.tm_min:02d}")
        file_name = file_name.replace("${second}", f"{current_time.tm_sec:02d}")
        file_name = file_name.replace("${pid}", str(os.getpid()))

        # create the full path for the file
        self.current_file = os.path.join(self.folder, file_name)

    def __is_outdated_age(self, operator : str, value : int, unit : str) -> bool:
        # get the file creation time
        file_time = os.path.getctime(self.current_file)
        # get the current time
        current_time = time.time()
        # get the difference in seconds
        diff = current_time - file_time
        # convert the value to seconds
        value = string2seconds(f"{value} {unit}")

        # compare the difference with the value
        match operator:
            case '>':
                if diff > value:
                    return True
            case '>=':
                if diff >= value:
                    return True
            case '<':
                if diff < value:
                    return True
            case '<=':
                if diff <= value:
                    return True
            case _:
                raise ValueError(f"Invalid operator: {operator}")
        return False

    def __is_outdated_size(self, operator : str, value : int, unit : str) -> bool:
        # get the file size
        file_size = os.path.getsize(self.current_file)
        # convert the value to bytes
        value = string2bytes(f"{value} {unit}")

        # compare the size with the value
        match operator:
            case '>':
                if file_size > value:
                    return True
            case '>=':
                if file_size >= value:
                    return True
            case '<':
                if file_size < value:
                    return True
            case '<=':
                if file_size <= value:
                    return True
            case _:
                raise ValueError(f"Invalid operator: {operator}")
        return False

    def __is_outdated(self) -> bool:
        """
        Check if the file is outdated based on the switch condition.
        """
        for condition in self.switch_condition:
            if match := RE_AGE_CONDITION.match(condition):
                operator = match.group('operator')
                value = int(match.group('value'))
                unit = match.group('unit')
                if self.__is_outdated_age(operator, value, unit):
                    return True
            elif match := RE_SIZE_CONDITION.match(condition):
                operator = match.group('operator')
                value = int(match.group('value'))
                unit = match.group('unit')
                if self.__is_outdated_size(operator, value, unit):
                    return True
            else:
                raise ValueError(f"Invalid switch condition: {condition}")
        return False

    def __call__(self, string : str):
        """
        Write the string to the file.
        If the file is outdated, create a new file.
        """
        # check if the file is outdated
        if self.__is_outdated():
            self.__create_new_file()

        # write the string to the file
        with open(self.current_file, 'a', encoding="utf-8") as f:
            f.write(string)


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
            elif callable(target):
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
        elif callable(target):
            self.__type = Target.Type.FILE
            self.__name = name if name is not None else target.__name__
            self.target = target
        else:
            raise ValueError("The target must be a function or a TerminalTarget; use Target.from_file(file) to create a file target")


        self.properties : dict[str, Any] = {}
        self.__lock = threading.Lock()

    @classmethod
    def from_file(cls, file : str) -> 'Target':
        """
        Create a Target from a file.
        The file will be created if it does not exist.
        """
        def write_to_file(string : str):
            with open(file, 'a', encoding="utf-8") as f:
                f.write(string)
        with open(file, 'w', encoding="utf-8") as f: # clear the file
            f.write('')
        return cls(write_to_file, file)

    @classmethod
    def from_file_schema(cls,
            folder : str, schema : str = "${date} ${hour}:${minute}.log",
            switch_condition : tuple[str] = ("age > 1 hour",),
            delete_condition : tuple[str] = ("nb_files >= 5",)
        )-> 'Target':
        """create a Target to write logs in files where the name is based on the schema
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

        The switch condition can be:
        - `age > x unit`: the file will be created if it is older than x unit (e.g. `age > 1 hour`)
        - `size > x unit`: the file will be created if it is larger than x unit (e.g. `size > 1 MB`)
        If multiple condition are provided, the file will be created if any of them is true. (OR condition)
        Operators allowed : `>`, `>=`, `<`, `<=`
        Units allowed : `hour`, `minute`, `second`, `day`, `week`, `month`, `year`, `KB`, `MB`, `GB`, `TB`
        Support plural form of the unit (e.g. `hours`, `minutes`, `seconds`, `days`, `weeks`, `months`, `years`, `KBs`, `MBs`, `GBs`, `TBs`)

        The delete condition can be:
        - `age > x unit`: the file will be deleted if it is older than x unit (e.g. `age > 1 hour`)
        - `nb_files > x`: the file will be deleted if there are more than x files in the folder (e.g. `nb_files > 5`)
        If multiple condition are provided, the file will be deleted if any of them is true. (OR condition)

        Args:
            folder (str): folder where the files will be created
            schema (str): schema for the file name. The default is "${date} ${hour}:${minute}.log".
            switch_condition (str): condition to switch the file. The default is "age > 1 hour".
            delete_condition (str): condition to delete the file. The default is "nb_files >= 5".
            The file will be created in the folder specified in the folder argument.

        Returns:
            Target: a Target instance that writes to the file specified by the schema
        """

        write_to_file = WriteToFile(folder, schema, switch_condition, delete_condition)

        return cls(write_to_file, folder)

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
        if not Target.exist(name):
            raise ValueError(f"Target {name} does not exist")
        return Target.__instances[name]

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
