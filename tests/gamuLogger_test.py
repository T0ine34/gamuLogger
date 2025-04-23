import os
import re
import sys
import tempfile
from time import sleep

import pytest

from gamuLogger.gamuLogger import (Levels,  # type: ignore
                                   TerminalTarget, Logger, Module, Target,
                                   chrono, critical, debug, debug_func,
                                   trace, trace_func, error, info,
                                   message, warning)


class Test_Logger:
    def test_trace(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.TRACE)
        trace("This is a trace message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] This is a trace message", result)

    def test_debug(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.DEBUG)
        debug("This is a debug message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] This is a debug message", result)

    def test_info(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.INFO)
        info("This is an info message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] This is an info message", result)

    def test_warning(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.WARNING)
        warning("This is a warning message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.* WARNING  .*\] This is a warning message", result)

    def test_error(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.ERROR)
        error("This is an error message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  ERROR   .*\] This is an error message", result)

    def test_critical(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.CRITICAL)
        critical("This is a critical message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.* CRITICAL .*\] This is a critical message", result)

    def test_message(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.INFO)
        message("This is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"This is a message", result)

    def test_multiline(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.INFO)
        info("This is a message\nThis is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] This is a message\n                                 \| This is a message", result)

    def test_module(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.INFO)
        Logger.set_module("test")
        info("This is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] \[ .*      test     .* \] This is a message", result)

    def test_sub_module(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.INFO)
        Logger.set_module("test")
        def subFunc():
            Logger.set_module("test.sub")
            info("This is a message")
        subFunc()
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] \[ .*     test     .* \] \[.*    sub    .* \] This is a message", result)

    def test_sub_sub_module(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.INFO)
        Logger.set_module("test")
        def subFunc():
            Logger.set_module("test.sub")
            def subSubFunc():
                Logger.set_module("test.sub.sub")
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
        Logger.set_level("stdout", Levels.INFO)
        Logger.set_module("test")
        info("This is a message\nThis is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*   INFO   .*\] \[ .*      test     .* \] This is a message\n                                                     \| This is a message", result)

    def test_too_long_module_name(self):
        Logger.reset()
        Module.clear()
        with pytest.raises(ValueError):
            Logger.set_module("This module name is too long")

    def test_chrono(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.DEBUG)

        @chrono
        def test():
            sleep(1)

        test()
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] Function test took 0:00:01.\d{6} to execute", result)

    def test_trace_func(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.TRACE)

        @trace_func(True)
        def test():
            return "This is a trace function"

        test()
        captured = capsys.readouterr()
        result = captured.out #type: str
        print(result)
        result = result.split("\n") #type: list[str]
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] Calling test with", result[0])
        assert re.match(r"                                 \| args: \(\)", result[1])
        assert re.match(r"                                 \| kwargs: {}", result[2])
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] Function test took 0:00:00 to execute and returned \"This is a trace function\"", result[3])

    def test_debug_func(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.DEBUG)

        @debug_func(False)
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

    def test_set_level(self, capsys):
        Logger.reset()
        Module.clear()
        Logger.set_level("stdout", Levels.INFO)

        debug("This is a debug message that should not be displayed")

        Logger.set_level("stdout", Levels.DEBUG)

        debug("This is a debug message that should be displayed")

        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG   .*\] This is a debug message that should be displayed", result)


    def test_fileTarget(self):
        Logger.reset()
        Module.clear()

        with tempfile.TemporaryDirectory() as tmpdirname:
            Logger.add_target(tmpdirname + "/test.log")

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

        Logger.add_target(customFunction)

        info("This is a message")

        result = out[0]

        print(result)

        assert re.match(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[   INFO   \] This is a message", result)
