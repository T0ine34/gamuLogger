#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ###############################################################################################
#                                   PYLINT
# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=no-name-in-module
# pylint: disable=import-error
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=protected-access
# ###############################################################################################

import re
import tempfile
from time import sleep
from unittest.mock import MagicMock

import pytest

from gamuLogger.gamu_logger import (Levels, Logger, Module, chrono, debug,
                                    debug_func, error, info, message,
                                    trace_func, warning)


class Test_Logger:

    @pytest.mark.parametrize(
        "level, expected",
        [
            (Logger.trace,    r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  TRACE  .*\] This is a message"),
            (Logger.debug,    r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG  .*\] This is a message"),
            (Logger.info,     r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  INFO   .*\] This is a message"),
            (Logger.warning,  r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.* WARNING .*\] This is a message"),
            (Logger.error,    r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  ERROR  .*\] This is a message"),
            (Logger.fatal,    r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  FATAL  .*\] This is a message")
        ],
        ids=[
            "TRACE",
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "FATAL"
        ],
    )
    def test_levels(self, level, expected, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.TRACE)
        Logger.set_module("test")
        level("This is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(expected, result)

    def test_message(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.INFO)
        message("This is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"This is a message", result)

    def test_multiline(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.INFO)
        info("This is a message\nThis is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  INFO   .*\] This is a message\n                                \| This is a message", result)

    def test_module(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.INFO)
        Logger.set_module("test")
        info("This is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  INFO   .*\] \[ .*      test     .* \] This is a message", result)

    def test_sub_module(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.INFO)
        Logger.set_module("test")
        def subFunc():
            Logger.set_module("test.sub")
            info("This is a message")
        subFunc()
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  INFO   .*\] \[ .*     test     .* \] \[.*    sub    .* \] This is a message", result)

    def test_sub_sub_module(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
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
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  INFO   .*\] \[ .*     test     .* \] \[.*    sub    .* \] \[.*    sub    .* \] This is a message", result)

    def test_multiline_module(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.INFO)
        Logger.set_module("test")
        info("This is a message\nThis is a message")
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  INFO   .*\] \[ .*      test     .* \] This is a message\n                                                    \| This is a message", result)

    def test_too_long_module_name(self):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        with pytest.raises(ValueError):
            Logger.set_module("This module name is too long")

    def test_chrono(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.DEBUG)

        @chrono
        def test():
            sleep(1)

        test()
        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG  .*\] Function test took 0:00:01.\d{6} to execute", result)

    def test_trace_func(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.TRACE)

        @trace_func(True)
        def test():
            return "This is a trace function"

        test()
        captured = capsys.readouterr()
        result = captured.out #type: str
        print(result)
        result = result.split("\n") #type: list[str]
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  TRACE  .*\] Calling test with", result[0])
        assert re.match(r"                                \| args: \(\)", result[1])
        assert re.match(r"                                \| kwargs: {}", result[2])
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  TRACE  .*\] Function test took 0:00:00 to execute and returned \"This is a trace function\"", result[3])

    def test_debug_func(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.DEBUG)

        @debug_func(False)
        def test():
            return "This is a debug function"

        test()
        captured = capsys.readouterr()
        result = captured.out #type: str
        print(result)
        result = result.split("\n") #type: list[str]
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG  .*\] Calling test with", result[0])
        assert re.match(r"                                \| args: \(\)", result[1])
        assert re.match(r"                                \| kwargs: {}", result[2])
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG  .*\] Function test returned \"This is a debug function\"", result[3])

    def test_set_level(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        Logger.set_level("stdout", Levels.INFO)

        debug("This is a debug message that should not be displayed")

        Logger.set_level("stdout", Levels.DEBUG)

        debug("This is a debug message that should be displayed")

        captured = capsys.readouterr()
        result = captured.out
        print(result)
        assert re.match(r"\[.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*\] \[.*  DEBUG  .*\] This is a debug message that should be displayed", result)

    def test_fileTarget(self):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        with tempfile.TemporaryDirectory() as tmpdirname:
            Logger.add_target(f"{tmpdirname}/test.log")

            info("This is a message")

            with open(f"{tmpdirname}/test.log", mode="r", encoding="utf-8") as file:
                result = file.read()


            print(result)

            assert re.match(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[  INFO   \] This is a message", result)

    def test_customFunctionAsTarget(self):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)
        out = []
        def customFunction(msg : str):
            out.append(msg)

        Logger.add_target(customFunction)

        info("This is a message")

        result = out[0]

        print(result)

        assert re.match(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[  INFO   \] This is a message", result)

    def test_module_specific_levels(self, capsys):
        Logger.reset()
        Module.clear()
        Module.set_default_level(Levels.TRACE)

        # Set up modules with specific levels
        Logger.set_level("stdout", Levels.DEBUG)            # Default level for stdout
        Logger.set_module_level("module1", Levels.DEBUG)    # Set DEBUG level for module1
        Logger.set_module_level("module2", Levels.WARNING)  # Set WARNING level for module2

        # Log messages from different modules
        Logger.set_module("module1")
        debug("This is a debug message from module1")       # Should be displayed
        info("This is an info message from module1")        # Should be displayed
        warning("This is a warning message from module1")   # Should be displayed
        error("This is an error message from module1")      # Should be displayed

        Logger.set_module("module2")
        debug("This is a debug message from module2")       # Should NOT be displayed
        info("This is an info message from module2")        # Should NOT be displayed
        warning("This is a warning message from module2")   # Should be displayed
        error("This is an error message from module2")      # Should be displayed

        # Capture the output
        captured = capsys.readouterr()
        result = captured.out
        print(result)

        # Assertions
        assert re.search(r"This is a debug message from module1", result)
        assert re.search(r"This is an info message from module1", result)
        assert re.search(r"This is a warning message from module1", result)
        assert re.search(r"This is an error message from module1", result)
        assert not re.search(r"This is a debug message from module2", result)
        assert not re.search(r"This is an info message from module2", result)
        assert re.search(r"This is a warning message from module2", result)
        assert re.search(r"This is an error message from module2", result)

    @pytest.mark.parametrize(
        "name, level",
        [
            ("module1", Levels.DEBUG),  # String name
            ("module2", Levels.WARNING), # String name, different level
            ("a.b.c", Levels.TRACE), # Dotted module name
        ],
        ids=["string_name_debug", "string_name_warning", "dotted_module_name"]
    )
    def test_set_module_level(self, name, level, monkeypatch):
        # Arrange
        get_instance_mock = MagicMock()
        monkeypatch.setattr(Logger, "get_instance", get_instance_mock)
        set_level_mock = MagicMock()
        monkeypatch.setattr(Module, "set_level", set_level_mock)


        # Act
        Logger.set_module_level(name, level)

        # Assert
        get_instance_mock.assert_called_once()
        set_level_mock.assert_called_once_with(name, level)

    @pytest.mark.parametrize(
        "level",
        [
            (Levels.DEBUG,),  # DEBUG level
            (Levels.WARNING,),  # WARNING level
            (Levels.INFO,), # INFO level
        ],
        ids=["debug_level", "warning_level", "info_level"]
    )
    def test_set_default_module_level(self, level, monkeypatch):
        # Arrange
        get_instance_mock = MagicMock()
        monkeypatch.setattr(Logger, "get_instance", get_instance_mock)
        set_default_level_mock = MagicMock()
        monkeypatch.setattr(Module, "set_default_level", set_default_level_mock)

        # Act
        Logger.set_default_module_level(level)

        # Assert
        get_instance_mock.assert_called_once()
        set_default_level_mock.assert_called_once_with(level)
