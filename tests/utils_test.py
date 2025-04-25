import os
import re
import sys
from enum import Enum

import pytest

FILEPATH = os.path.abspath(__file__)

from gamuLogger.utils import (COLORS, CustomEncoder, colorize,
                              get_executable_formatted, get_time,
                              replace_newline, split_long_string)


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


class TestSplitLongString:
    @pytest.mark.parametrize(
        "string, length, expected_output",
        [
            ("Hello World", 5, "Hello\nWorld"), # id: short_string
            ("Hello World", 6, "Hello\nWorld"), # id: exact_length
            ("Hello World", 11, "Hello World"), # id: string_less_than_length
            ("This is a longer string that needs to be split", 10, "This is a\nlonger\nstring\nthat needs\nto be\nsplit"), # id: long_string
            ("This is a string with\na newline", 10, "This is a\nstring\nwith\na newline"), # id: string_with_newline
            ("This is a string with multiple   spaces", 10, "This is a\nstring\nwith\nmultiple  \nspaces"), # id: string_with_multiple_spaces

        ],
    )
    def test_split_long_string_happy_path(self, string, length, expected_output):

        # Act
        actual_output = split_long_string(string, length)

        # Assert
        assert actual_output == expected_output

    @pytest.mark.parametrize(
        "string, length",
        [
            ("Hello World", 2), # id: word_longer_than_length
            ("HelloWorld", 8), # id: no_spaces
        ],
    )
    def test_split_long_string_error_cases(self, string, length):

        # Act and Assert
        with pytest.raises(ValueError):
            split_long_string(string, length)


    @pytest.mark.parametrize(
        "string, length, expected_output",
        [
            ("", 5, ""), # id: empty_string
            (" ", 5, " "), # id: single_space
            ("\n", 5, "\n"), # id: only_newline
        ],
    )
    def test_split_long_string_edge_cases(self, string, length, expected_output):

        # Act
        actual_output = split_long_string(string, length)

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


class TestGetExecutableFormatted:
    @pytest.mark.parametrize(
        "sys_executable, sys_argv, expected_output",
        [
            ("/usr/bin/python3", ["/path/to/script.py"], "python3 /path/to/script.py"), # id: python3_executable
            ("/usr/bin/python", ["/path/to/script.py"], "python /path/to/script.py"), # id: python_executable
            ("/usr/bin/python3.10", ["/path/to/script.py"], "python3.10 /path/to/script.py"), # id: python310_executable
            ("/home/user/my_python", ["/path/to/script.py"], "my_python /path/to/script.py"), # id: custom_python_executable

        ],
    )
    def test_get_executable_formatted_python(self, monkeypatch, sys_executable, sys_argv, expected_output):
        # Arrange
        monkeypatch.setattr(sys, "executable", sys_executable)
        monkeypatch.setattr(sys, "argv", sys_argv)


        # Act
        actual_output = get_executable_formatted()

        # Assert
        assert actual_output == expected_output

    @pytest.mark.parametrize(
        "sys_executable, sys_argv, expected_output",
        [
            ("/usr/bin/my_program", ["/path/to/script.py"], "my_program"), # id: non_python_executable
            ("/usr/bin/another_program", ["/path/to/script.py"], "another_program"), # id: another_non_python_executable
        ],

    )
    def test_get_executable_formatted_non_python(self, monkeypatch, sys_executable, sys_argv, expected_output):
        # Arrange
        monkeypatch.setattr(sys, "executable", sys_executable)
        monkeypatch.setattr(sys, "argv", sys_argv)

        # Act
        actual_output = get_executable_formatted()

        # Assert
        assert actual_output == expected_output

    @pytest.mark.parametrize(
        "sys_executable, sys_argv, expected_output",
        [
            ("/usr/bin/python3", [], "python3 "), # id: empty_sys_argv
            ("/usr/bin/python3", [""], "python3 "), # id: empty_string_sys_argv
        ],
    )
    def test_get_executable_formatted_edge_cases(self, monkeypatch, sys_executable, sys_argv, expected_output):
        # Arrange
        monkeypatch.setattr(sys, "executable", sys_executable)
        monkeypatch.setattr(sys, "argv", sys_argv)

        # Act
        actual_output = get_executable_formatted()

        # Assert
        assert actual_output == expected_output
