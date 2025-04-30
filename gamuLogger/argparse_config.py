#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ###############################################################################################
#                                   PYLINT
# Disable C0301 = Line too long (80 chars by line is not enough)
# pylint: disable=line-too-long
# ###############################################################################################

"""
configuration for argparse
"""

import argparse

from .gamu_logger import Levels, Logger, Target


def validate_module_level(_input : str) -> tuple[str, Levels]:
    """
    Validate the module level input
    """
    if ':' not in _input:
        raise argparse.ArgumentTypeError(f"Invalid module level format: {_input}. "
            "Format: MODULE:LEVEL, where LEVEL is one of: "
            f"{', '.join([level.name for level in Levels])}.")

    name, level = _input.split(":")

    if not name:
        raise argparse.ArgumentTypeError(f"name cannot be empty: {_input}. ")

    try:
        level = Levels.from_string(level)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid logging level: {level}. "
            "Format: LEVEL, where LEVEL is one of: "
            f"{', '.join([level.name for level in Levels])}.") from None

    return name, level

def validate_log_file(_input : str) -> tuple[str, Levels]:
    """
    Validate the log file input
    """
    if ':' not in _input:
        file = _input
        level = "info"
    else:
        file, level = _input.split(":")

    if not file:
        raise argparse.ArgumentTypeError(f"File cannot be empty: {_input}. ")

    if not level:
        level = "info"

    try:
        level = Levels.from_string(level)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid logging level: {level}. "
            "Format: LEVEL, where LEVEL is one of: "
            f"{', '.join([level.name for level in Levels])}.") from None

    return file, level

def validate_level(_input : str) -> Levels:
    """
    Validate the level input
    """
    try:
        level = Levels.from_string(_input)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid logging level: {_input}. "
            "Format: LEVEL, where LEVEL is one of: "
            f"{', '.join([level.name for level in Levels])}.") from None

    return level


def config_argparse(parser : argparse.ArgumentParser, /, allow_other_targets : bool = True) -> None:
    """
    Configuration for argparse
    """
    group = parser.add_argument_group(
        "logging",
        "Logger configuration",
    )

    verbose_group = group.add_mutually_exclusive_group(required=False)

    verbose_group.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity level (default: 0), up to 2 (0 is info, 2 is trace)",
    )

    verbose_group.add_argument(
        "-q",
        "--quiet",
        action="count",
        default=0,
        help="Decrease verbosity level (default: 0), up to 4 (0 is info, 4 is complely silent)",
    )

    verbose_group.add_argument(
        "--level",
        type=validate_level,
        default="info",
        metavar="LEVEL",
        help="Set the logging level. "
             "Format: LEVEL, where LEVEL is one of: "
             f"{', '.join([level.name for level in Levels])}.",
    )

    if allow_other_targets:
        group.add_argument(
            "--log-file",
            action="append",
            default=[],
            type=validate_log_file,
            metavar="FILE:LEVEL",
            help="Log to a file with a specific level (default: info). "
                "Format: FILE:LEVEL, where LEVEL is one of: "
                f"{', '.join([level.name for level in Levels])}. Can be ommited to use the default level."
                "You can specify multiple files.",
        )

        group.add_argument(
            "--module-level",
            type=validate_module_level,
            action="append",
            default=[],
            metavar="MODULE:LEVEL",
            help="Set the logging level for a specific module. "
                "If the name of the module doesn't exist, this do nothing. "
                "Format: MODULE:LEVEL, where LEVEL is one of: "
                f"{', '.join([level.name for level in Levels])}.",
        )


def config_logger(args : argparse.Namespace):
    """
    Configuration for the logger
    """
    # Set the logging level
    if args.verbose > 2:
        raise argparse.ArgumentTypeError(
            "Verbose level must be between 0 and 2 (inclusive)."
        )
    elif args.verbose == 2:
        level = Levels.TRACE
    elif args.verbose == 1:
        level = Levels.DEBUG

    elif args.quiet == 1:
        level = Levels.WARNING
    elif args.quiet == 2:
        level = Levels.ERROR
    elif args.quiet == 3:
        level = Levels.FATAL
    elif args.quiet == 4:
        level = Levels.NONE
    elif args.quiet > 4:
        raise argparse.ArgumentTypeError(

            "Quiet level must be between 0 and 4 (inclusive)."
        )
    else:
        level = args.level

    Logger.set_level("stdout", level)

    # Set the logging level for each module
    for module, level in args.module_level:
        if module == "all":
            Logger.set_default_module_level(level)
        else:
            Logger.set_module_level(module, level)

    # Set the logging level for each file
    for file, level in args.log_file:
        Logger.add_target(Target.from_file(file), level)
