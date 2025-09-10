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

import os
import re
import sys
from enum import Enum

import pytest

from gamuLogger.utils import (COLORS, CustomEncoder, colorize, get_time,
                              replace_newline, schema2regex, string2bytes,
                              string2seconds)

FILEPATH = os.path.abspath(__file__)



def test_get_time_format():
    # Act
    time_str = get_time()

    # Assert
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", time_str) is not None # id: valid_format


class TestReplaceNewline:
    @pytest.mark.parametrize(
        "string, indent, expected_output",
        [
            ("Hello\nWorld", 33, "Hello\n                                 | World"), # id: default_indent
            ("Hello\nWorld", 10, "Hello\n          | World"), # id: custom_indent
            ("Hello\nWorld\nTest", 5, "Hello\n     | World\n     | Test"), # id: multiple_newlines
            ("Hello\n\nWorld", 2, "Hello\n  | \n  | World"), # id: consecutive_newlines

        ],
    )
    def test_replace_newline_happy_path(self, string, indent, expected_output):

        # Act
        actual_output = replace_newline(string, indent)

        # Assert
        assert actual_output == expected_output

    @pytest.mark.parametrize(
        "string, indent, expected_output",
        [
            ("\n", 2, "\n  | "), # id: only_newline
            ("", 2, ""), # id: empty_string
            ("Hello", 2, "Hello"), # id: no_newline

        ],
    )
    def test_replace_newline_edge_cases(self, string, indent, expected_output):

        # Act
        actual_output = replace_newline(string, indent)

        # Assert
        assert actual_output == expected_output


class MockEnum(Enum):
    VALUE1 = 1
    VALUE2 = 2

class MockObject:
    def __init__(self):
        self.value = 1

    def __str__(self):
        return f"MockObject value={self.value}"

class MockObjectNoStr:
    def __init__(self):
        self.value = 1


class TestCustomEncoder:

    @pytest.mark.parametrize(
        "input_obj, expected_output",
        [
            (MockEnum.VALUE1, "VALUE1"),  # id: enum_value
            ({"key1": "value1", "key2": "value2"}, "{'key1': 'value1', 'key2': 'value2'}"),  # id: dict_object
            ("test string", "test string"),  # id: string_object
            (123, "123"),  # id: int_object
            (123.45, "123.45"), # id: float_object
            ([1, 2, 3], "[1, 2, 3]"), # id: list_object
            ((1, 2, 3), "(1, 2, 3)"), # id: tuple_object
        ],
    )
    def test_default_happy_path(self, input_obj, expected_output):
        # Act
        encoder = CustomEncoder()
        actual_output = encoder.default(input_obj)

        # Assert
        assert actual_output == expected_output

    @pytest.mark.parametrize(
        "input_obj, expected_output",
        [
            (MockObject(), {'value': 1}), # id: object_with_dict
            (MockObjectNoStr(), {'value': 1}), # id: object_with_dict_no_str_method
        ],
    )
    def test_default_object_with_dict(self, input_obj, expected_output):

        # Act
        encoder = CustomEncoder()
        actual_output = encoder.default(input_obj)

        # Assert
        assert actual_output == expected_output


class TestColorize:
    @pytest.mark.parametrize(
        "color, string, expected_output",
        [
            (COLORS.RED, "test", f"{COLORS.RED}test{COLORS.RESET}"), # id: red_string
            (COLORS.GREEN, "test", f"{COLORS.GREEN}test{COLORS.RESET}"), # id: green_string
            (COLORS.YELLOW, "test", f"{COLORS.YELLOW}test{COLORS.RESET}"), # id: yellow_string
            (COLORS.BLUE, "test", f"{COLORS.BLUE}test{COLORS.RESET}"), # id: blue_string
            (COLORS.MAGENTA, "test", f"{COLORS.MAGENTA}test{COLORS.RESET}"), # id: magenta_string
            (COLORS.CYAN, "test", f"{COLORS.CYAN}test{COLORS.RESET}"), # id: cyan_string
            (COLORS.RESET, "test", f"{COLORS.RESET}test{COLORS.RESET}"), # id: reset_string
        ],
    )
    def test_colorize_happy_path(self, color, string, expected_output):

        # Act
        actual_output = colorize(color, string)

        # Assert
        assert actual_output == expected_output

    @pytest.mark.parametrize(
        "color, string, expected_output",
        [
            (COLORS.RED, "", f"{COLORS.RED}{COLORS.RESET}"), # id: empty_string
            (COLORS.RED, " ", f"{COLORS.RED} {COLORS.RESET}"), # id: space_string
            (COLORS.RED, "\n", f"{COLORS.RED}\n{COLORS.RESET}"), # id: newline_string
            (COLORS.RED, "test\nstring", f"{COLORS.RED}test\nstring{COLORS.RESET}"), # id: multiline_string

        ],
    )
    def test_colorize_edge_cases(self, color, string, expected_output):

        # Act
        actual_output = colorize(color, string)

        # Assert
        assert actual_output == expected_output


