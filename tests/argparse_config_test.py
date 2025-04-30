import argparse
from unittest.mock import MagicMock

import pytest

from gamuLogger.argparse_config import (config_argparse, config_logger,
                                        validate_level, validate_log_file,
                                        validate_module_level)
from gamuLogger.gamu_logger import Levels, Logger, Target


class Test_ValidateModuleLevel:
    @pytest.mark.parametrize(
        "_input, expected_name, expected_level",
        [
            ("module1:INFO", "module1", Levels.INFO),
            ("module2:DEBUG", "module2", Levels.DEBUG),
            ("module3:WARNING", "module3", Levels.WARNING),
            ("a.b.c:TRACE", "a.b.c", Levels.TRACE),
        ],
        ids=["info", "debug", "warning", "trace"]
    )
    def test_valid_input(self, _input, expected_name, expected_level):

        # Act
        name, level = validate_module_level(_input)

        # Assert
        assert name == expected_name
        assert level == expected_level

    @pytest.mark.parametrize(
        "_input",
        [
            "invalid_input",  # Missing colon
            "module1:INVALID_LEVEL",  # Invalid level
            ":", # only colon
            "module:", # no level
            ":info", # no module
        ],
        ids=["missing_colon", "invalid_level", "only_colon", "no_level", "no_module"]
    )
    def test_invalid_input(self, _input):

        # Act & Assert
        with pytest.raises(argparse.ArgumentTypeError):
            validate_module_level(_input)


class TestValidateLogFile:
    @pytest.mark.parametrize(
        "_input, expected_file, expected_level",
        [
            ("test.log:INFO", "test.log", Levels.INFO),
            ("test.log:DEBUG", "test.log", Levels.DEBUG),
            ("test.log:WARNING", "test.log", Levels.WARNING),
            ("test.log", "test.log", Levels.INFO),  # Default level
            ("test.log:", "test.log", Levels.INFO), # Empty level, defaults to INFO
            ("test.log:info", "test.log", Levels.INFO), # Lowercase level
        ],
        ids=["info", "debug", "warning", "default_level", "empty_level", "lowercase_level"]
    )
    def test_valid_input(self, _input, expected_file, expected_level):

        # Act
        file, level = validate_log_file(_input)

        # Assert
        assert file == expected_file
        assert level == expected_level

    @pytest.mark.parametrize(
        "_input",
        [
            "test.log:INVALID_LEVEL",  # Invalid level
            ":", # only colon
            ":info", # no file
            "test.log:123", # Invalid level type
        ],
        ids=["invalid_level", "only_colon", "no_file", "invalid_level_type"]
    )
    def test_invalid_input(self, _input):

        # Act & Assert
        with pytest.raises(argparse.ArgumentTypeError):
            validate_log_file(_input)


class TestValidateLevel:
    @pytest.mark.parametrize(
        "_input, expected_level",
        [
            ("INFO", Levels.INFO),
            ("DEBUG", Levels.DEBUG),
            ("WARNING", Levels.WARNING),
            ("ERROR", Levels.ERROR),
            ("FATAL", Levels.FATAL),
            ("info", Levels.INFO),  # Case-insensitive
            ("DeBuG", Levels.DEBUG),  # Case-insensitive
        ],
        ids=["info", "debug", "warning", "error", "critical", "info_lowercase", "debug_mixedcase"]
    )
    def test_valid_input(self, _input, expected_level):

        # Act
        level = validate_level(_input)

        # Assert
        assert level == expected_level

    @pytest.mark.parametrize(
        "_input",
        [
            "INVALID_LEVEL",  # Invalid level
            "123",  # Invalid level type
            "", # Empty string
        ],
        ids=["invalid_level_name", "invalid_level_type", "empty_string"]
    )
    def test_invalid_input(self, _input):

        # Act & Assert
        with pytest.raises(argparse.ArgumentTypeError):
            validate_level(_input)


