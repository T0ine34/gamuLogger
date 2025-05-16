import pytest
from gamuLogger.condition import AgeCondition, SizeCondition, NbFilesCondition, condition_factory
from gamuLogger.utils import string2seconds
from unittest.mock import Mock

class TestAgeCondition:
    @pytest.mark.parametrize(
        "operator, value, unit, age, expected",
        [
            (">", 10, "seconds", 15, True),
            (">", 10, "seconds", 5, False),
            (">=", 10, "seconds", 10, True),
            (">=", 10, "seconds", 5, False),
            ("<", 10, "seconds", 5, True),
            ("<", 10, "seconds", 15, False),
            ("<=", 10, "seconds", 10, True),
            ("<=", 10, "seconds", 15, False),
            ("==", 10, "seconds", 10, True),
            ("==", 10, "seconds", 15, False),
        ],
        ids=[
            "greater_true", "greater_",
            "greater_equal_true", "greater_equal_",
            "less_true", "less_",
            "less_equal_true", "less_equal_",
            "equal_true", "equal_"
        ]
    )
    def test_call(self, operator, value, unit, age, expected):
        condition = AgeCondition(operator, value, unit)
        assert condition(age) == expected

    @pytest.mark.parametrize(
        "operator, value, unit",
        [
            ("invalid", 10, "seconds"),
        ],
        ids=["invalid_operator"]
    )
    def test_invalid_operator(self, operator, value, unit):
        with pytest.raises(ValueError, match=f"Invalid operator: {operator}"):
            AgeCondition(operator, value, unit)

    @pytest.mark.parametrize(
        "string, expected_operator, expected_value, expected_unit",
        [
            ("> 10 seconds", ">", 10, "seconds"),
            ("<= 5 minutes", "<=", 5, "minutes"),
        ],
        ids=["valid_greater", "valid_less_equal"]
    )
    def test_from_string_valid(self, string, expected_operator, expected_value, expected_unit, monkeypatch):
        mock_match = Mock()
        mock_match.group.side_effect = lambda x: {
            "operator": expected_operator,
            "value": str(expected_value),
            "unit": expected_unit
        }[x]
        monkeypatch.setattr("re.match", lambda pattern, string: mock_match)
        condition = AgeCondition.from_string(string)
        assert condition._AgeCondition__operator == expected_operator
        assert condition._AgeCondition__age_in_seconds == string2seconds(f"{expected_value} {expected_unit}")

    @pytest.mark.parametrize(
        "string",
        [
            "invalid string",
        ],
        ids=["invalid_format"]
    )
    def test_from_string_invalid(self, string):
        with pytest.raises(ValueError, match=f"Invalid age condition: {string}"):
            AgeCondition.from_string(string)

    @pytest.mark.parametrize(
        "operator, value, unit",
        [
            (">", 10, "seconds"),
            ("<=", 5, "minutes"),
        ],
        ids=["valid_greater", "valid_less_equal"]
    )
    def test_from_match(self, operator, value, unit):
        mock_match = Mock()
        mock_match.group.side_effect = lambda x: {
            "operator": operator,
            "value": str(value),
            "unit": unit
        }[x]
        condition = AgeCondition.from_match(mock_match)
        assert condition._AgeCondition__operator == operator
        assert condition._AgeCondition__age_in_seconds == string2seconds(f"{value} {unit}")

    def test_str(self):
        condition = AgeCondition(">", 10, "seconds")
        assert str(condition) == "> 10 seconds"
    
    def test_repr(self):
        condition = AgeCondition(">", 10, "seconds")
        assert repr(condition) == "AgeCondition(operator='>', value='10', unit='seconds')"

