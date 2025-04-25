import pytest

from gamuLogger.custom_types import (COLORS, Levels, LoggerConfig, Module,
                                     Target, TerminalTarget)


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


class TestCOLORS:
    @pytest.mark.parametrize(
        "color, expected_str",
        [
            (COLORS.RED, '\033[91m'),
            (COLORS.DARK_RED, '\033[91m\033[1m'),
            (COLORS.GREEN, '\033[92m'),
            (COLORS.YELLOW, '\033[93m'),
            (COLORS.BLUE, '\033[94m'),
            (COLORS.MAGENTA, '\033[95m'),
            (COLORS.CYAN, '\033[96m'),
            (COLORS.RESET, '\033[0m'),
            (COLORS.NONE, ''),
        ],
        ids=["red", "dark_red", "green", "yellow", "blue", "magenta", "cyan", "reset", "none"]
    )
    def test_str(self, color, expected_str):
        # Act
        result = str(color)

        # Assert
        assert result == expected_str


    @pytest.mark.parametrize(
        "color, other, expected_result",
        [
            (COLORS.RED, "test", "\033[91mtest"),  # color + string
            ("test", COLORS.RED, "test\033[91m"),  # string + color
            (COLORS.RED, 123, "\033[91m123"),  # color + int
            (123, COLORS.RED, "123\033[91m"),  # int + color

        ],
        ids=["color_plus_string", "string_plus_color", "color_plus_int", "int_plus_color"]
    )
    def test_add_radd(self, color, other, expected_result):

        # Act
        result = color + other

        # Assert
        assert result == expected_result

    @pytest.mark.parametrize(
        "color, expected_repr",
        [
            (COLORS.RED, '\033[91m'),
            (COLORS.DARK_RED, '\033[91m\033[1m'),
            (COLORS.GREEN, '\033[92m'),
            (COLORS.YELLOW, '\033[93m'),
            (COLORS.BLUE, '\033[94m'),
            (COLORS.MAGENTA, '\033[95m'),
            (COLORS.CYAN, '\033[96m'),
            (COLORS.RESET, '\033[0m'),
            (COLORS.NONE, ''),
        ],
        ids=["red", "dark_red", "green", "yellow", "blue", "magenta", "cyan", "reset", "none"]
    )
    def test_repr(self, color, expected_repr):

        # Act
        result = repr(color)

        # Assert
        assert result == expected_repr



class TestLevels:
    @pytest.mark.parametrize(
        "level_str, expected_level",
        [
            ("trace", Levels.TRACE),
            ("debug", Levels.DEBUG),
            ("info", Levels.INFO),
            ("warning", Levels.WARNING),
            ("error", Levels.ERROR),
            ("critical", Levels.CRITICAL),
            ("TRACE", Levels.TRACE),  # Case-insensitive
            ("DeBuG", Levels.DEBUG),  # Case-insensitive
            ("iNfO", Levels.INFO),  # Case-insensitive
            ("WARNING", Levels.WARNING), # Case-insensitive
            ("ErRoR", Levels.ERROR),  # Case-insensitive
            ("CRITICAL", Levels.CRITICAL), # Case-insensitive
            ("invalid", Levels.INFO),  # Invalid level
            ("", Levels.INFO),  # Empty string
        ],
        ids=["trace", "debug", "info", "warning", "error", "critical", "trace_uppercase", "debug_mixedcase", "info_mixedcase", "warning_uppercase", "error_mixedcase", "critical_uppercase", "invalid", "empty"]
    )
    def test_from_string(self, level_str, expected_level):

        # Act
        level = Levels.from_string(level_str)

        # Assert
        assert level == expected_level

    @pytest.mark.parametrize(
        "level, expected_str",
        [
            (Levels.TRACE, '  TRACE   '),
            (Levels.DEBUG, '  DEBUG   '),
            (Levels.INFO, '   INFO   '),
            (Levels.WARNING, ' WARNING  '),
            (Levels.ERROR, '  ERROR   '),
            (Levels.CRITICAL, ' CRITICAL '),
        ],
        ids=["trace", "debug", "info", "warning", "error", "critical"]
    )
    def test_str(self, level, expected_str):

        # Act
        result = str(level)

        # Assert
        assert result == expected_str

    @pytest.mark.parametrize(
        "level, expected_int",
        [
            (Levels.TRACE, 0),
            (Levels.DEBUG, 1),
            (Levels.INFO, 2),
            (Levels.WARNING, 3),
            (Levels.ERROR, 4),
            (Levels.CRITICAL, 5),
        ],
        ids=["trace", "debug", "info", "warning", "error", "critical"]
    )
    def test_int(self, level, expected_int):

        # Act
        result = int(level)

        # Assert
        assert result == expected_int


    @pytest.mark.parametrize(
        "level1, level2, expected_le",
        [
            (Levels.TRACE, Levels.DEBUG, True),
            (Levels.DEBUG, Levels.TRACE, False),
            (Levels.INFO, Levels.INFO, True),
        ],
        ids=["trace_le_debug", "debug_le_trace", "info_le_info"]
    )
    def test_le(self, level1, level2, expected_le):

        # Act
        result = level1 <= level2

        # Assert
        assert result == expected_le

    @pytest.mark.parametrize(
        "level, expected_color",
        [
            (Levels.TRACE, COLORS.CYAN),
            (Levels.DEBUG, COLORS.BLUE),
            (Levels.INFO, COLORS.GREEN),
            (Levels.WARNING, COLORS.YELLOW),
            (Levels.ERROR, COLORS.RED),
            (Levels.CRITICAL, COLORS.DARK_RED),
        ],
        ids=["trace", "debug", "info", "warning", "error", "critical"]
    )
    def test_color(self, level, expected_color):

        # Act
        color = level.color()

        # Assert
        assert color == expected_color


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
        target_instance = Target(target, name)

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
        def target_callable(x):
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


