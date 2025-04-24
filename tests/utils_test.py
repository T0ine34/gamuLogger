import os
import re
import sys

import pytest

FILEPATH = os.path.abspath(__file__)

from gamuLogger.utils import get_time, replace_newline, split_long_string


def test_get_time():
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", get_time())

def test_replace_newline():
    assert replace_newline("Hello\nWorld") == "Hello\n                                 | World"
    assert replace_newline("Hello\nWorld", 10) == "Hello\n          | World"
    assert replace_newline("\n", 2) == "\n  | "
    assert replace_newline("", 2) == ""
    assert replace_newline("Hello", 2) == "Hello"


def test_split_long_string():
    assert split_long_string("Hello World", 5) == "Hello\nWorld"
    assert split_long_string("Hello World", 6) == "Hello\nWorld"
    pytest.raises(ValueError, split_long_string, "Hello World", 2)
    pytest.raises(ValueError, split_long_string, "HelloWorld", 8)
    assert split_long_string("Hello World", 11) == "Hello World"
