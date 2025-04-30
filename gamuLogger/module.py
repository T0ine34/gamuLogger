#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ###############################################################################################
#                                   PYLINT
# Disable C0301 = Line too long (80 chars by line is not enough)
# pylint: disable=line-too-long
# ###############################################################################################

"""
Module class for the logger system.
"""

from .custom_types import Levels


class Module:
    """
    A class that represents a module in the logger system.
    It is used to keep track of the modules that are being logged.
    """
    __instances : dict[tuple[str|None, str|None], 'Module'] = {}
    __levels : dict[str, Levels] = {}
    __default_level : Levels = Levels.INFO
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

    @classmethod
    def get(cls, filename : str, function : str) -> 'Module':
        """
        Get the module instance by its filename and function name.
        If the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
        """
        functions = function.split('.')
        for i in range(len(functions), 0, -1):
            # if the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
            if (filename, '.'.join(functions[:i])) in cls.__instances:
                return cls.__instances[(filename, '.'.join(functions[:i]))]
        if (filename, '<module>') in cls.__instances:
            return cls.__instances[(filename, '<module>')]
        raise ValueError(f"No module found for file {filename} and function {function}")

    @classmethod
    def exist(cls, filename : str, function : str) -> bool:
        """
        Check if the module instance exists by its filename and function name.
        If the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
        """
        functions = function.split('.')
        for i in range(len(functions), 0, -1):
            # if the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
            if (filename, '.'.join(functions[:i])) in cls.__instances:
                return True
        if (filename, '<module>') in cls.__instances:
            return True
        return False

    @classmethod
    def exist_exact(cls, filename : str, function : str) -> bool:
        """
        Check if the module instance exists by its filename and function name.
        """
        return (filename, function) in cls.__instances


    @classmethod
    def delete(cls, filename : str, function : str):
        """
        Delete the module instance by its filename and function name.
        """
        if cls.exist_exact(filename, function):
            # del Module.__instances[(filename, function)]
            cls.__instances.pop((filename, function), None)
        else:
            raise ValueError(f"No module found for file {filename} and function {function}")

    @classmethod
    def get_by_name(cls, name : str) -> 'Module':
        """
        Get the module instance by its name.
        """
        for module in cls.__instances.values():
            if module.get_complete_name() == name:
                return module
        raise ValueError(f"No module found for name {name}")

    @classmethod
    def exist_by_name(cls, name : str) -> bool:
        """
        Check if the module instance exists by its name.
        """
        return any(
            module.get_complete_name() == name
            for module in cls.__instances.values()
        )

    @classmethod
    def delete_by_name(cls, name : str):
        """
        Delete the module instance by its name.
        """
        if not cls.exist_by_name(name):
            raise ValueError(f"No module found for name {name}")
        module = cls.get_by_name(name)
        del cls.__instances[(module.file, module.function)]


    @classmethod
    def clear(cls):
        """
        Clear all the module instances.
        """
        cls.__instances = {}

    @classmethod
    def new(cls, name : str, file : str|None = None, function : str|None = None) -> 'Module':
        """
        Create a new module instance by its name, file and function.
        If the module already exists, it will return the existing instance.
        If the module is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
        and create the parent modules if they don't exist.
        """
        if cls.exist_by_name(name):
            existing = cls.get_by_name(name)
            if file == existing.file and function == existing.function:
                return existing
            raise ValueError(f"Module {name} already exists with file {existing.file} and function {existing.function}")

        if '.' in name:
            parent_name, module_name = name.rsplit('.', 1)
            if not cls.exist_by_name(parent_name):
                #create the parent module
                parent = cls.new(parent_name, file, function)
            else:
                #get the parent module
                parent = cls.get_by_name(parent_name)
            return cls(module_name, parent, file, function)
        return cls(name, None, file, function)

    @classmethod
    def all(cls) -> dict[tuple[str|None, str|None], 'Module']:
        """
        Get all the module instances.
        """
        return cls.__instances


    @classmethod
    def set_level(cls, name : str, level : Levels):
        """
        Set the level of the module instance by its name.
        """
        cls.__levels[name] = level

    @classmethod
    def get_level(cls, name : str) -> Levels:
        """
        Get the level of the module instance by its name.
        """
        return cls.__levels[name] if name in cls.__levels else cls.__default_level

    @classmethod
    def set_default_level(cls, level : Levels):
        """
        Set the default level of the module instance.
        """
        cls.__default_level = level

    @classmethod
    def get_default_level(cls) -> Levels:
        """
        Get the default level of the module instance.
        """
        return cls.__default_level
