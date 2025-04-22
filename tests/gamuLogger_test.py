import os
import re
import sys
import tempfile
from time import sleep

import pytest

from gamuLogger.gamuLogger import (LEVELS,  # type: ignore
                                   TERMINAL_TARGETS, Logger, Module, Target,
                                   chrono, critical, debug, debugFunc,
                                   deepDebug, deepDebugFunc, error, info,
                                   message, warning)


class Test_Logger:
    def test_deepDebug(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.DEEP_DEBUG)
        deepDebug("This is a deep debug message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] This is a deep debug message", result)

    def test_debug(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.DEBUG)
        debug("This is a debug message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] This is a debug message", result)

    def test_info(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.INFO)
        info("This is an info message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] This is an info message", result)

    def test_warning(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.WARNING)
        warning("This is a warning message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.* WARNING  .*\] This is a warning message", result)

    def test_error(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.ERROR)
        error("This is an error message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  ERROR   .*\] This is an error message", result)

    def test_critical(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.CRITICAL)
        critical("This is a critical message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.* CRITICAL .*\] This is a critical message", result)

    def test_message(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.INFO)
        message("This is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"This is a message", result)

    def test_multiline(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.INFO)
        info("This is a message\nThis is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] This is a message\n                                 \| This is a message", result)

    def test_module(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.INFO)
        Logger.setModule("test")
        info("This is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] \[ .*      test     .* \] This is a message", result)

    def test_sub_module(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.INFO)
        Logger.setModule("test")
        def subFunc():
            Logger.setModule("test.sub")
            info("This is a message")
        subFunc()
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] \[ .*     test     .* \] \[.*    sub    .* \] This is a message", result)

    def test_sub_sub_module(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.INFO)
        Logger.setModule("test")
        def subFunc():
            Logger.setModule("test.sub")
            def subSubFunc():
                Logger.setModule("test.sub.sub")
                info("This is a message")
            subSubFunc()
        subFunc()
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] \[ .*     test     .* \] \[.*    sub    .* \] \[.*    sub    .* \] This is a message", result)

    def test_multiline_module(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.INFO)
        Logger.setModule("test")
        info("This is a message\nThis is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] \[ .*      test     .* \] This is a message\n                                                     \| This is a message", result)

    def test_too_long_module_name(self):
        Logger.reset()
        Module.clear()
        with pytest.raises(ValueError):
            Logger.setModule("This module name is too long")

    def test_chrono(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.DEBUG)

        @chrono
        def test():
            sleep(1)

        test()
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] Function test took 0:00:01.\d{6} to execute", result)

    def test_deepDebugFunc(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.DEEP_DEBUG)

        @deepDebugFunc(True)
        def test():
            return "This is a deep debug function"

        test()
        captured = capsys.readouterr()
        result = captured.out #type: str
        print(result)
        result = result.split("\n") #type: list[str]
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] Calling test with", result[0])
        assert re.match(r"                                 \| args: \(\)", result[1])
        assert re.match(r"                                 \| kwargs: {}", result[2])
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] Function test took 0:00:00 to execute and returned \"This is a deep debug function\"", result[3])

    def test_debugFunc(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.DEBUG)

        @debugFunc(False)
        def test():
            return "This is a debug function"

        test()
        captured = capsys.readouterr()
        result = captured.out #type: str
        print(result)
        result = result.split("\n") #type: list[str]
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] Calling test with", result[0])
        assert re.match(r"                                 \| args: \(\)", result[1])
        assert re.match(r"                                 \| kwargs: {}", result[2])
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] Function test returned \"This is a debug function\"", result[3])

    def test_setLevel(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.setLevel("stdout", LEVELS.INFO)

        debug("This is a debug message that should not be displayed")

        Logger.setLevel("stdout", LEVELS.DEBUG)

        debug("This is a debug message that should be displayed")

        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] This is a debug message that should be displayed", result)


    def test_fileTarget(self):
        Logger.reset()
        Module.clear()

        with tempfile.TemporaryDirectory() as tmpdirname:
            Logger.addTarget(tmpdirname + "/test.log")

            info("This is a message")

            with open(tmpdirname + "/test.log", "r") as file:
                result = file.read()


            print(result)

            assert re.match(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[   INFO   \] This is a message", result)

    def test_customFunctionAsTarget(self):
        Logger.reset()
        Module.clear()

        out = []
        def customFunction(message):
            out.append(message)

        Logger.addTarget(customFunction)

        info("This is a message")

        result = out[0]

        print(result)

        assert re.match(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[   INFO   \] This is a message", result)
