import pytest
from gamuLogger.function import trace_func, debug_func
from gamuLogger import Logger, Levels


class TestTraceFunc:
    def test_without_chrono(self):
        logs = []
        def capture(message : str):
            logs.append(message)
        
        Logger.add_target(capture, Levels.TRACE)
        Logger.set_default_module_level(Levels.TRACE)
        
        @trace_func(use_chrono=False)
        def sample_function(a, b):
            return a + b


        result = sample_function(1, 2)
        assert result == 3

        assert len(logs) == 2
        assert "Calling sample_function with" in logs[0]
        assert "args: (1, 2)" in logs[0]
        assert "Function sample_function returned \"3\"" in logs[1]


    def test_with_chrono(self):
        logs = []
        def capture(message : str):
            logs.append(message)
        
        Logger.add_target(capture, Levels.TRACE)
        Logger.set_default_module_level(Levels.TRACE)
            
        @trace_func(use_chrono=True)
        def sample_function(a, b):
            return a + b

        result = sample_function(1, 2)
        assert result == 3

        assert len(logs) == 2
        assert "Calling sample_function with" in logs[0]
        assert "args: (1, 2)" in logs[0]
        assert "Function sample_function took" in logs[1]
        assert "and returned \"3\"" in logs[1]


    def test_with_kwargs(self):
        logs = []
        def capture(message : str):
            logs.append(message)
        
        Logger.add_target(capture, Levels.TRACE)
        Logger.set_default_module_level(Levels.TRACE)
        
        @trace_func(use_chrono=False)
        def sample_function(a, b, c=None):
            return f"{a}, {b}, {c}"

        result = sample_function(1, 2, c=3)
        assert result == "1, 2, 3"

        assert len(logs) == 2
        assert "Calling sample_function with" in logs[0]
        assert "args: (1, 2)" in logs[0]
        assert "kwargs: {'c': 3}" in logs[0]
        assert "Function sample_function returned \"1, 2, 3\"" in logs[1]


    def test_nested_calls(self):
        logs = []
        def capture(message : str):
            logs.append(message)
        
        Logger.add_target(capture, Levels.TRACE)
        Logger.set_default_module_level(Levels.TRACE)

        @trace_func(use_chrono=False)
        def inner_function(x):
            return x * 2

        @trace_func(use_chrono=False)
        def outer_function(y):
            return inner_function(y) + 1

        result = outer_function(3)
        assert result == 7

        assert len(logs) == 4
        assert "Calling outer_function with" in logs[0]
        assert "Calling inner_function with" in logs[1]
        assert "Function inner_function returned \"6\"" in logs[2]
        assert "Function outer_function returned \"7\"" in logs[3]


class TestDebugFunc:
    def test_without_chrono(self):
        logs = []
        def capture(message : str):
            logs.append(message)
        
        Logger.add_target(capture, Levels.TRACE)
        Logger.set_default_module_level(Levels.TRACE)
        
        @debug_func(use_chrono=False)
        def sample_function(a, b):
            return a + b


        result = sample_function(1, 2)
        assert result == 3

        assert len(logs) == 2
        assert "Calling sample_function with" in logs[0]
        assert "args: (1, 2)" in logs[0]
        assert "Function sample_function returned \"3\"" in logs[1]


    def test_with_chrono(self):
        logs = []
        def capture(message : str):
            logs.append(message)
        
        Logger.add_target(capture, Levels.TRACE)
        Logger.set_default_module_level(Levels.TRACE)
            
        @debug_func(use_chrono=True)
        def sample_function(a, b):
            return a + b

        result = sample_function(1, 2)
        assert result == 3

        assert len(logs) == 2
        assert "Calling sample_function with" in logs[0]
        assert "args: (1, 2)" in logs[0]
        assert "Function sample_function took" in logs[1]
        assert "and returned \"3\"" in logs[1]


    def test_with_kwargs(self):
        logs = []
        def capture(message : str):
            logs.append(message)
        
        Logger.add_target(capture, Levels.TRACE)
        Logger.set_default_module_level(Levels.TRACE)
        
        @debug_func(use_chrono=False)
        def sample_function(a, b, c=None):
            return f"{a}, {b}, {c}"

        result = sample_function(1, 2, c=3)
        assert result == "1, 2, 3"

        assert len(logs) == 2
        assert "Calling sample_function with" in logs[0]
        assert "args: (1, 2)" in logs[0]
        assert "kwargs: {'c': 3}" in logs[0]
        assert "Function sample_function returned \"1, 2, 3\"" in logs[1]


    def test_nested_calls(self):
        logs = []
        def capture(message : str):
            logs.append(message)
        
        Logger.add_target(capture, Levels.TRACE)
        Logger.set_default_module_level(Levels.TRACE)

        @debug_func(use_chrono=False)
        def inner_function(x):
            return x * 2

        @debug_func(use_chrono=False)
        def outer_function(y):
            return inner_function(y) + 1

        result = outer_function(3)
        assert result == 7

        assert len(logs) == 4
        assert "Calling outer_function with" in logs[0]
        assert "Calling inner_function with" in logs[1]
        assert "Function inner_function returned \"6\"" in logs[2]
        assert "Function outer_function returned \"7\"" in logs[3]
