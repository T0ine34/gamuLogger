import sys
import threading
from enum import Enum
from typing import Any, Callable


class Module:
    __instances = {}  # type: dict[tuple[str|None, str|None], Module]
    def __init__(self, name : str, parent : 'Module|None' = None, file : str|None = None, function : str|None = None):
        self.parent = parent
        self.name = name
        self.file = file
        self.function = function

        Module.__instances[(self.file, self.function)] = self

    def getCompleteName(self) -> str:
        if self.parent is None:
            return self.name
        return f'{self.parent.getCompleteName()}.{self.name}'

    def getCompletePath(self) -> list[str]:
        if self.parent is None:
            return [self.name]
        return self.parent.getCompletePath() + [self.name]

    @staticmethod
    def get(filename : str, function : str) -> 'Module':
        # if Module.exist(filename, function):
        #     return Module.__instances[(filename, function)]
        # else:
        #     raise ValueError(f"No module found for file {filename} and function {function}")
        functions = function.split('.')
        for i in range(len(functions), 0, -1): # if the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
            if (filename, '.'.join(functions[:i])) in Module.__instances:
                return Module.__instances[(filename, '.'.join(functions[:i]))]
        if (filename, '<module>') in Module.__instances:
            return Module.__instances[(filename, '<module>')]
        raise ValueError(f"No module found for file {filename} and function {function}")

    @staticmethod
    def exist(filename : str, function : str) -> bool:
        # return (filename, function) in Module.__instances
        functions = function.split('.')
        for i in range(len(functions), 0, -1): # if the function is a.b.c.d, we check if a.b.c.d, a.b.c, a.b, a are in the instances
            if (filename, '.'.join(functions[:i])) in Module.__instances:
                return True
        if (filename, '<module>') in Module.__instances:
            return True
        return False


    @staticmethod
    def delete(filename : str, function : str):
        if Module.exist(filename, function):
            del Module.__instances[(filename, function)]
        else:
            raise ValueError(f"No module found for file {filename} and function {function}")

    @staticmethod
    def getByName(name : str) -> 'Module':
        for module in Module.__instances.values():
            if module.getCompleteName() == name:
                return module
        raise ValueError(f"No module found for name {name}")

    @staticmethod
    def existByName(name : str) -> bool:
        return any(
            module.getCompleteName() == name
            for module in Module.__instances.values()
        )

    @staticmethod
    def deleteByName(name : str):
        if not Module.existByName(name):
            raise ValueError(f"No module found for name {name}")
        module = Module.getByName(name)
        del Module.__instances[(module.file, module.function)]


    @staticmethod
    def clear():
        Module.__instances = {}

    @staticmethod
    def new(name : str, file : str|None = None, function : str|None = None) -> 'Module':
        if Module.existByName(name):
            existing = Module.getByName(name)
            if file == existing.file and function == existing.function:
                return existing
            else:
                raise ValueError(f"Module {name} already exists with file {existing.file} and function {existing.function}")

        if '.' in name:
            parentName, moduleName = name.rsplit('.', 1)
            if not Module.existByName(parentName):
                raise ValueError(f"No module found for name {parentName}")
            #get the parent module
            parent = Module.getByName(parentName)
            return Module(moduleName, parent, file, function)
        return Module(name, None, file, function)

    @staticmethod
    def all() -> dict[tuple[str|None, str|None], 'Module']:
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
    MAGENTA = '\033[96m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    NONE = ''

    def __str__(self):
        return self.value

    def __add__(self, other):
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

    def __radd__(self, other):
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

