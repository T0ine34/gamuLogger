import os
import tempfile

import pytest

from gamuLogger.custom_types import COLORS, Levels, Target, TerminalTarget


class TempFile:
    def __enter__(self):
        self.fd, self.filepath = tempfile.mkstemp()
        return self.filepath

    def __exit__(self, exc_type, exc_value, traceback):
        os.close(self.fd)
        os.remove(self.filepath)


class Test_Levels:
    def test_values(self):
        assert int(Levels.TRACE) == 0
        assert int(Levels.DEBUG) == 1
        assert int(Levels.INFO) == 2
        assert int(Levels.WARNING) == 3
        assert int(Levels.ERROR) == 4
        assert int(Levels.CRITICAL) == 5

    def test_superiority(self):
        assert Levels.TRACE <= Levels.DEBUG
        assert Levels.DEBUG <= Levels.INFO
        assert Levels.INFO <= Levels.WARNING
        assert Levels.WARNING <= Levels.ERROR
        assert Levels.ERROR <= Levels.CRITICAL

    def test_from_string(self):
        assert Levels.from_string('trace') == Levels.TRACE
        assert Levels.from_string('debug') == Levels.DEBUG
        assert Levels.from_string('info') == Levels.INFO
        assert Levels.from_string('warning') == Levels.WARNING
        assert Levels.from_string('error') == Levels.ERROR
        assert Levels.from_string('critical') == Levels.CRITICAL
        assert Levels.from_string('invalid') == Levels.INFO

    def test_str(self):
        assert str(Levels.TRACE) ==         '  TRACE   '
        assert str(Levels.DEBUG) ==         '  DEBUG   '
        assert str(Levels.INFO) ==          '   INFO   '
        assert str(Levels.WARNING) ==       ' WARNING  '
        assert str(Levels.ERROR) ==         '  ERROR   '
        assert str(Levels.CRITICAL) ==      ' CRITICAL '

    def test_color(self):
        assert Levels.TRACE.color() == COLORS.BLUE
        assert Levels.DEBUG.color() == COLORS.CYAN
        assert Levels.INFO.color() == COLORS.GREEN
        assert Levels.WARNING.color() == COLORS.YELLOW
        assert Levels.ERROR.color() == COLORS.RED
        assert Levels.CRITICAL.color() == COLORS.DARK_RED


class Test_TerminalTarget:
    def test_str(self):
        assert str(TerminalTarget.STDOUT) == 'stdout'
        assert str(TerminalTarget.STDERR) == 'stderr'

    def test_from_string(self):
        assert TerminalTarget.from_string('stdout') == TerminalTarget.STDOUT
        assert TerminalTarget.from_string('stderr') == TerminalTarget.STDERR
        pytest.raises(ValueError, TerminalTarget.from_string, 'invalid')


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
        target = Target(TerminalTarget.STDOUT)
        assert target.type == Target.Type.TERMINAL
        assert str(target) == "stdout"
        Target.clear()
        target = Target(TerminalTarget.STDERR)
        assert target.type == Target.Type.TERMINAL
        assert str(target) == "stderr"
        Target.clear()

    def test_from_string(self):
        fd, filepath = tempfile.mkstemp()
        target = Target.from_file(filepath)
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
