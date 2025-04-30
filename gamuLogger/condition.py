from abc import ABC, abstractmethod
import re
from typing import Any, Callable

from .regex import RE_AGE_CONDITION, RE_NB_FILES_CONDITION, RE_SIZE_CONDITION
from .utils import string2seconds, string2bytes


class Condition(ABC):
    """
    A class to represent a condition for logging.
    """

    operators : dict[str, Callable[[int, int], bool]] = {
        ">": lambda x, y: x > y,
        ">=": lambda x, y: x >= y,
        "<": lambda x, y: x < y,
        "<=": lambda x, y: x <= y,
        "==": lambda x, y: x == y
    }

    @classmethod
    @abstractmethod
    def from_string(cls, string : str) -> 'Condition':
        """
        Create a Condition from a string.

        :param string: The string to parse.
        :return: An instance of Condition.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @classmethod
    @abstractmethod
    def from_match(cls, match : re.Match[str]) -> 'Condition':
        """
        Create a Condition from a regex match object.

        :param match: The regex match object.
        :return: An instance of Condition.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    @abstractmethod
    def __call__(self, *args : Any, **kwargs : Any) -> bool:
        """
        Call method to evaluate the condition.
        """
        raise NotImplementedError("Subclasses should implement this method.")


class AgeCondition(Condition):
    """
    A condition that checks if the age is greater than a specified value.
    """

    def __init__(self, operator : str, value : int, unit : str):
        """
        Initialize the AgeCondition with an operator, value, and unit.

        Operators allowed : `>`, `>=`, `<`, `<=`, `==`
        Units allowed : `hour`, `minute`, `second`, `day`, `week`, `month`, `year`
        Support plural form of the unit
        (`hours`, `minutes`, `seconds`, `days`, `weeks`, `months`, `years`)
        """

        self.__age_in_seconds = string2seconds(f"{value} {unit}")
        self.__operator = operator

    @classmethod
    def from_string(cls, string : str) -> 'AgeCondition':
        """
        Create an AgeCondition from a string.

        :param string: The string to parse.
        :return: An instance of AgeCondition.
        """
        match = re.match(RE_AGE_CONDITION, string)
        if not match:
            raise ValueError(f"Invalid age condition: {string}")

        return cls.from_match(match)

    @classmethod
    def from_match(cls, match : re.Match[str]) -> 'AgeCondition':
        """
        Create an AgeCondition from a regex match object.

        :param match: The regex match object.
        :return: An instance of AgeCondition.
        """
        operator = match.group('operator')
        value = int(match.group('value'))
        unit = match.group('unit')

        return cls(operator, value, unit)

    def __call__(self, age : int) -> bool:
        """
        Evaluate the condition against a given age.

        :param age: The age to evaluate, in seconds.
        :return: True if the condition is met, False otherwise.
        """

        if self.__operator not in self.operators:
            raise ValueError(f"Invalid operator: {self.__operator}")

        return self.operators[self.__operator](age, self.__age_in_seconds)


class SizeCondition(Condition):
    """
    A condition that checks if the size is greater than a specified value.
    """

    def __init__(self, operator : str, value : int, unit : str):
        """
        Initialize the SizeCondition with an operator, value, and unit.

        Operators allowed : `>`, `>=`, `<`, `<=`, `==`
        Units allowed : `B`, `KB`, `MB`, `GB`, `TB`, `PB`, `EB`, `ZB`, `YB`
        Support plural form of the unit
        (`Bs`, `KBs`, `MBs`, `GBs`, `TBs`, `PBs`, `EBs`, `ZBs`, `YBs`)
        """

        self.__size_in_bytes = string2bytes(f"{value} {unit}")
        self.__operator = operator

    @classmethod
    def from_string(cls, string : str) -> 'SizeCondition':
        """
        Create a SizeCondition from a string.

        :param string: The string to parse.
        :return: An instance of SizeCondition.
        """
        match = re.match(RE_SIZE_CONDITION, string)
        if not match:
            raise ValueError(f"Invalid size condition: {string}")

        return cls.from_match(match)

    @classmethod
    def from_match(cls, match : re.Match[str]) -> 'SizeCondition':
        """
        Create a SizeCondition from a regex match object.

        :param match: The regex match object.
        :return: An instance of SizeCondition.
        """
        operator = match.group('operator')
        value = int(match.group('value'))
        unit = match.group('unit')

        return cls(operator, value, unit)

    def __call__(self, size : int) -> bool:
        """
        Evaluate the condition against a given size.

        :param size: The size to evaluate, in bytes.
        :return: True if the condition is met, False otherwise.
        """
        if self.__operator not in self.operators:
            raise ValueError(f"Invalid operator: {self.__operator}")
        return self.operators[self.__operator](size, self.__size_in_bytes)


class NbFilesCondition(Condition):
    """
    A condition that checks if the number of files is greater than a specified value.
    """

    def __init__(self, operator : str, value : int):
        """
        Initialize the NbFilesCondition with an operator and value.

        Operators allowed : `>`, `>=`, `==`
        """

        if operator not in (">", ">=", "=="):
            raise ValueError(f"Invalid operator: {operator}")

        self.__nb_files = value
        self.__operator = operator

    @classmethod
    def from_string(cls, string : str) -> 'NbFilesCondition':
        """
        Create a NbFilesCondition from a string.

        :param string: The string to parse.
        :return: An instance of NbFilesCondition.
        """
        match = re.match(RE_NB_FILES_CONDITION, string)
        if not match:
            raise ValueError(f"Invalid number of files condition: {string}")

        return cls.from_match(match)

    @classmethod
    def from_match(cls, match : re.Match[str]) -> 'NbFilesCondition':
        """
        Create a NbFilesCondition from a regex match object.

        :param match: The regex match object.
        :return: An instance of NbFilesCondition.
        """
        operator = match.group('operator')
        value = int(match.group('value'))

        return cls(operator, value)

    def __call__(self, nb_files : int) -> bool:
        """
        Evaluate the condition against a given number of files.

        :param nb_files: The number of files to evaluate.
        :return: True if the condition is met, False otherwise.
        """
        if self.__operator not in self.operators:
            raise ValueError(f"Invalid operator: {self.__operator}")

        return self.operators[self.__operator](nb_files, self.__nb_files)


def condition_factory(string : str) -> Condition:
    """
    Create a Condition from a string.

    :param string: The string to parse.
    :return: An instance of Condition.
    """
    if match := re.match(RE_AGE_CONDITION, string):
        return AgeCondition.from_match(match)
    if match := re.match(RE_SIZE_CONDITION, string):
        return SizeCondition.from_match(match)
    if match := re.match(RE_NB_FILES_CONDITION, string):
        return NbFilesCondition.from_match(match)
    raise ValueError(f"Invalid condition: {string}")
