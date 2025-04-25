import argparse

from gamuLogger import (Levels, Logger, debug, debug_func, error, fatal, info,
                        trace)

Logger.set_module("example1")

@debug_func(True) # True or False to enable or disable chrono
def addition(a, b):
    return a + b

@debug_func(True)
def division(a, b):
    return a / b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("a", type=int)
    parser.add_argument("b", type=int)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--trace", action="store_true")

    args = parser.parse_args()
    if args.debug:
        Logger.set_level('stdout', Levels.DEBUG)
    if args.trace:
        Logger.set_level('stdout', Levels.TRACE)

    trace("starting operation")

    a = args.a
    b = args.b

    info(f"Adding {a} and {b}")
    result = addition(a, b)
    info(f"Result: {result}")

    info(f"Dividing {a} by {b}")
    try:
        result = division(a, b)
        info(f"Result: {result}")
    except Exception as e:
        fatal(f"Error: {e}")
        exit(1)
    finally:
        trace("operation finished")


if __name__ == "__main__":
    main()
