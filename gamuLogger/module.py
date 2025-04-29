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
