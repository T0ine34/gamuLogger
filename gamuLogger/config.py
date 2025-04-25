# -*- coding: utf-8 -*-

"""
GamuLogger - A simple and powerful logging library for Python
Antoine Buirey 2025
"""

from typing import Any


class Config:
    """
    Configuration class for the GamuLogger.
    """

    def __init__(self, **default : dict[str, Any]) -> None:
        self.__default = default
        self.__conf = self.__default.copy()

    def __repr__(self) -> str:
        """
        Get the string representation of the configuration.
        """
        return f"Config({self.__conf})"

    def __str__(self) -> str:
        """
        Get the string representation of the configuration.
        """
        return f"Config({self.__conf})"

    def __contains__(self, name : str) -> bool:
        """
        Check if a configuration attribute exists.
        """
        return name in self.__conf

    def __getitem__(self, name : str) -> Any:
        """
        Get the value of a configuration attribute.
        """
        if name in self.__conf:
            return self.__conf[name]
        raise KeyError(f"Configuration attribute '{name}' not found.")

    def __setitem__(self, name : str, value : Any) -> None:
        """
        Set the value of a configuration attribute.
        """
        if name in self.__conf:
            self.__conf[name] = value
        else:
            raise KeyError(f"Configuration attribute '{name}' not found.")

    def clear(self) -> None:
        """
        Clear the configuration.
        """
        self.__conf = self.__default.copy()
