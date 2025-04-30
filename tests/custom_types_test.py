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

import pytest

from gamuLogger.custom_types import COLORS, Levels


class TestCOLORS:
    @pytest.mark.parametrize(
        "color, expected_str",
        [
            (COLORS.RED, '\033[91m'),
            (COLORS.DARK_RED, '\033[91m\033[1m'),
            (COLORS.GREEN, '\033[92m'),
            (COLORS.YELLOW, '\033[93m'),
            (COLORS.BLUE, '\033[94m'),
            (COLORS.MAGENTA, '\033[95m'),
            (COLORS.CYAN, '\033[96m'),
            (COLORS.RESET, '\033[0m'),
            (COLORS.NONE, ''),
        ],
        ids=["red", "dark_red", "green", "yellow", "blue", "magenta", "cyan", "reset", "none"]
    )
    def test_str(self, color, expected_str):
        # Act
        result = str(color)

        # Assert
        assert result == expected_str


    @pytest.mark.parametrize(
        "color, other, expected_result",
        [
            (COLORS.RED, "test", "\033[91mtest"),  # color + string
            ("test", COLORS.RED, "test\033[91m"),  # string + color
            (COLORS.RED, 123, "\033[91m123"),  # color + int
            (123, COLORS.RED, "123\033[91m"),  # int + color

        ],
        ids=["color_plus_string", "string_plus_color", "color_plus_int", "int_plus_color"]
    )
    def test_add_radd(self, color, other, expected_result):

        # Act
        result = color + other

        # Assert
        assert result == expected_result

    @pytest.mark.parametrize(
        "color, expected_repr",
        [
            (COLORS.RED, '\033[91m'),
            (COLORS.DARK_RED, '\033[91m\033[1m'),
            (COLORS.GREEN, '\033[92m'),
            (COLORS.YELLOW, '\033[93m'),
            (COLORS.BLUE, '\033[94m'),
            (COLORS.MAGENTA, '\033[95m'),
            (COLORS.CYAN, '\033[96m'),
            (COLORS.RESET, '\033[0m'),
            (COLORS.NONE, ''),
        ],
        ids=["red", "dark_red", "green", "yellow", "blue", "magenta", "cyan", "reset", "none"]
    )
    def test_repr(self, color, expected_repr):

        # Act
        result = repr(color)

        # Assert
        assert result == expected_repr


class TestLevels:
    @pytest.mark.parametrize(
        "level_str, expected_level",
        [
            ("trace", Levels.TRACE),
            ("debug", Levels.DEBUG),
            ("info", Levels.INFO),
            ("warning", Levels.WARNING),
            ("error", Levels.ERROR),
            ("fatal", Levels.FATAL),
            ("TRACE", Levels.TRACE),  # Case-insensitive
            ("DeBuG", Levels.DEBUG),  # Case-insensitive
            ("iNfO", Levels.INFO),  # Case-insensitive
            ("WARNING", Levels.WARNING), # Case-insensitive
            ("ErRoR", Levels.ERROR),  # Case-insensitive
            ("FATAL", Levels.FATAL), # Case-insensitive
        ],
        ids=["trace", "debug", "info", "warning", "error", "fatal", "trace_uppercase", "debug_mixedcase", "info_mixedcase", "warning_uppercase", "error_mixedcase", "fatal_uppercase"]
    )
    def test_from_string(self, level_str, expected_level):

        # Act
        level = Levels.from_string(level_str)

        # Assert
        assert level == expected_level


    @pytest.mark.parametrize(
        "level_str",
        [
            "invalid",  # Invalid level
            "",  # Empty string
        ],
        ids=["invalid", "empty"]
    )
    def test_from_string_invalid(self, level_str):
        # Act & Assert
        with pytest.raises(ValueError):
            Levels.from_string(level_str)


    @pytest.mark.parametrize(
        "level, expected_str",
        [
            (Levels.TRACE,   '  TRACE  '),
            (Levels.DEBUG,   '  DEBUG  '),
            (Levels.INFO,    '  INFO   '),
            (Levels.WARNING, ' WARNING '),
            (Levels.ERROR,   '  ERROR  '),
            (Levels.FATAL,   '  FATAL  '),
        ],
        ids=["trace", "debug", "info", "warning", "error", "fatal"]
    )
    def test_str(self, level, expected_str):

        # Act
        result = str(level)

        # Assert
        assert result == expected_str

    @pytest.mark.parametrize(
        "level, expected_int",
        [
            (Levels.TRACE, 0),
            (Levels.DEBUG, 1),
            (Levels.INFO, 2),
            (Levels.WARNING, 3),
            (Levels.ERROR, 4),
            (Levels.FATAL, 5),
        ],
        ids=["trace", "debug", "info", "warning", "error", "fatal"]
    )
    def test_int(self, level, expected_int):

        # Act
        result = int(level)

        # Assert
        assert result == expected_int


    @pytest.mark.parametrize(
        "level1, level2, expected_le",
        [
            (Levels.TRACE, Levels.DEBUG, True),
            (Levels.DEBUG, Levels.TRACE, False),
            (Levels.INFO, Levels.INFO, True),
        ],
        ids=["trace_le_debug", "debug_le_trace", "info_le_info"]
    )
    def test_le(self, level1, level2, expected_le):

        # Act
        result = level1 <= level2

        # Assert
        assert result == expected_le

    @pytest.mark.parametrize(
        "level, expected_color",
        [
            (Levels.TRACE, COLORS.CYAN),
            (Levels.DEBUG, COLORS.BLUE),
            (Levels.INFO, COLORS.GREEN),
            (Levels.WARNING, COLORS.YELLOW),
            (Levels.ERROR, COLORS.RED),
            (Levels.FATAL, COLORS.DARK_RED),
        ],
        ids=["trace", "debug", "info", "warning", "error", "fatal"]
    )
    def test_color(self, level, expected_color):

        # Act
        color = level.color()

        # Assert
        assert color == expected_color
