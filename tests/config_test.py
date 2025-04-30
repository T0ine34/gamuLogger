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

from gamuLogger.config import Config


class TestConfig:
    @pytest.mark.parametrize(
        "default",
        [
            ({"a": 1, "b": "test"}),  # Dictionary with multiple entries
            ({}),  # Empty dictionary
            ({"nested": {"a": 1, "b": 2}}), # Nested dictionary
        ],
        ids=["multiple_entries", "empty_dictionary", "nested_dictionary"]
    )
    def test_init(self, default):

        # Act
        config = Config(**default)

        # Assert
        assert config._Config__default == default
        assert config._Config__conf == default


    @pytest.mark.parametrize(
        "default, expected_repr",
        [
            ({"a": 1, "b": "test"}, "Config({'a': 1, 'b': 'test'})"),  # Dictionary with multiple entries
            ({}, "Config({})"),  # Empty dictionary
            ({"nested": {"a": 1, "b": 2}}, "Config({'nested': {'a': 1, 'b': 2}})"), # Nested dictionary
        ],
        ids=["multiple_entries", "empty_dictionary", "nested_dictionary"]
    )
    def test_repr(self, default, expected_repr):
        # Arrange
        config = Config(**default)

        # Act
        representation = repr(config)

        # Assert
        assert representation == expected_repr

    @pytest.mark.parametrize(
        "default, expected_str",
        [
            ({"a": 1, "b": "test"}, "Config({'a': 1, 'b': 'test'})"),  # Dictionary with multiple entries
            ({}, "Config({})"),  # Empty dictionary
            ({"nested": {"a": 1, "b": 2}}, "Config({'nested': {'a': 1, 'b': 2}})"), # Nested dictionary
        ],
        ids=["multiple_entries", "empty_dictionary", "nested_dictionary"]
    )
    def test_str(self, default, expected_str):
        # Arrange
        config = Config(**default)

        # Act
        string_representation = str(config)

        # Assert
        assert string_representation == expected_str


    @pytest.mark.parametrize(
        "default, name, expected_contains",
        [
            ({"a": 1, "b": "test"}, "a", True),  # Existing key
            ({"a": 1, "b": "test"}, "c", False),  # Non-existent key
            ({}, "a", False),  # Empty dictionary
        ],
        ids=["existing_key", "non_existent_key", "empty_dictionary"]
    )
    def test_contains(self, default, name, expected_contains):
        # Arrange
        config = Config(**default)

        # Act
        contains = name in config

        # Assert
        assert contains == expected_contains

    @pytest.mark.parametrize(
        "default, name, expected_value",
        [
            ({"a": 1, "b": "test"}, "a", 1),  # Existing key
            ({"nested": {"a": 1, "b": 2}}, "nested", {"a": 1, "b": 2}), # Nested dictionary access
        ],
        ids=["existing_key", "nested_dictionary"]
    )
    def test_getitem(self, default, name, expected_value):
        # Arrange
        config = Config(**default)

        # Act
        value = config[name]

        # Assert
        assert value == expected_value

    @pytest.mark.parametrize(
        "default, name",
        [
            ({"a": 1, "b": "test"}, "c"),  # Non-existent key
            ({}, "a"),  # Empty dictionary
        ],
        ids=["non_existent_key", "empty_dictionary"]
    )
    def test_getitem_key_error(self, default, name):
        # Arrange
        config = Config(**default)

        # Act & Assert
        with pytest.raises(KeyError):
            config[name]

    @pytest.mark.parametrize(
        "default, name, value",
        [
            ({"a": 1, "b": "test"}, "a", 2),  # Existing key
            ({"a": 1, "b": "test"}, "b", "new_value"), # Existing key, different type
            ({"nested": {"a": 1, "b": 2}}, "nested", {"a": 3, "c": 4}), # Nested dictionary modification
        ],
        ids=["existing_key_int", "existing_key_str", "nested_dictionary"]
    )
    def test_setitem(self, default, name, value):
        # Arrange
        config = Config(**default)

        # Act
        config[name] = value

        # Assert
        assert config[name] == value

    @pytest.mark.parametrize(
        "default, name, value",
        [
            ({"a": 1, "b": "test"}, "c", 2),  # Non-existent key
            ({}, "a", 1),  # Empty dictionary
        ],
        ids=["non_existent_key", "empty_dictionary"]
    )
    def test_setitem_key_error(self, default, name, value):
        # Arrange
        config = Config(**default)

        # Act & Assert
        with pytest.raises(KeyError):
            config[name] = value


    @pytest.mark.parametrize(
        "default",
        [
            ({"a": 1, "b": "test"}),  # Dictionary with multiple entries
            ({"nested": {"a": 1, "b": 2}}), # Nested dictionary
        ],
        ids=["multiple_entries", "nested_dictionary"]
    )
    def test_clear(self, default):
        # Arrange
        config = Config(**default)
        # Modify the config
        try:
            config["a"] = 2
        except KeyError:
            pass

        # Act
        config.clear()

        # Assert
        assert config._Config__conf == default
