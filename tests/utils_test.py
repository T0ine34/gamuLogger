import os
import re
import sys

import pytest

FILEPATH = os.path.abspath(__file__)

from gamuLogger.utils import (centerString, getCallerInfo,  # type: ignore
                              getTime, replaceNewLine, splitLongString,
                              strictTypeCheck)


def test_getTime():
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", getTime())

def test_replaceNewLine():
    assert replaceNewLine("Hello\nWorld") == "Hello\n                                 | World"
    assert replaceNewLine("Hello\nWorld", 10) == "Hello\n          | World"
    assert replaceNewLine("\n", 2) == "\n  | "
    assert replaceNewLine("", 2) == ""
    assert replaceNewLine("Hello", 2) == "Hello"

def test_centerString():
    assert centerString("Hello", 10) == "  Hello   "
    assert centerString("Hello", 11) == "   Hello   "
    assert centerString("Hello", 9) == "  Hello  "
    assert centerString("Hello", 5) == "Hello"
    assert centerString("Hello", 3) == "Hello"
    assert centerString("Hello", 0) == "Hello"
    assert centerString("Hello", -10) == "Hello"

def test_strictTypeCheck():
    @strictTypeCheck
    def test(a : int, b : str):
        pass

    @strictTypeCheck
    def test2(a : int, b : str = "Hello"):
        pass

    @strictTypeCheck
    def test3(a : int|float):
        pass

    with pytest.raises(TypeError):
        test(1, 2)

    with pytest.raises(TypeError):
        test(1, 2.0)

    test(1, "2")

    test2(1)
    test2(1, "2")

    with pytest.raises(TypeError):
        test2(1, 2)

    test2(a=1, b="2")

    test3(1)
    test3(1.0)
    test3(1.0)

    with pytest.raises(TypeError):
        test3("1")

def test_splitLongString():
    assert splitLongString("Hello World", 5) == "Hello\nWorld"
    assert splitLongString("Hello World", 6) == "Hello\nWorld"
    pytest.raises(ValueError, splitLongString, "Hello World", 2)
    pytest.raises(ValueError, splitLongString, "HelloWorld", 8)
    assert splitLongString("Hello World", 11) == "Hello World"