class TestSizeCondition:
    @pytest.mark.parametrize(
        "value, unit, size", # size is in bytes
        [
            (10, "B",  15),
            (10, "KB", 15 * 1024),
            (10, "MB", 15 * 1024**2),
            (10, "GB", 15 * 1024**3),
            (10, "TB", 15 * 1024**4),
            (10, "PB", 15 * 1024**5)
        ],
        ids=[
            "greater_B", "greater_KB",
            "greater_MB", "greater_GB",
            "greater_TB", "greater_PB",
        ]
    )
    def test_greater_equal(self, value, unit, size):
        condition = SizeCondition(">=", value, unit)
        assert condition(size)

    @pytest.mark.parametrize(
        "value, unit, size", # size is in bytes
        [
            (10, "B",  5),
            (10, "KB", 5 * 1024),
            (10, "MB", 5 * 1024**2),
            (10, "GB", 5 * 1024**3),
            (10, "TB", 5 * 1024**4),
            (10, "PB", 5 * 1024**5)
        ],
        ids=[
            "less__B", "less__KB",
            "less__MB", "less__GB",
            "less__TB", "less__PB",
        ]
    )
    def test_less_equal(self, value, unit, size):
        condition = SizeCondition("<=", value, unit)
        assert condition(size)
        
    @pytest.mark.parametrize(
        "value, unit, size", # size is in bytes
        [
            (10, "B",  15),
            (10, "KB", 15 * 1024),
            (10, "MB", 15 * 1024**2),
            (10, "GB", 15 * 1024**3),
            (10, "TB", 15 * 1024**4),
            (10, "PB", 15 * 1024**5)
        ],
        ids=[
            "greater_B", "greater_KB",
            "greater_MB", "greater_GB",
            "greater_TB", "greater_PB",
        ]
    )
    def test_greater(self, value, unit, size):
        condition = SizeCondition(">", value, unit)
        assert condition(size)
    
    @pytest.mark.parametrize(
        "value, unit, size", # size is in bytes
        [
            (10, "B",  5),
            (10, "KB", 5 * 1024),
            (10, "MB", 5 * 1024**2),
            (10, "GB", 5 * 1024**3),
            (10, "TB", 5 * 1024**4),
            (10, "PB", 5 * 1024**5)
        ],
        ids=[
            "less__B", "less__KB",
            "less__MB", "less__GB",
            "less__TB", "less__PB",
        ]
    )
    def test_less(self, value, unit, size):
        condition = SizeCondition("<", value, unit)
        assert condition(size)
    
    @pytest.mark.parametrize(
        "value, unit, size", # size is in bytes
        [
            (10, "B",  10),
            (10, "KB", 10 * 1024),
            (10, "MB", 10 * 1024**2),
            (10, "GB", 10 * 1024**3),
            (10, "TB", 10 * 1024**4),
            (10, "PB", 10 * 1024**5)
        ],
        ids=[
            "equal_B", "equal_KB",
            "equal_MB", "equal_GB",
            "equal_TB", "equal_PB",
        ]
    )
    def test_equal(self, value, unit, size):
        condition = SizeCondition("==", value, unit)
        assert condition(size)
    
    @pytest.mark.parametrize(
        "value, unit, size", # size is in bytes
        [
            (10, "B",  15),
            (10, "KB", 15 * 1024),
            (10, "MB", 15 * 1024**2),
            (10, "GB", 15 * 1024**3),
            (10, "TB", 15 * 1024**4),
            (10, "PB", 15 * 1024**5)
        ],
        ids=[
            "not_equal_B", "not_equal_KB",
            "not_equal_MB", "not_equal_GB",
            "not_equal_TB", "not_equal_PB",
        ]
    )
    def test_not_equal(self, value, unit, size):
        condition = SizeCondition("!=", value, unit)
        assert condition(size)
    
    @pytest.mark.parametrize(
        "operator, value, unit",
        [
            ("invalid", 10, "bytes"),
        ],
        ids=["invalid_operator"]
    )
    def test_invalid_operator(self, operator, value, unit):
        with pytest.raises(ValueError, match=f"Invalid operator: {operator}"):
            SizeCondition(operator, value, unit)
    
    @pytest.mark.parametrize(
        "string, expected_operator, expected_value, expected_unit",
        [
            ("> 10 B", ">", 10, "B"),
            ("<= 5 KB", "<=", 5, "KB"),
        ],
        ids=["valid_greater", "valid_less_equal"]
    )
    def test_from_string_valid(self, string, expected_operator, expected_value, expected_unit, monkeypatch):
        mock_match = Mock()
        mock_match.group.side_effect = lambda x: {
            "operator": expected_operator,
            "value": str(expected_value),
            "unit": expected_unit
        }[x]
        monkeypatch.setattr("re.match", lambda pattern, string: mock_match)
        condition = SizeCondition.from_string(string)
        assert condition._SizeCondition__operator == expected_operator
        assert condition._SizeCondition__size_in_bytes == 10 if expected_unit == "B" else 5 * 1024
    
    @pytest.mark.parametrize(
        "string",
        [
            "invalid string",
        ],
        ids=["invalid_format"]
    )
    def test_from_string_invalid(self, string):
        with pytest.raises(ValueError, match=f"Invalid size condition: {string}"):
            SizeCondition.from_string(string)

    def test_str(self):
        condition = SizeCondition(">", 10, "B")
        assert str(condition) == "> 10 bytes"
    
    def test_repr(self):
        condition = SizeCondition(">", 10, "B")
        assert repr(condition) == "SizeCondition(operator='>', value='10', unit='bytes')"

