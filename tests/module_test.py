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

from gamuLogger.module import Module

class TestModule:
    @pytest.mark.parametrize(
        "name, parent, file, function, expected_complete_name",
        [
            ("module1", None, "file1.py", "func1", "module1"),  # simple module
            ("module2", Module("module1"), "file2.py", "func2", "module1.module2"),  # nested module
        ],
        ids=["simple_module", "nested_module"]
    )
    def test_get_complete_name(self, name, parent, file, function, expected_complete_name):
        # Arrange
        module = Module(name, parent, file, function)

        # Act
        complete_name = module.get_complete_name()

        # Assert
        assert complete_name == expected_complete_name

    @pytest.mark.parametrize(
        "name, parent, file, function, expected_complete_path",
        [
            ("module1", None, "file1.py", "func1", ["module1"]),  # simple module
            ("module2", Module("module1"), "file2.py", "func2", ["module1", "module2"]),  # nested module
        ],
        ids=["simple_module", "nested_module"]
    )
    def test_get_complete_path(self, name, parent, file, function, expected_complete_path):
        # Arrange
        module = Module(name, parent, file, function)

        # Act
        complete_path = module.get_complete_path()

        # Assert
        assert complete_path == expected_complete_path

    @pytest.mark.parametrize(
        "filename, function, expected_module_name",
        [
            ("file1.py", "a.b.c.d", "a.b.c.d"),  # exact match
            ("file1.py", "a.b.c", "a.b.c"),  # partial match
            ("file1.py", "a.b", "a.b"),  # partial match
            ("file1.py", "a", "a"),  # partial match
        ],
        ids=["exact_match", "partial_match_1", "partial_match_2", "partial_match_3"]
    )
    def test_get(self, filename, function, expected_module_name):

        # Arrange
        Module.clear()
        Module("a", file=filename, function="a")
        Module("b", parent=Module.get(filename, "a"), file=filename, function="a.b")
        Module("c", parent=Module.get(filename, "a.b"), file=filename, function="a.b.c")
        Module("d", parent=Module.get(filename, "a.b.c"), file=filename, function="a.b.c.d")


        # Act
        module = Module.get(filename, function)

        # Assert
        assert module.get_complete_name() == expected_module_name


    @pytest.mark.parametrize(
        "filename, function",
        [
            ("file1.py", "non_existent"),  # non-existent module
        ],
        ids=["non_existent_module"]
    )
    def test_get_not_found(self, filename, function):
        # Arrange
        Module.clear()

        # Act & Assert
        with pytest.raises(ValueError):
            Module.get(filename, function)

    @pytest.mark.parametrize(
        "filename, function, expected_result",
        [
            ("file1.py", "a.b.c.d", True),  # exact match
            ("file1.py", "a.b.c", True),  # partial match
            ("file1.py", "a.b", True),  # partial match
            ("file1.py", "a", True),  # partial match
            ("file1.py", "x.y.z", True),  # fallback to <module>
            ("file2.py", "a.b.c.d", False),  # non-existent module
        ],
        ids=["exact_match", "partial_match_1", "partial_match_2", "partial_match_3", "fallback_to_module", "non_existent_module"]
    )
    def test_exist(self, filename, function, expected_result):
        # Arrange
        Module.clear()
        Module("a", file="file1.py", function="a")
        Module("b", parent=Module.get("file1.py", "a"), file="file1.py", function="a.b")
        Module("c", parent=Module.get("file1.py", "a.b"), file="file1.py", function="a.b.c")
        Module("d", parent=Module.get("file1.py", "a.b.c"), file="file1.py", function="a.b.c.d")
        Module("top_level", file="file1.py", function="<module>")

        # Act
        result = Module.exist(filename, function)

        # Assert
        assert result == expected_result

    @pytest.mark.parametrize(
        "filename, function",
        [
            ("file1.py", "a.b.c.d"),  # existing module
        ],
        ids=["existing_module"]
    )
    def test_delete(self, filename, function):
        # Arrange
        Module.clear()
        Module("a", file=filename, function="a")
        Module("b", parent=Module.get(filename, "a"), file=filename, function="a.b")
        Module("c", parent=Module.get(filename, "a.b"), file=filename, function="a.b.c")
        Module("d", parent=Module.get(filename, "a.b.c"), file=filename, function="a.b.c.d")

        # Act
        Module.delete(filename, function)

        # Assert
        assert not Module.exist_exact(filename, function)

    @pytest.mark.parametrize(
        "filename, function",
        [
            ("file1.py", "non_existent"),  # non-existent module
        ],
        ids=["non_existent_module"]
    )
    def test_delete_not_found(self, filename, function):
        # Arrange
        Module.clear()

        # Act & Assert
        with pytest.raises(ValueError):
            Module.delete(filename, function)


    @pytest.mark.parametrize(
        "name",
        [
            ("a.b.c.d"),  # existing module by name
        ],
        ids=["existing_module"]
    )
    def test_get_by_name(self, name):
        # Arrange
        Module.clear()
        Module("a", file="file1.py", function="a")
        Module("b", parent=Module.get("file1.py", "a"), file="file1.py", function="a.b")
        Module("c", parent=Module.get("file1.py", "a.b"), file="file1.py", function="a.b.c")
        Module("d", parent=Module.get("file1.py", "a.b.c"), file="file1.py", function="a.b.c.d")

        # Act
        module = Module.get_by_name(name)

        # Assert
        assert module.get_complete_name() == name

    @pytest.mark.parametrize(
        "name",
        [
            ("non_existent"),  # non-existent module by name
        ],
        ids=["non_existent_module"]
    )
    def test_get_by_name_not_found(self, name):
        # Arrange
        Module.clear()

        # Act & Assert
        with pytest.raises(ValueError):
            Module.get_by_name(name)


    @pytest.mark.parametrize(
        "name, expected_result",
        [
            ("a.b.c.d", True),  # existing module by name
            ("non_existent", False),  # non-existent module by name
        ],
        ids=["existing_module", "non_existent_module"]
    )
    def test_exist_by_name(self, name, expected_result):
        # Arrange
        Module.clear()
        Module("a", file="file1.py", function="a")
        Module("b", parent=Module.get("file1.py", "a"), file="file1.py", function="a.b")
        Module("c", parent=Module.get("file1.py", "a.b"), file="file1.py", function="a.b.c")
        Module("d", parent=Module.get("file1.py", "a.b.c"), file="file1.py", function="a.b.c.d")

        # Act
        result = Module.exist_by_name(name)

        # Assert
        assert result == expected_result


    @pytest.mark.parametrize(
        "name",
        [
            ("a.b.c.d"),  # existing module by name
        ],
        ids=["existing_module"]
    )
    def test_delete_by_name(self, name):
        # Arrange
        Module.clear()
        Module("a", file="file1.py", function="a")
        Module("b", parent=Module.get("file1.py", "a"), file="file1.py", function="a.b")
        Module("c", parent=Module.get("file1.py", "a.b"), file="file1.py", function="a.b.c")
        Module("d", parent=Module.get("file1.py", "a.b.c"), file="file1.py", function="a.b.c.d")

        # Act
        Module.delete_by_name(name)

        # Assert
        assert not Module.exist_by_name(name)

    @pytest.mark.parametrize(
        "name",
        [
            ("non_existent"),  # non-existent module by name
        ],
        ids=["non_existent_module"]
    )
    def test_delete_by_name_not_found(self, name):
        # Arrange
        Module.clear()

        # Act & Assert
        with pytest.raises(ValueError):
            Module.delete_by_name(name)

    def test_clear(self):
        # Arrange
        Module("module1", file="file1.py", function="func1")

        # Act
        Module.clear()

        # Assert
        assert not Module.exist("file1.py", "func1")

    @pytest.mark.parametrize(
        "name, file, function",
        [
            ("module1", "file1.py", "func1"),  # simple module
            ("a.b.c.d", "file2.py", "func2"),  # nested module
        ],
        ids=["simple_module", "nested_module"]
    )
    def test_new(self, name, file, function):
        # Arrange
        Module.clear()

        # Act
        module = Module.new(name, file, function)

        # Assert
        assert Module.exist(file, function)
        assert module.get_complete_name() == name

    @pytest.mark.parametrize(
        "name, file, function",
        [
            ("module1", "file1.py", "func1"),  # existing module
        ],
        ids=["existing_module"]
    )
    def test_new_already_exists(self, name, file, function):
        # Arrange
        Module.clear()
        module1 = Module.new(name, file, function)

        module2 = Module.new(name, file, function)

        # Act & Assert
        assert module1 is module2  # should return the same instance

    def test_all(self):
        # Arrange
        Module.clear()
        Module("module1", file="file1.py", function="func1")

        # Act
        all_modules = Module.all()

        # Assert
        assert ("file1.py", "func1") in all_modules