class TestConfigArgparse:
    @pytest.mark.parametrize(
        "allow_other_targets",
        [
            (True,),  # Allow other targets
            (False,), # Do not allow other targets
        ],
        ids=["allow_other_targets", "do_not_allow_other_targets"]
    )
    def test_config_argparse(self, allow_other_targets):
        # Arrange
        parser = argparse.ArgumentParser()

        # Act
        config_argparse(parser, allow_other_targets=allow_other_targets)

        # Assert
        actions = {action.dest: action for action in parser._actions}
        assert "verbose" in actions
        assert "quiet" in actions
        assert "level" in actions
        assert actions["verbose"].default == 0
        assert actions["quiet"].default == 0
        assert actions["level"].default == "info"
        assert actions["level"].type is validate_level

        if allow_other_targets:
            assert "log_file" in actions
            assert "module_level" in actions
            assert actions["log_file"].default == []
            assert actions["log_file"].type is validate_log_file
            assert actions["module_level"].default == []
            assert actions["module_level"].type is validate_module_level


class TestConfigLogger:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        Logger.reset()
        yield

    @pytest.mark.parametrize(
        "verbose, quiet, level, module_level, log_file",
        [
            (0, 0, Levels.INFO, [], []),  # Default level
            (1, 0, Levels.INFO, [], []),  # Verbose level 1
            (2, 0, Levels.INFO, [], []),  # Verbose level 2
            (0, 1, Levels.INFO, [], []),  # Quiet level 1
            (0, 2, Levels.INFO, [], []),  # Quiet level 2
            (0, 3, Levels.INFO, [], []),  # Quiet level 3, FATAL
            (0, 4, Levels.INFO, [], []),  # Quiet level 4, NONE
            (0, 0, Levels.DEBUG, [], []),  # Level DEBUG
            (0, 0, Levels.WARNING, [], []), # Level WARNING
            (0, 0, Levels.INFO, [("module1", Levels.DEBUG)], []),  # Module level
            (0, 0, Levels.INFO, [("all", Levels.DEBUG)], []), # Default module level
            (0, 0, Levels.INFO, [], [("test.log", Levels.DEBUG)]),  # Log file
        ],
        ids=["default_level", "verbose_1", "verbose_2", "quiet_1", "quiet_2", "quiet_3", "quiet_4", "level_debug", "level_warning", "module_level", "all_module_level", "log_file"]
    )
    def test_config_logger(self, verbose, quiet, level, module_level, log_file, monkeypatch):
        # Arrange
        args = argparse.Namespace(
            verbose=verbose, quiet=quiet, level=level, module_level=module_level, log_file=log_file
        )
        set_level_mock = MagicMock()
        set_module_level_mock = MagicMock()
        set_default_module_level_mock = MagicMock()
        add_target_mock = MagicMock()

        monkeypatch.setattr(Logger, "set_level", set_level_mock)
        monkeypatch.setattr(Logger, "set_module_level", set_module_level_mock)
        monkeypatch.setattr(Logger, "set_default_module_level", set_default_module_level_mock)
        monkeypatch.setattr(Logger, "add_target", add_target_mock)

        # Act
        config_logger(args)

        # Assert
        if verbose > 0:
            if verbose == 1:
                expected_level = Levels.DEBUG
            elif verbose == 2:
                expected_level = Levels.TRACE
            set_level_mock.assert_called_once_with("stdout", expected_level)

        elif quiet > 0:
            if quiet == 1:
                expected_level = Levels.WARNING
            elif quiet == 2:
                expected_level = Levels.ERROR
            elif quiet == 3:
                expected_level = Levels.FATAL
            elif quiet == 4:
                expected_level = Levels.NONE
            set_level_mock.assert_called_once_with("stdout", expected_level)
        else:
            set_level_mock.assert_called_once_with("stdout", level)

        for module, level in module_level:
            if module == "all":
                set_default_module_level_mock.assert_called_once_with(level)
            else:
                set_module_level_mock.assert_any_call(module, level)

        for file, level in log_file:
            add_target_mock.assert_any_call(Target.from_file(file), level)

    @pytest.mark.parametrize(
        "verbose, quiet",
        [
            (3, 0),  # Verbose level too high
            (0, 5),  # Quiet level too high
        ],
        ids=["verbose_too_high", "quiet_too_high"]
    )
    def test_config_logger_invalid_level(self, verbose, quiet):
        # Arrange
        args = argparse.Namespace(
            verbose=verbose, quiet=quiet, level="INFO", module_level=[], log_file=[]
        )

        # Act & Assert
        with pytest.raises(argparse.ArgumentTypeError):
            config_logger(args)
