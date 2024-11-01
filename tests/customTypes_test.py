import os
import tempfile
from xml.etree import ElementTree as ET

import pytest

from gamuLogger.customTypes import (COLORS, LEVELS,  # type: ignore
                                    SENSITIVE_LEVELS, TERMINAL_TARGETS,
                                    LoggerConfig, Target)


class TempFile:
    def __enter__(self):
        self.fd, self.filepath = tempfile.mkstemp()
        return self.filepath

    def __exit__(self, exc_type, exc_value, traceback):
        os.close(self.fd)
        os.remove(self.filepath)


class Test_LEVELS:
    def test_values(self):
        assert int(LEVELS.DEEP_DEBUG) == 0
        assert int(LEVELS.DEBUG) == 1
        assert int(LEVELS.INFO) == 2
        assert int(LEVELS.WARNING) == 3
        assert int(LEVELS.ERROR) == 4
        assert int(LEVELS.CRITICAL) == 5

    def test_superiority(self):
        assert LEVELS.DEEP_DEBUG <= LEVELS.DEBUG
        assert LEVELS.DEBUG <= LEVELS.INFO
        assert LEVELS.INFO <= LEVELS.WARNING
        assert LEVELS.WARNING <= LEVELS.ERROR
        assert LEVELS.ERROR <= LEVELS.CRITICAL

    def test_from_string(self):
        assert LEVELS.from_string('debug') == LEVELS.DEBUG
        assert LEVELS.from_string('info') == LEVELS.INFO
        assert LEVELS.from_string('warning') == LEVELS.WARNING
        assert LEVELS.from_string('error') == LEVELS.ERROR
        assert LEVELS.from_string('critical') == LEVELS.CRITICAL
        assert LEVELS.from_string('invalid') == LEVELS.INFO

    def test_str(self):
        assert str(LEVELS.DEEP_DEBUG) ==    '  DEBUG   '
        assert str(LEVELS.DEBUG) ==         '  DEBUG   '
        assert str(LEVELS.INFO) ==          '   INFO   '
        assert str(LEVELS.WARNING) ==       ' WARNING  '
        assert str(LEVELS.ERROR) ==         '  ERROR   '
        assert str(LEVELS.CRITICAL) ==      ' CRITICAL '

    def test_color(self):
        assert LEVELS.DEEP_DEBUG.color() == COLORS.BLUE
        assert LEVELS.DEBUG.color() == COLORS.BLUE
        assert LEVELS.INFO.color() == COLORS.GREEN
        assert LEVELS.WARNING.color() == COLORS.YELLOW
        assert LEVELS.ERROR.color() == COLORS.RED
        assert LEVELS.CRITICAL.color() == COLORS.DARK_RED


class Test_SENSITIVE_LEVELS:
    def test_from_string(self):
        assert SENSITIVE_LEVELS.from_string('hide') == SENSITIVE_LEVELS.HIDE
        assert SENSITIVE_LEVELS.from_string('show') == SENSITIVE_LEVELS.SHOW
        assert SENSITIVE_LEVELS.from_string('invalid') == SENSITIVE_LEVELS.HIDE

    def test_from_bool(self):
        assert SENSITIVE_LEVELS.from_bool(True) == SENSITIVE_LEVELS.SHOW
        assert SENSITIVE_LEVELS.from_bool(False) == SENSITIVE_LEVELS.HIDE

class Test_TERMINAL_TARGETS:
    def test_str(self):
        assert str(TERMINAL_TARGETS.STDOUT) == 'stdout'
        assert str(TERMINAL_TARGETS.STDERR) == 'stderr'

    def test_from_string(self):
        assert TERMINAL_TARGETS.from_string('stdout') == TERMINAL_TARGETS.STDOUT
        assert TERMINAL_TARGETS.from_string('stderr') == TERMINAL_TARGETS.STDERR
        pytest.raises(ValueError, TERMINAL_TARGETS.from_string, 'invalid')


class Test_Target:
    class Test_Type:
        def test_str(self):
            assert str(Target.Type.FILE) == 'file'
            assert str(Target.Type.TERMINAL) == 'terminal'

    def test_from_function(self):
        def function():
            pass
        target = Target(function)
        assert target.type == Target.Type.FILE
        assert str(target) == "function"

    def test_from_terminal(self):
        target = Target(TERMINAL_TARGETS.STDOUT)
        assert target.type == Target.Type.TERMINAL
        assert str(target) == "stdout"
        Target.clear()
        target = Target(TERMINAL_TARGETS.STDERR)
        assert target.type == Target.Type.TERMINAL
        assert str(target) == "stderr"
        Target.clear()

    def test_from_string(self):
        fd, filepath = tempfile.mkstemp()
        target = Target.fromFile(filepath)
        assert target.type == Target.Type.FILE
        assert os.path.exists(filepath)
        assert str(target) == filepath

        # cleanup
        os.close(fd)
        os.remove(filepath)
        Target.clear()

    def test_get_existing_target(self):
        def function():
            pass
        Target(function)

        target = Target.get("function")
        assert target.type == Target.Type.FILE
        assert str(target) == "function"
        Target.clear()