class TestLoggerConfig:
    def test_init(self):
        # Act
        config = LoggerConfig()

        # Assert
        assert config.show_threads_name is False
        assert config.show_process_name is False

    def test_clear(self):
        # Arrange
        config = LoggerConfig()
        config.show_threads_name = True
        config.show_process_name = True

        # Act
        config.clear()

        # Assert
        assert not config.show_threads_name
        assert not config.show_process_name

    @pytest.mark.parametrize(
        "key, expected_value",
        [
            ("show_threads_name", False),
            ("show_process_name", False),
        ],
        ids=["show_threads_name", "show_process_name"]
    )
    def test_getitem(self, key, expected_value):
        # Arrange
        config = LoggerConfig()

        # Act
        value = config[key]

        # Assert
        assert value == expected_value

    @pytest.mark.parametrize(
        "key",
        [
            "invalid_key",
            "",
            None
        ],
        ids=["invalid_key", "empty_string", "none"]

    )
    def test_getitem_invalid_key(self, key):
        # Arrange
        config = LoggerConfig()

        # Act & Assert
        with pytest.raises(KeyError):
            config[key]

    @pytest.mark.parametrize(
        "key, value",
        [
            ("show_threads_name", True),
            ("show_process_name", True),
            ("show_threads_name", False),
            ("show_process_name", 123),
        ],
        ids=["show_threads_name_true", "show_process_name_true", "show_threads_name_false", "show_process_name_int"]
    )
    def test_setitem(self, key, value):
        # Arrange
        config = LoggerConfig()

        # Act
        config[key] = value

        # Assert
        assert config[key] == value


    @pytest.mark.parametrize(
        "key, value",
        [
            ("invalid_key", True),
            ("", 123),
            (None, False)
        ],
        ids=["invalid_key", "empty_string", "none"]

    )
    def test_setitem_invalid_key(self, key, value):
        # Arrange
        config = LoggerConfig()

        # Act & Assert
        with pytest.raises(KeyError):
            config[key] = value

    @pytest.mark.parametrize(
        "show_threads_name, show_process_name, expected_str",
        [
            (False, False, "LoggerConfig(show_threads_name=False, show_process_name=False)"),
            (True, False, "LoggerConfig(show_threads_name=True, show_process_name=False)"),
            (False, True, "LoggerConfig(show_threads_name=False, show_process_name=True)"),
            (True, True, "LoggerConfig(show_threads_name=True, show_process_name=True)"),
        ],
        ids=["false_false", "true_false", "false_true", "true_true"]
    )
    def test_str(self, show_threads_name, show_process_name, expected_str):
        # Arrange
        config = LoggerConfig()
        config.show_threads_name = show_threads_name
        config.show_process_name = show_process_name

        # Act
        result = str(config)

        # Assert
        assert result == expected_str