class TestString2Seconds:
    @pytest.mark.parametrize(
        "input_string, expected_output",
        [
            ("1 second", 1),  # id: single_unit_second
            ("2 minutes", 2*60),  # id: single_unit_minutes
            ("3 hours", 3*60*60),  # id: single_unit_hours
            ("4 days", 4*24*60*60),  # id: single_unit_days
            ("5 weeks", 5*7*24*60*60),  # id: single_unit_weeks
            ("6 months", 6*30*24*60*60),  # id: single_unit_months
            ("7 years", 7*365*24*60*60),  # id: single_unit_years
            ("1 hour 30 minutes", 1*60*60 + 30*60),  # id: hour_minute
            ("2 days 3 hours 15 minutes", 2*24*60*60 + 3*60*60 + 15*60),  # id: day_hour_minute
            ("1 year 1 month 1 week 1 day 1 hour 1 minute 1 second",
             1*365*24*60*60 + 1*30*24*60*60 + 1*7*24*60*60 + 1*24*60*60 + 1*60*60 + 1*60 + 1),  # id: complex_units
            ("1 second 2 minutes 3 hours", 1 + 2*60 + 3*60*60),  # id: mixed_units
            ("1 second 2 minutes", 1 + 2*60),  # id: mixed_units_no_hours
            ("0 seconds", 0),  # id: zero_seconds
        ],
    )
    def test_string2seconds_happy_path(self, input_string, expected_output):
        # Act
        actual_output = string2seconds(input_string)

        # Assert
        assert actual_output == expected_output

    @pytest.mark.parametrize(
        "input_string",
        [
            ("1 unknown_unit"),  # id: unknown_unit
            ("two hours"),  # id: non_numeric_value
            ("1hour"),  # id: missing_space
            ("1"),  # id: incomplete_pair
            ("1 hour 2"),  # id: incomplete_last_pair
        ],
    )
    def test_string2seconds_error_cases(self, input_string):
        # Act and Assert
        with pytest.raises((ValueError, KeyError)):
            string2seconds(input_string)

    @pytest.mark.parametrize(
        "input_string, expected_output",
        [
            ("", 0),  # id: empty_string
            ("0 seconds", 0),  # id: zero_seconds
            ("0 hours 0 minutes", 0),  # id: zero_multiple_units
        ],
    )
    def test_string2seconds_edge_cases(self, input_string, expected_output):
        # Act
        actual_output = string2seconds(input_string)

        # Assert
        assert actual_output == expected_output


class TestString2Bytes:
    @pytest.mark.parametrize(
        "input_string, expected_output",
        [
            ("1 B", 1),  # id: single_unit_bytes
            ("2 KB", 1024*2),  # id: single_unit_kilobytes
            ("3 MB", 1024**2*3),  # id: single_unit_megabytes
            ("4 GB", 1024**3*4),  # id: single_unit_gigabytes
            ("5 TB", 1024**4*5),  # id: single_unit_terabytes
            ("6 PB", 1024**5*6),  # id: single_unit_petabytes
            ("1 KB 2 MB 3 GB", 1*1024 + 2*1024**2 + 3*1024**3),  # id: mixed_units
            ("1 TB 512 GB", 1*1024**4 + 512*1024**3),  # id: mixed_units_no_bytes
        ],
    )
    def test_string2bytes_happy_path(self, input_string, expected_output):
        # Act
        actual_output = string2bytes(input_string)

        # Assert
        assert actual_output == expected_output

    @pytest.mark.parametrize(
        "input_string",
        [
            ("1 unknown_unit"),  # id: unknown_unit
            ("two KB"),  # id: non_numeric_value
            ("1KB"),  # id: missing_space
            ("1"),  # id: incomplete_pair
            ("1 KB 2"),  # id: incomplete_last_pair
            ("1 XB"),  # id: invalid_unit
        ],
    )
    def test_string2bytes_error_cases(self, input_string):
        # Act and Assert
        with pytest.raises((ValueError, KeyError)):
            string2bytes(input_string)

    @pytest.mark.parametrize(
        "input_string, expected_output",
        [
            ("", 0),  # id: empty_string
            ("0 B", 0),  # id: zero_bytes
            ("0 KB 0 MB", 0),  # id: zero_multiple_units
        ],
    )
    def test_string2bytes_edge_cases(self, input_string, expected_output):
        # Act
        actual_output = string2bytes(input_string)

        # Assert
        assert actual_output == expected_output


class TestSchema2Regex:
    @pytest.mark.parametrize(
        "schema, test_string, expected_match",
        [
            ("${date}", "2024-01-01", True),  # Date
            ("${time}", "10:30:00", True),  # Time
            ("${datetime}", "2024-01-01_10:30:00", True),  # Datetime
            ("${year}", "2024", True),  # Year
            ("${month}", "01", True),  # Month
            ("${day}", "01", True),  # Day
            ("${hour}", "10", True),  # Hour
            ("${minute}", "30", True),  # Minute
            ("${second}", "00", True),  # Second
            ("${pid}", "12345", True), # PID (mocked)
            ("test_${date}_${time}", "test_2024-01-01_10:30:00", True), # Combined
            ("test", "test", True), # No placeholders
            ("${date}", "invalid_date", False),  # Invalid date
            ("${time}", "invalid_time", False),  # Invalid time
            ("${datetime}", "invalid_datetime", False),  # Invalid datetime
            ("test_${date}_${time}", "test_invalid_date_10:30:00", False), # Combined with invalid date
            ("test_${date}_${time}", "test_2024-01-01_invalid_time", False), # Combined with invalid time
            ("${unknown}", "anything", False), # Unknown placeholder, treated literally
        ],

        ids=["date", "time", "datetime", "year", "month", "day", "hour", "minute", "second", "pid", "combined", "no_placeholders", "invalid_date", "invalid_time", "invalid_datetime", "combined_invalid_date", "combined_invalid_time", "unknown_placeholder"]
    )
    def test_schema2regex(self, monkeypatch, schema, test_string, expected_match):
        # Arrange
        monkeypatch.setattr(os, "getpid", lambda: 12345)

        # Act
        pattern = schema2regex(schema)
        match = pattern.fullmatch(test_string)

        # Assert
        assert bool(match) == expected_match
