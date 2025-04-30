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
import time
from unittest.mock import patch, mock_open
import pytest

from gamuLogger.targets import WriteToFile, TerminalTarget, Target

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


class TestWriteToFile:
    @pytest.fixture
    def setup_folder(self, tmp_path):
        folder = tmp_path / "logs"
        schema = "${hour}-${minute}-${second}.log"
        switch_condition = ("age > 1 hour",)
        delete_condition = ("nb_files >= 5",)
        return folder, schema, switch_condition, delete_condition

    def test_init_creates_folder(self, setup_folder):
        folder, schema, switch_condition, delete_condition = setup_folder

        # Act
        WriteToFile(str(folder), schema, switch_condition, delete_condition)

        # Assert
        assert os.path.exists(folder)

    def test_invalid_switch_condition(self, setup_folder):
        folder, schema, _, delete_condition = setup_folder
        invalid_switch_condition = ("invalid_condition",)

        # Act & Assert
        with pytest.raises(ValueError):
            WriteToFile(str(folder), schema, invalid_switch_condition, delete_condition)

    def test_invalid_delete_condition(self, setup_folder):
        folder, schema, switch_condition, _ = setup_folder
        invalid_delete_condition = ("invalid_condition",)

        # Act & Assert
        with pytest.raises(ValueError):
            WriteToFile(str(folder), schema, switch_condition, invalid_delete_condition)

    @patch("gamuLogger.targets.time.localtime")
    def test_create_new_file(self, mock_localtime, setup_folder):
        folder, schema, switch_condition, delete_condition = setup_folder
        mock_localtime.return_value = time.struct_time(
            (2023, 1, 1, 12, 0, 0, 0, 0, 0)
        )  # Mocked time

        # Arrange
        writer = WriteToFile(str(folder), schema, switch_condition, delete_condition)

        # Act
        writer._WriteToFile__create_new_file()

        # Assert
        expected_file = os.path.join(
            str(folder), "12-00-00" + ".log"
        )
        assert writer.current_file == expected_file

    @patch("os.listdir")
    @patch("os.path.getctime")
    def test_get_log_files_by_age(self, mock_getctime, mock_listdir, setup_folder):
        folder, schema, switch_condition, delete_condition = setup_folder
        mock_listdir.return_value = ["12-00-00.log", "12-01-00.log", "app.log"]
        mock_getctime.side_effect = [100, 200]

        # Arrange
        writer = WriteToFile(str(folder), schema, switch_condition, delete_condition)

        # Act
        result = writer._WriteToFile__get_log_files_by_age()

        # Assert
        assert result == ["12-00-00.log", "12-01-00.log"]

    @patch("os.path.getctime")
    @patch("os.path.getsize")
    def test_is_outdated(self, mock_getsize, mock_getctime, setup_folder):
        folder, schema, switch_condition, delete_condition = setup_folder
        mock_getctime.return_value = time.time() - 3600  # File created 1 hour ago
        mock_getsize.return_value = 1024 * 1024  # File size is 1 MB

        # Arrange
        writer = WriteToFile(str(folder), schema, switch_condition, delete_condition)

        # Act
        result = writer._WriteToFile__is_outdated()

        # Assert
        assert result is True

    @patch("os.remove")
    @patch("os.listdir")
    @patch("os.path.getctime")
    @patch("time.time")
    def test_delete_excess_files(self, mock_time, mock_getctime, mock_listdir, mock_remove, setup_folder):
        folder, schema, switch_condition, delete_condition = setup_folder
        mock_listdir.return_value = [
            "12-00-00.log", "12-01-00.log", "12-02-00.log", "12-03-00.log", "12-04-00.log", "12-05-00.log"
        ]  # 6 files to trigger the delete condition
        mock_getctime.side_effect = [100, 200, 300, 400, 500, 600]
        mock_time.return_value = 700

        # Arrange
        writer = WriteToFile(str(folder), schema, switch_condition, delete_condition)

        # Act
        writer._WriteToFile__delete_excess_files()

        # Assert
        assert mock_remove.call_count == 2  # Ensure at least one file was deleted
        mock_remove.assert_any_call(os.path.join(str(folder), "12-00-00.log"))  # Oldest file should be deleted
        mock_remove.assert_any_call(os.path.join(str(folder), "12-01-00.log"))

    @patch("builtins.open", new_callable=mock_open)
    @patch("gamuLogger.targets.WriteToFile._WriteToFile__is_outdated", return_value=True)
    @patch("gamuLogger.targets.WriteToFile._WriteToFile__delete_excess_files")
    def test_call(self, mock_delete_excess_files, mock_is_outdated, mock_file, setup_folder):
        folder, schema, switch_condition, delete_condition = setup_folder

        # Arrange
        writer = WriteToFile(str(folder), schema, switch_condition, delete_condition)

        # Act
        writer("Test log entry\n")

        # Assert
        mock_file.assert_called_once_with(writer.current_file, "a", encoding="utf-8")
        mock_file().write.assert_called_once_with("Test log entry\n")
        mock_is_outdated.assert_called_once()
        mock_delete_excess_files.assert_called_once()


class TestFromFileSchema:
    @pytest.fixture
    def setup_folder(self, tmp_path):
        folder = tmp_path / "logs"
        schema = "${hour}-${minute}-${second}.log"
        switch_condition = ("age > 1 hour",)
        delete_condition = ("nb_files >= 5",)
        return folder, schema, switch_condition, delete_condition

    def test_from_file_schema_creates_target(self, setup_folder):
        folder, schema, switch_condition, delete_condition = setup_folder

        # Act
        target = Target.from_file_schema(
            str(folder), schema, switch_condition, delete_condition
        )

        # Assert
        assert isinstance(target, Target)
        assert target.name == str(folder)
        assert target.type == Target.Type.FILE

    def test_from_file_schema_creates_folder(self, setup_folder):
        folder, schema, switch_condition, delete_condition = setup_folder

        # Act
        Target.from_file_schema(
            str(folder), schema, switch_condition, delete_condition
        )

        # Assert
        assert os.path.exists(folder)

    def test_from_file_schema_invalid_switch_condition(self, setup_folder):
        folder, schema, _, delete_condition = setup_folder
        invalid_switch_condition = ("invalid_condition",)

        # Act & Assert
        with pytest.raises(ValueError):
            Target.from_file_schema(
                str(folder), schema, invalid_switch_condition, delete_condition
            )

    def test_from_file_schema_invalid_delete_condition(self, setup_folder):
        folder, schema, switch_condition, _ = setup_folder
        invalid_delete_condition = ("invalid_condition",)

        # Act & Assert
        with pytest.raises(ValueError):
            Target.from_file_schema(
                str(folder), schema, switch_condition, invalid_delete_condition
            )

    @patch("gamuLogger.targets.time.localtime")
    def test_from_file_schema_creates_correct_file(self, mock_localtime, setup_folder):
        folder, schema, switch_condition, delete_condition = setup_folder
        mock_localtime.return_value = time.struct_time(
            (2023, 1, 1, 12, 0, 0, 0, 0, 0)
        )  # Mocked time

        # Act
        target = Target.from_file_schema(
            str(folder), schema, switch_condition, delete_condition
        )
        target("Test log entry\n")

        # Assert
        expected_file = os.path.join(str(folder), "12-00-00.log")
        assert os.path.exists(expected_file)
        with open(expected_file, "r", encoding="utf-8") as f:
            assert f.read() == "Test log entry\n"
