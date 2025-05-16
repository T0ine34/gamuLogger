#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ###############################################################################################
#                                   PYLINT
# pylint: disable=line-too-long
# ###############################################################################################

"""
GamuLogger - A simple and powerful logging library for Python

Antoine Buirey 2025
"""

import re

RE_AGE_CONDITION = re.compile(r"(?:age\s*)?(?P<operator>>|>=|<|<=|==|!=)\s*(?P<value>\d+)\s*(?P<unit>(?:hour|minute|second|day|week|month|year)s?)")
RE_SIZE_CONDITION = re.compile(r"(?:size\s*)?(?P<operator>>|>=|<|<=|==|!=)\s*(?P<value>\d+)\s*(?P<unit>(?:KB|MB|GB|TB)s?)")
RE_NB_FILES_CONDITION = re.compile(r"(?:nb_files\s*)?(?P<operator>>|>=|==|!=)\s*(?P<value>\d+)")

RE_YEAR     = r"\d{4}"
RE_MONTH    = r"[01]\d"
RE_DAY      = r"[0-3]\d"
RE_HOUR     = r"[0-2]\d"
RE_MINUTE   = r"[0-5]\d"
RE_SECOND   = r"[0-5]\d"
RE_PID      = r"\d+"

RE_DATE     = r"\d{4}-[01]\d-[0-3]\d"
RE_TIME     = r"[0-2]\d:[0-5]\d:[0-5]\d"
RE_DATETIME = r"\d{4}-[01]\d-[0-3]\d_[0-2]\d:[0-5]\d:[0-5]\d"
