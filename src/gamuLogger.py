import threading
from datetime import datetime
from json import dumps
from typing import Any, Callable

from .customTypes import (COLORS, LEVELS, SENSITIVE_LEVELS, TERMINAL_TARGETS,
                            LoggerConfig, Module, Target)
from .utils import (CustomJSONEncoder, centerString, colorize, getCallerInfo,
                    getExecutableFormatted, getTime, replaceNewLine,
                    splitLongString, strictTypeCheck)


class UnexpectedError(Exception): ...

class Logger:

    __instance = None # type: Logger|None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Logger, cls).__new__(cls)
            cls.__instance.init()

        return cls.__instance

    def init(self):
        self.config = LoggerConfig()

        #configuring default target
        defaultTargget = Target(TERMINAL_TARGETS.STDOUT)
        defaultTargget["level"] = LEVELS.INFO
        defaultTargget["sensitiveMode"] = SENSITIVE_LEVELS.HIDE

#---------------------------------------- Internal methods ----------------------------------------

    @strictTypeCheck
    def __print(self, level : LEVELS, msg : Any, callerInfo : tuple[str, str]):
        for target in Target.list():
            self.__printInTarget(level, msg, callerInfo, target)

    @strictTypeCheck
    def __printInTarget(self, level : LEVELS, msg : Any, callerInfo : tuple[str, str], target : Target):
        if not target["level"] <= level:
            return
        result = ""

        # add the current time
        result += self.__LogElementTime(target)

        # add the process name if needed
        result += self.__LogElementProcessName(target)

        # add the thread name if needed
        result += self.__LogElementThreadName(target)

        # add the level of the message
        result += self.__LogElementLevel(level, target)

        # add the module name if needed
        result += self.__LogElementModule(callerInfo, target)

        # add the message
        result += self.__LogElementMessage(msg, callerInfo)

        result = self.__parseSensitive(result, target)
        target(result+"\n")

    def __LogElementTime(self, target):
        if target.type == Target.Type.TERMINAL:
            return f"[{COLORS.BLUE}{getTime()}{COLORS.RESET}]"
        else:
            # if the target is a file, we don't need to color the output
            return f"[{getTime()}]"

    def __LogElementProcessName(self, target):
        if self.config.showProcessName:
            if target.type == Target.Type.TERMINAL:
                return f" [{COLORS.CYAN}{centerString(getExecutableFormatted(), 20)}{COLORS.RESET}]"
            else:
                return f" [{centerString(getExecutableFormatted(), 20)}]"
        return ""

    def __LogElementThreadName(self, target):
        if self.config.showThreadsName:
            name = centerString(threading.current_thread().name, 30)
            if target.type == Target.Type.TERMINAL:
                return f" [ {COLORS.CYAN}{name}{COLORS.RESET} ]"
            else:
                return f" [ {name} ]"
        return ""

    def __LogElementLevel(self, level, target):
        if target.type == Target.Type.TERMINAL:
            return f" [{level.color()}{level}{COLORS.RESET}]"
        else:
            return f" [{level}]"

    def __LogElementModule(self, callerInfo, target):
        result = ""
        if Module.exist(*callerInfo):
            for module in Module.get(*callerInfo).getCompletePath():
                if target.type == Target.Type.TERMINAL:
                    result += f" [ {colorize(COLORS.BLUE, centerString(module, 15))} ]"
                else:
                    result += f" [ {centerString(module, 15)} ]"
        return result

    def __LogElementMessage(self, msg, callerInfo):
        if isinstance(msg, (int, float, bool)):
            msg = str(msg)
        elif isinstance(msg, str):
            msg = splitLongString(msg, 150)
        else:
            msg = dumps(msg, indent=4, cls=CustomJSONEncoder)

        return f" {replaceNewLine(msg, 33 + (20 if Module.exist(*callerInfo) else 0))}"

    @strictTypeCheck
    def __printMessageInTarget(self, msg : str, color : COLORS, target : Target):
        msg = self.__parseSensitive(msg, target)
        if target.type == Target.Type.TERMINAL:
            target(f"{color}{msg}{COLORS.RESET}")
        else:
            target(msg+"\n")

    @strictTypeCheck
    def __printMessage(self, msg : str, color : COLORS):
        for target in Target.list():
            self.__printMessageInTarget(msg, color, target)

    @strictTypeCheck
    def __parseSensitive(self, msg : str, target : Target) -> str:
        match target["sensitiveMode"]:
            case SENSITIVE_LEVELS.HIDE:
                for sensitive in self.config.sensitiveDatas:
                    msg = msg.replace(sensitive, "*" * len(sensitive))
                return msg
            case SENSITIVE_LEVELS.SHOW:
                return msg
            case _:
                raise ValueError(f"Unknown sensitive mode: {target['sensitiveMode']}")