class LEVELS(Enum):
    """
    ## list of levels:
    - DEEP_DEBUG:   this level is used to print very detailed information, it may contain sensitive information
    - DEBUG:        this level is used to print debug information, it may contain sensitive information
    - INFO:         this level is used to print information about the normal execution of the program
    - WARNING:      this level is used to print warnings about the execution of the program (non-blocking, but may lead to errors)
    - ERROR:        this level is used to print errors that may lead to the termination of the program
    - CRITICAL:     this level is used to print critical errors that lead to the termination of the program, typically used in largest except block
    """

    DEEP_DEBUG = 0  # this level is used to print very detailed information, it may contain sensitive information
    DEBUG = 1       # this level is used to print debug information, it may contain sensitive information
    INFO = 2        # this level is used to print information about the normal execution of the program
    WARNING = 3     # this level is used to print warnings about the execution of the program (non-blocking, but may lead to errors)
    ERROR = 4       # this level is used to print errors that may lead to the termination of the program
    CRITICAL = 5    # this level is used to print critical errors that lead to the termination of the program, typically used in largest except block


    @staticmethod
    def from_string(level : str) -> 'LEVELS':
        match level.lower():
            case 'deep_debug':
                return LEVELS.DEEP_DEBUG
            case 'debug':
                return LEVELS.DEBUG
            case 'info':
                return LEVELS.INFO
            case 'warning':
                return LEVELS.WARNING
            case 'error':
                return LEVELS.ERROR
            case 'critical':
                return LEVELS.CRITICAL
            case _:
                return LEVELS.INFO

    def __str__(self) -> str:
        """
        Return the string representation of the level, serialized to 10 characters (centered with spaces)
        """
        match self:
            case LEVELS.DEEP_DEBUG:
                return '  DEBUG   '
            case LEVELS.DEBUG:
                return '  DEBUG   '
            case LEVELS.INFO:
                return '   INFO   '
            case LEVELS.WARNING:
                return ' WARNING  '
            case LEVELS.ERROR:
                return '  ERROR   '
            case LEVELS.CRITICAL:
                return ' CRITICAL '

    def __int__(self):
        return self.value

    def __le__(self, other : 'LEVELS'):
        return self.value <= other.value

    def color(self) -> COLORS:
        match self:
            case LEVELS.DEEP_DEBUG:
                return COLORS.BLUE
            case LEVELS.DEBUG:
                return COLORS.BLUE
            case LEVELS.INFO:
                return COLORS.GREEN
            case LEVELS.WARNING:
                return COLORS.YELLOW
            case LEVELS.ERROR:
                return COLORS.RED
            case LEVELS.CRITICAL:
                return COLORS.DARK_RED

class SENSITIVE_LEVELS(Enum):
    HIDE = 10
    SHOW = 11

    @staticmethod
    def from_string(level : str) -> 'SENSITIVE_LEVELS':
        match level.lower():
            case 'hide':
                return SENSITIVE_LEVELS.HIDE
            case 'show':
                return SENSITIVE_LEVELS.SHOW
            case _:
                return SENSITIVE_LEVELS.HIDE

    @staticmethod
    def from_bool(value : bool) -> 'SENSITIVE_LEVELS':
        return SENSITIVE_LEVELS.SHOW if value else SENSITIVE_LEVELS.HIDE

class TERMINAL_TARGETS(Enum):
    STDOUT = 30
    STDERR = 31

    def __str__(self) -> str:
        match self:
            case TERMINAL_TARGETS.STDOUT:
                return 'stdout'
            case TERMINAL_TARGETS.STDERR:
                return 'stderr'

    @staticmethod
    def from_string(target : str) -> 'TERMINAL_TARGETS':
        match target.lower():
            case 'stdout':
                return TERMINAL_TARGETS.STDOUT
            case 'stderr':
                return TERMINAL_TARGETS.STDERR
            case _:
                raise ValueError(f"Invalid terminal target: {target}")