class TestNbFilesCondition:
    @pytest.mark.parametrize(
        "operator, value, nb_files, expected",
        [
            (">", 10, 15, True),
            (">", 10, 5, False),
            (">=", 10, 10, True),
            (">=", 10, 5, False),
            ("==", 10, 10, True),
            ("==", 10, 15, False),
        ],
        ids=[
            "greater_true", "greater_",
            "greater_equal_true", "greater_equal_",
            "equal_true", "equal_"
        ]
    )
    def test_call(self, operator, value, nb_files, expected):
        condition = NbFilesCondition(operator, value)
        assert condition(nb_files) == expected

    @pytest.mark.parametrize(
        "operator, value",
        [
            ("invalid", 10),
        ],
        ids=["invalid_operator"]
    )
    def test_invalid_operator(self, operator, value):
        with pytest.raises(ValueError, match=f"Invalid operator: {operator}"):
            NbFilesCondition(operator, value)

    @pytest.mark.parametrize(
        "string, expected_operator, expected_value",
        [
            ("> 10", ">", 10),
            (">= 5", ">=", 5),
        ],
        ids=["valid_greater", "valid_less_equal"]
    )
    def test_from_string_valid(self, string, expected_operator, expected_value):
        condition = NbFilesCondition.from_string(string)
        assert condition._NbFilesCondition__operator == expected_operator
        assert condition._NbFilesCondition__nb_files == expected_value

    @pytest.mark.parametrize(
        "string",
        [
            "invalid string",
        ],
        ids=["invalid_format"]
    )
    def test_from_string_invalid(self, string):
        with pytest.raises(ValueError):
            NbFilesCondition.from_string(string)

    @pytest.mark.parametrize(
        "operator, value",
        [
            (">", 10),
            (">=", 5),
        ],
        ids=["valid_greater", "valid_less_equal"]
    )
    def test_from_match(self, operator, value):
        mock_match = Mock()
        mock_match.group.side_effect = lambda x: {
            "operator": operator,
            "value": str(value),
        }[x]
        condition = NbFilesCondition.from_match(mock_match)
        assert condition._NbFilesCondition__operator == operator
        assert condition._NbFilesCondition__nb_files == value


class TestConditionFactory:
    @pytest.mark.parametrize(
        "string, expected_type",
        [
            ("> 10 seconds", AgeCondition),
            ("< 5 KB", SizeCondition),
            ("> 10", NbFilesCondition),
        ],
        ids=[
            "valid_age_condition",
            "valid_size_condition",
            "valid_nb_files_condition",
        ]
    )
    def test_valid_conditions_no_prefix(self, string, expected_type):
        condition = condition_factory(string)
        assert isinstance(condition, expected_type)
 
    @pytest.mark.parametrize(
        "string, expected_type",
        [
            ("age > 10 seconds", AgeCondition),
            ("size < 5 KB", SizeCondition),
            ("nb_files > 10", NbFilesCondition),
        ],
        ids=[
            "valid_age_condition",
            "valid_size_condition",
            "valid_nb_files_condition",
        ]
    )
    def test_valid_conditions(self, string, expected_type):
        condition = condition_factory(string)
        assert isinstance(condition, expected_type)

    @pytest.mark.parametrize(
        "string",
        [
            "invalid string",
            "age > 10 invalid_unit",
            "size < 5 invalid_unit",
            "nb_files > invalid_value",
        ],
        ids=[
            "invalid_format",
            "invalid_age_unit",
            "invalid_size_unit",
            "invalid_nb_files_value",
        ]
    )
    def test_invalid_conditions(self, string):
        with pytest.raises(ValueError):
            condition_factory(string)

    def test_str(self):
        condition = NbFilesCondition(">", 10)
        assert str(condition) == "> 10 files"
    
    def test_repr(self):
        condition = NbFilesCondition(">", 10)
        assert repr(condition) == "NbFilesCondition(operator='>', value='10', unit='files')"