
import sys
import threading
from enum import Enum
from typing import Callable, Any

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