class Target:
    __instances = {} #type: dict[str, Target]

    class Type(Enum):
        FILE = 20
        TERMINAL = 21

        def __str__(self) -> str:
            match self:
                case Target.Type.FILE:
                    return 'file'
                case Target.Type.TERMINAL:
                    return 'terminal'

    def __new__(cls, target : Callable[[str], None] | TERMINAL_TARGETS, name : str|None = None):
        if name is None:
            if isinstance(target, TERMINAL_TARGETS):
                name = name if name is not None else str(target)
            elif hasattr(target, '__name__'):
                name = target.__name__
            else:
                raise ValueError("The target must be a function or a TERMINAL_TARGETS; use Target.fromFile(file) to create a file target")
        if target in cls.__instances:
            return cls.__instances[name]
        instance = super().__new__(cls)
        cls.__instances[name] = instance
        return instance

    def __init__(self, target : Callable[[str], None] | TERMINAL_TARGETS, name : str|None = None):

        if isinstance(target, str):
            raise ValueError("The target must be a function or a TERMINAL_TARGETS; use Target.fromFile(file) to create a file target")

        if isinstance(target, TERMINAL_TARGETS):
            match target:
                case TERMINAL_TARGETS.STDOUT:
                    self.target = sys.stdout.write
                case TERMINAL_TARGETS.STDERR:
                    self.target = sys.stderr.write
            self.__type = Target.Type.TERMINAL
            self.__name = name if name is not None else str(target)
        else:
            self.__type = Target.Type.FILE
            self.__name = name if name is not None else target.__name__
            self.target = target


        self.properties = {} #type: dict[str, Any]
        self.__lock = threading.Lock()

    @staticmethod
    def fromFile(file : str) -> 'Target':
        def writeToFile(string : str):
            with open(file, 'a', encoding="utf-8") as f:
                f.write(string)
        with open(file, 'w', encoding="utf-8") as f: # clear the file
            f.write('')
        return Target(writeToFile, file)

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
        return self.__type

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name : str):
        old_name = self.__name
        self.__name = name
        del Target.__instances[old_name]
        Target.__instances[name] = self

    def delete(self):
        Target.unregister(self)


    @staticmethod
    def get(name : str | TERMINAL_TARGETS) -> 'Target':
        name = str(name)
        if Target.exist(name):
            return Target.__instances[name]
        else:
            raise ValueError(f"Target {name} does not exist")

    @staticmethod
    def exist(name : str | TERMINAL_TARGETS) -> bool:
        name = str(name)
        return name in Target.__instances.keys()

    @staticmethod
    def list() -> list['Target']:
        return list(Target.__instances.values())

    @staticmethod
    def clear():
        Target.__instances = {}

    @staticmethod
    def register(target : 'Target'):
        Target.__instances[target.name] = target

    @staticmethod
    def unregister(target):
        name = target if isinstance(target, str) else target.name
        if Target.exist(name):
            del Target.__instances[name]
        else:
            raise ValueError(f"Target {name} does not exist")


class LoggerConfig:
    def __init__(self, sensitiveDatas: list[str] = None):
        if sensitiveDatas is None:
            sensitiveDatas = []
        self.sensitiveDatas = sensitiveDatas
        self.showThreadsName = False
        self.showProcessName = False


    def clear(self):
        self.sensitiveDatas = []
        self.showThreadsName = False
        self.showProcessName = False


    def __getitem__(self, key: str) -> Any:
        match key:
            case 'sensitiveDatas':
                return self.sensitiveDatas
            case 'showThreadsName':
                return self.showThreadsName
            case 'showProcessName':
                return self.showProcessName
            case _:
                raise KeyError(f"Parameter {key} not found")

    def __setitem__(self, key: str, value: Any):
        match key:
            case 'sensitiveDatas':
                self.sensitiveDatas = value
            case 'showThreadsName':
                self.showThreadsName = value
            case 'showProcessName':
                self.showProcessName = value
            case _:
                raise KeyError(f"Parameter {key} not found")

    def __str__(self):
        return f"LoggerConfig(sensitiveDatas={self.sensitiveDatas}, showThreadsName={self.showThreadsName}, showProcessName={self.showProcessName})"
