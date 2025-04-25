import argparse
import threading
import time

from gamuLogger import Logger, debug, debug_func, error, fatal, info

Logger.show_process_name()
Logger.show_threads_name()

Logger.set_module('example')

def doSomething():
    Logger.set_module('example.func1')
    for i in range(10):
        info(f"Doing something {i}")
        time.sleep(1)

def doSomethingElse():
    Logger.set_module('example.func2')
    for i in range(10):
        info(f"Doing something else {i}")
        time.sleep(1)

def main():
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
