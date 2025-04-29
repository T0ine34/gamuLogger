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
# ###############################################################################################

import pytest

from gamuLogger.targets import TerminalTarget, Target


class TestTerminalTarget:
    @pytest.mark.parametrize(
        "target, expected_str",
        [
            (TerminalTarget.STDOUT, "stdout"),
            (TerminalTarget.STDERR, "stderr"),
        ],
        ids=["stdout", "stderr"]
    )
    def test_str(self, target, expected_str):

        # Act
        result = str(target)

        # Assert
        assert result == expected_str

    @pytest.mark.parametrize(
        "target_str, expected_target",
        [
            ("stdout", TerminalTarget.STDOUT),
            ("stderr", TerminalTarget.STDERR),
            ("STDOUT", TerminalTarget.STDOUT),  # Case-insensitive
            ("STDERR", TerminalTarget.STDERR),  # Case-insensitive
            ("StDoUt", TerminalTarget.STDOUT),  # Case-insensitive
            ("StDeRr", TerminalTarget.STDERR),  # Case-insensitive
        ],
        ids=["stdout", "stderr", "stdout_uppercase", "stderr_uppercase", "stdout_mixedcase", "stderr_mixedcase"]
    )
    def test_from_string(self, target_str, expected_target):

        # Act
        target = TerminalTarget.from_string(target_str)

        # Assert
        assert target == expected_target

    @pytest.mark.parametrize(
        "target_str",
        [
            "invalid",  # Invalid target
            "",  # Empty string
        ],
        ids=["invalid", "empty"]
    )
    def test_from_string_invalid(self, target_str):

        # Act & Assert
        with pytest.raises(ValueError):
            TerminalTarget.from_string(target_str)


class TestTargetType:
    @pytest.mark.parametrize(
        "target_type, expected_str",
        [
            (Target.Type.FILE, "file"),
            (Target.Type.TERMINAL, "terminal"),
        ],
        ids=["file", "terminal"]
    )
    def test_str(self, target_type, expected_str):

        # Act
        result = str(target_type)

        # Assert
        assert result == expected_str


