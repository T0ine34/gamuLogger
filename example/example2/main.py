import argparse
import threading
import time

from gamuLogger import Logger, critical, debug, debugFunc, error, info

Logger.showProcessName()
Logger.showThreadsName()

def doSomething():
    for i in range(10):
        info(f"Doing something {i}")
        time.sleep(1)

def doSomethingElse():
    for i in range(10):
        info(f"Doing something else {i}")
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser()
    Logger.configArgParse(parser)

    args = parser.parse_args()
    Logger.parseArgs(args)

    thread1 = threading.Thread(target=doSomething)
    thread2 = threading.Thread(target=doSomethingElse)

    Logger.info("Starting threads")
    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
    Logger.info("Threads finished")

if __name__ == "__main__":
    main()