#---------------------------------------- Logging methods -----------------------------------------

    @staticmethod
    def deepDebug(msg : Any, callerInfo = None):
        if callerInfo is None:
            callerInfo = getCallerInfo()
        Logger.getInstance().__print(LEVELS.DEEP_DEBUG, msg, callerInfo)

    @staticmethod
    def debug(msg : Any, callerInfo = None):
        if callerInfo is None:
            callerInfo = getCallerInfo()
        Logger.getInstance().__print(LEVELS.DEBUG, msg, callerInfo)

    @staticmethod
    def info(msg : Any, callerInfo = None):
        if callerInfo is None:
            callerInfo = getCallerInfo()
        Logger.getInstance().__print(LEVELS.INFO, msg, callerInfo)

    @staticmethod
    def warning(msg : Any, callerInfo = None):
        if callerInfo is None:
            callerInfo = getCallerInfo()
        Logger.getInstance().__print(LEVELS.WARNING, msg, callerInfo)

    @staticmethod
    def error(msg : Any, callerInfo = None):
        if callerInfo is None:
            callerInfo = getCallerInfo()
        Logger.getInstance().__print(LEVELS.ERROR, msg, callerInfo)

    @staticmethod
    def critical(msg : Any, callerInfo = None):
        if callerInfo is None:
            callerInfo = getCallerInfo()
        Logger.getInstance().__print(LEVELS.CRITICAL, msg, callerInfo)

    @staticmethod
    @strictTypeCheck
    def message(msg : Any, color : COLORS = COLORS.NONE):
        Logger.getInstance().__printMessage(msg, color)

#---------------------------------------- Configuration methods -----------------------------------

    @staticmethod
    def getInstance() -> 'Logger':
        return Logger.__instance #type: ignore

    @staticmethod
    @strictTypeCheck
    def setLevel(targetName: str, level : LEVELS):
        target = Target.get(targetName)
        target["level"] = level

    @staticmethod
    @strictTypeCheck
    def setSensitiveMode(targetName: str, mode : SENSITIVE_LEVELS):
        target = Target.get(targetName)
        target["sensitiveMode"] = mode

        if mode == SENSITIVE_LEVELS.SHOW:
            Logger.getInstance().__printMessageInTarget("Sensitive mode was disable, this file may contain sensitive information, please do not share it with anyone", COLORS.YELLOW, target)

    @staticmethod
    def setModule(name : str):
        callerInfo = getCallerInfo()
        if not name:
            Module.delete(*callerInfo)
        elif any(len(token) > 15 for token in name.split(".")):
            raise ValueError("Module name should be less than 15 characters")
        else:
            Module.new(name, *callerInfo)


    @staticmethod
    @strictTypeCheck
    def showThreadsName(value : bool = True):
        Logger.getInstance().config.showThreadsName = value

    @staticmethod
    @strictTypeCheck
    def showProcessName(value : bool = True):
        Logger.getInstance().config.showProcessName = value


    @staticmethod
    @strictTypeCheck
    def addTarget(targetFunc : Callable[[str], None] | str | Target | TERMINAL_TARGETS, level : LEVELS = LEVELS.INFO, sensitiveMode : SENSITIVE_LEVELS = SENSITIVE_LEVELS.HIDE) -> str:
        target = None #type: Target|None
        if isinstance(targetFunc, str):
            target = Target.fromFile(targetFunc)
        elif isinstance(targetFunc, Target):
            target = targetFunc
        else:
            target = Target(targetFunc)
        Logger.setLevel(target.name, level)
        Logger.setSensitiveMode(target.name, sensitiveMode)
        return target.name

    @staticmethod
    @strictTypeCheck
    def removeTarget(targetName : str):
        Target.unregister(targetName)

    @staticmethod
    @strictTypeCheck
    def addSensitiveData(data : Any):
        Logger.getInstance().config.sensitiveDatas.append(data)


    @staticmethod
    @strictTypeCheck
    def reset():
        Target.clear()
        Logger.getInstance().config.clear()

        if not Logger.__instance:
            raise UnexpectedError("Logger instance does not exist")

        #configuring default target
        defaultTargget = Target(TERMINAL_TARGETS.STDOUT)
        defaultTargget["level"] = LEVELS.INFO
        defaultTargget["sensitiveMode"] = SENSITIVE_LEVELS.HIDE

