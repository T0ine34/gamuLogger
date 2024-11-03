import argparse

from gamuLogger import LEVELS, Logger, critical, debug, debugFunc, error, info

Logger.setModule("example1")

@debugFunc(True) # True or False to enable or disable chrono
def addition(a, b):
    return a + b

@debugFunc(True)
def division(a, b):
    return a / b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("a", type=int)
    parser.add_argument("b", type=int)
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()
    if args.debug:
        Logger.setLevel('stdout', LEVELS.DEBUG)

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
        critical(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