class TestTarget:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        Target.clear()
        yield

    @pytest.mark.parametrize(
        "target, name",
        [
            (lambda x: None, "test_target"),  # Function target with name
            (TerminalTarget.STDOUT, None),  # TerminalTarget with no name
            (TerminalTarget.STDERR, "stderr_target"),  # TerminalTarget with name
        ],
        ids=["function_with_name", "terminal_target_no_name", "terminal_target_with_name"]
    )
    def test_new(self, target, name):

        # Act
        Target(target, name)

        # Assert
        assert Target.exist(name or str(target))


    @pytest.mark.parametrize(
        "target, name",
        [
            ("invalid_target", "test_target"),  # Invalid target type
            (123, "test_target"),  # Invalid target type
        ],
        ids=["invalid_target_type_str", "invalid_target_type_int"]
    )
    def test_new_invalid_target(self, target, name):

        # Act & Assert
        with pytest.raises(ValueError):
            Target(target, name)

    def test_new_no_name(self):
        # Arrange
        def target_callable(_):
            return None

        # Act & Assert
        t = Target(target_callable)

        assert t.name == target_callable.__name__

    @pytest.mark.parametrize(
        "file",
        [
            ("test.log"),
        ],
        ids=["test_log_file"]
    )
    def test_from_file(self, file, tmp_path):
        # Arrange
        file_path = tmp_path / file

        # Act
        target = Target.from_file(str(file_path))

        # Assert
        assert Target.exist(str(file_path))
        assert target.type == Target.Type.FILE
        assert target.name == str(file_path)

    @pytest.mark.parametrize(
        "string",
        [
            ("test_string"),
        ],
        ids=["test_string"]
    )
    def test_call(self, string, tmp_path):
        # Arrange
        file_path = tmp_path / "test.log"
        target = Target.from_file(str(file_path))

        # Act
        target(string)

        # Assert
        with open(file_path, "r", encoding="utf-8") as f:
            assert f.read() == string

    @pytest.mark.parametrize(
        "target, name, expected_str",
        [
            (lambda x: None, "test_target", "test_target"),  # Function target
            (TerminalTarget.STDOUT, None, "stdout"),  # TerminalTarget
        ],
        ids=["function_target", "terminal_target"]
    )
    def test_str(self, target, name, expected_str):
        # Arrange
        target_instance = Target(target, name)

        # Act
        result = str(target_instance)

        # Assert
        assert result == expected_str

    @pytest.mark.parametrize(
        "target, name, expected_repr",
        [
            (lambda x: None, "test_target", "Target(test_target)"),  # Function target
            (TerminalTarget.STDOUT, None, "Target(stdout)"),  # TerminalTarget
        ],
        ids=["function_target", "terminal_target"]
    )
    def test_repr(self, target, name, expected_repr):
        # Arrange
        target_instance = Target(target, name)

        # Act
        result = repr(target_instance)

        # Assert
        assert result == expected_repr

    @pytest.mark.parametrize(
        "key, value",
        [
            ("test_key", "test_value"),
        ],
        ids=["test_key_value"]
    )
    def test_getitem_setitem_delitem_contains(self, key, value):
        # Arrange
        target = Target(lambda x: None, "test_target")

        # Act
        target[key] = value

        # Assert
        assert target[key] == value
        assert key in target
        del target[key]
        assert key not in target


    @pytest.mark.parametrize(
        "target, expected_type",
        [
            (lambda x: None, Target.Type.FILE),  # Function target
            (TerminalTarget.STDOUT, Target.Type.TERMINAL),  # TerminalTarget
        ],
        ids=["function_target", "terminal_target"]
    )
    def test_type(self, target, expected_type):
        # Arrange
        target_instance = Target(target, "test_target")

        # Act
        result = target_instance.type

        # Assert
        assert result == expected_type

    @pytest.mark.parametrize(
        "target, name, new_name",
        [
            (lambda x: None, "test_target", "new_test_target"),  # Function target
            (TerminalTarget.STDOUT, None, "new_stdout"),  # TerminalTarget
        ],
        ids=["function_target", "terminal_target"]
    )
    def test_name_setter(self, target, name, new_name):
        # Arrange
        target_instance = Target(target, name)

        # Act
        target_instance.name = new_name

        # Assert
        assert target_instance.name == new_name
        assert Target.exist(new_name)
        assert not Target.exist(name or str(target))


    def test_delete(self):
        # Arrange
        target = Target(lambda x: None, "test_target")

        # Act
        target.delete()

        # Assert
        assert not Target.exist("test_target")

    @pytest.mark.parametrize(
        "name",
        [
            ("test_target"),
        ],
        ids=["test_target"]
    )
    def test_get(self, name):
        # Arrange
        target = Target(lambda x: None, name)

        # Act
        retrieved_target = Target.get(name)

        # Assert
        assert retrieved_target is target

    @pytest.mark.parametrize(
        "name",
        [
            ("non_existent_target"),
        ],
        ids=["non_existent_target"]
    )
    def test_get_non_existent(self, name):

        # Act & Assert
        with pytest.raises(ValueError):
            Target.get(name)

    @pytest.mark.parametrize(
        "name, expected_result",
        [
            ("test_target", True),
            ("non_existent_target", False),
        ],
        ids=["existent_target", "non_existent_target"]
    )
    def test_exist(self, name, expected_result):
        # Arrange
        if expected_result:
            Target(lambda x: None, name)

        # Act
        result = Target.exist(name)

        # Assert
        assert result == expected_result

    def test_list(self):
        # Arrange
        target1 = Target(lambda x: None, "test_target1")
        target2 = Target(lambda x: None, "test_target2")

        # Act
        target_list = Target.list()

        # Assert
        assert target1 in target_list
        assert target2 in target_list

    def test_clear(self):
        # Arrange
        Target(lambda x: None, "test_target")

        # Act
        Target.clear()

        # Assert
        assert not Target.exist("test_target")


    @pytest.mark.parametrize(
        "target_name",
        [
            ("test_target"),
        ],
        ids=["test_target"]
    )
    def test_register_unregister(self, target_name):
        # Arrange
        target = Target(lambda x: None, target_name)

        # Act
        Target.unregister(target)

        # Assert
        assert not Target.exist(target_name)

        Target.register(target)
        assert Target.exist(target_name)

        Target.unregister(target_name)
        assert not Target.exist(target_name)


    def test_unregister_non_existent(self):
        # Arrange
        target_name = "non_existent_target"

        # Act & Assert
        with pytest.raises(ValueError):
            Target.unregister(target_name)
