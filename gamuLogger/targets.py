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
import time
from enum import Enum
from typing import Any, Callable

from .condition import (AgeCondition, NbFilesCondition, SizeCondition,
                        condition_factory)

from.utils import schema2regex



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
        self.schema_regex = schema2regex(self.schema)
        self.current_file = ""
        self.__create_new_file()

        self.switch_condition = [condition_factory(condition) for condition in switch_condition]

        self.delete_condition = [condition_factory(condition) for condition in delete_condition]

    def __create_new_file(self):
        """
        Create a new file based on the schema and the current time.
        """
        # get the current time
        current_time = time.localtime()
        # create the file name based on the schema
        file_name = self.schema.replace("${date}", f"{current_time.tm_year}-{current_time.tm_mon:02d}-{current_time.tm_mday:02d}")
        file_name = file_name.replace("${time}", f"{current_time.tm_hour:02d}-{current_time.tm_min:02d}-{current_time.tm_sec:02d}")
        file_name = file_name.replace("${datetime}", f"{current_time.tm_year}-{current_time.tm_mon:02d}-{current_time.tm_mday:02d}_{current_time.tm_hour:02d}-{current_time.tm_min:02d}-{current_time.tm_sec:02d}")

        file_name = file_name.replace("${year}", str(current_time.tm_year))
        file_name = file_name.replace("${month}", f"{current_time.tm_mon:02d}")
        file_name = file_name.replace("${day}", f"{current_time.tm_mday:02d}")

        file_name = file_name.replace("${hour}", f"{current_time.tm_hour:02d}")
        file_name = file_name.replace("${minute}", f"{current_time.tm_min:02d}")
        file_name = file_name.replace("${second}", f"{current_time.tm_sec:02d}")
        file_name = file_name.replace("${pid}", str(os.getpid()))

        # create the full path for the file
        self.current_file = os.path.join(self.folder, file_name)

    def __get_log_files_by_age(self) -> list[str]:
        """
        Return the list of files in the folder that match the schema and are older than the current file.
        """
        # get the list of files in the folder
        files = os.listdir(self.folder)
        # filter the files that match the schema
        files = [file for file in files if self.schema_regex.match(file)]
        # sort the files by age (oldest first)
        files.sort(key=lambda x: os.path.getctime(os.path.join(self.folder, x)))
        return files

    def __is_outdated(self) -> bool:
        """
        Check if the file is outdated based on the switch condition.
        """
        if not os.path.exists(self.current_file):
            return True

        for condition in self.switch_condition:
            if isinstance(condition, AgeCondition):
                if condition(os.path.getctime(self.current_file)):
                    return True
            elif isinstance(condition, SizeCondition):
                if condition(os.path.getsize(self.current_file)):
                    return True
            elif isinstance(condition, NbFilesCondition):
                raise ValueError("NbFilesCondition is not supported for switching")
            else:
                raise ValueError(f"Unknown condition type: {type(condition)}")
        return False

    def __delete_excess_files(self) -> None:
        """
        Delete the files that exceed the limit.
        """
        oldest_files = self.__get_log_files_by_age()
        to_delete : set[str] = set()
        for condition in self.delete_condition:
            if isinstance(condition, NbFilesCondition):
                while condition(len(oldest_files)):
                    # delete the oldest file
                    to_delete.add(oldest_files.pop(0))
            elif isinstance(condition, AgeCondition):
                for file in oldest_files:
                    edit_date = os.path.getctime(os.path.join(self.folder, file))
                    age = time.time() - edit_date
                    if condition(age):
                        to_delete.add(file)
            elif isinstance(condition, SizeCondition):
                raise ValueError("SizeCondition is not supported for deletion")

        # delete the files
        for file in to_delete:
            os.remove(os.path.join(self.folder, file))

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

        # delete the excedent files
        self.__delete_excess_files()


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
    __lock = threading.Lock()

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
        with cls.__lock: # prevent multiple threads to create the same target
            if name in cls.__instances:
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
            folder : str, schema : str = "${date}_${hour}-${minute}.log",
            switch_condition : tuple[str] = ("age > 1 hour",),
            delete_condition : tuple[str] = ("nb_files >= 5",)
        )-> 'Target':
        """create a Target to write logs in files where the name is based on a schema

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
        Operators allowed : `>`, `>=`, `<`, `<=`, `==`
        Units allowed : `hour`, `minute`, `second`, `day`, `week`, `month`, `year`, `KB`, `MB`, `GB`, `TB`
        Support plural form of the unit (e.g. `hours`, `minutes`, `seconds`, `days`, `weeks`, `months`, `years`, `KBs`, `MBs`, `GBs`, `TBs`)

        The delete condition can be:
        - `age > x unit`: the file will be deleted if it is older than x unit (e.g. `age > 1 hour`)
        - `nb_files > x`: the file will be deleted if there are more than x files in the folder (e.g. `nb_files > 5`)
        If multiple condition are provided, the file will be deleted if any of them is true. (OR condition)
        Operators allowed : `>`, `>=`, `==`
        To fullfill the `nb_files` condition, older files will be deleted first.

        Args:
            folder (str): folder where the files will be created
            schema (str): schema for the file name. The default is "${date}_${hour}-${minute}.log".
            switch_condition (str): condition to switch the file. The default is "age > 1 hour".
            delete_condition (str): condition to delete the file. The default is "nb_files > 5".

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
