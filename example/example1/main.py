import argparse

from gamuLogger import (Levels, Logger, config_argparse, config_logger, debug,
                        debug_func, error, fatal, info, trace)

Logger.set_module("main")

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
    config_argparse(parser)

    args = parser.parse_args()
    config_logger(args)

    trace("starting operation")

    a = args.a
    b = args.b
    Logger.set_module("addition")

    info(f"Adding {a} and {b}")
    result = addition(a, b)
    info(f"Result: {result}")

    Logger.set_module("division")

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