def deepDebug(msg : Any):
    Logger.deepDebug(msg, getCallerInfo())

def debug(msg : Any):
    Logger.debug(msg, getCallerInfo())

def info(msg : Any):
    Logger.info(msg, getCallerInfo())

def warning(msg : Any):
    Logger.warning(msg, getCallerInfo())

def error(msg : Any):
    Logger.error(msg, getCallerInfo())

def critical(msg : Any):
    Logger.critical(msg, getCallerInfo())

@strictTypeCheck
def message(msg : Any, color : COLORS = COLORS.NONE):
    """
    Print a message to the standard output, in yellow color\n
    This method should be used before any other method\n
    It is used to pass information to the user about the global execution of the program
    """
    Logger.message(msg, color)

@strictTypeCheck
def deepDebugFunc(useChrono : bool = False):
    """
    Decorator to print deep debug messages before and after the function call
    usage:
    ```python
    @deep_debug_func(useChrono=False)
    def my_function(arg1, arg2, kwarg1=None):
        return arg1+arg2

    my_function("value1", "value2", kwarg1="value3")
    ```
    will print:
    ```log
    [datetime] [   DEBUG   ] Calling my_function with\n\t\t\t   | args: (value1, value2)\n\t\t\t   | kwargs: {'kwarg1': 'value3'}
    [datetime] [   DEBUG   ] Function my_function returned "value1value2"
    ```

    note: this decorator does nothing if the Logger level is not set to deep debug
    """
    @strictTypeCheck
    def pre_wrapper(func : Callable):
        @strictTypeCheck
        def wrapper(*args, **kwargs):
            Logger.deepDebug(f"Calling {func.__name__} with\nargs: {args}\nkwargs: {kwargs}", getCallerInfo())
            if useChrono:
                start = datetime.now()
            result = func(*args, **kwargs)
            if useChrono:
                end = datetime.now()
                tDelta = str(end-start).split(".")[0]
                Logger.deepDebug(f"Function {func.__name__} took {tDelta} to execute and returned \"{result}\"", getCallerInfo())
            else:
                Logger.deepDebug(f"Function {func.__name__} returned \"{result}\"", getCallerInfo())
            return result
        return wrapper
    return pre_wrapper

@strictTypeCheck
def debugFunc(useChrono : bool = False):
    """
    Decorator to print deep debug messages before and after the function call
    usage:
    ```python
    @deep_debug_func
    def my_function(arg1, arg2, kwarg1=None):
        return arg1+arg2

    my_function("value1", "value2", kwarg1="value3")
    ```
    will print:
    ```log
    [datetime] [   DEBUG   ] Calling my_function with\n\t\t\t   | args: (value1, value2)\n\t\t\t   | kwargs: {'kwarg1': 'value3'}
    [datetime] [   DEBUG   ] Function my_function returned "value1value2"
    ```

    note: this decorator does nothing if the Logger level is not set to debug or deep debug
    """
    @strictTypeCheck
    def pre_wrapper(func : Callable):
        @strictTypeCheck
        def wrapper(*args, **kwargs):
            Logger.debug(f"Calling {func.__name__} with\nargs: {args}\nkwargs: {kwargs}", getCallerInfo())
            if useChrono:
                start = datetime.now()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                Logger.error(f"An error occurred in function {func.__name__}: {e.__class__.__name__} - {e}", getCallerInfo())
                raise e
            if useChrono:
                end = datetime.now()
                Logger.debug(f"Function {func.__name__} took {end-start} to execute and returned \"{result}\"", getCallerInfo())
            else:
                Logger.debug(f"Function {func.__name__} returned \"{result}\"", getCallerInfo())
            return result
        return wrapper
    return pre_wrapper

@strictTypeCheck
def chrono(func : Callable):
    """
    Decorator to print the execution time of a function
    usage:
    ```python
    @chrono
    def my_function(arg1, arg2, kwarg1=None):
        return arg1+arg2

    my_function("value1", "value2", kwarg1="value3")
    ```
    will print:
    ```log
    [datetime] [   DEBUG   ] Function my_function took 0.0001s to execute
    ```
    """
    @strictTypeCheck
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        debug(f"Function {func.__name__} took {end-start} to execute")
        return result
    return wrapper

# create the instance of the logger
Logger()
