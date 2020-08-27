#!/usr/bin/python3

# Common functions
from settings import *


def logger(level, message):
    if LOG_LEVEL == "crit":
        if level == "crit":
            print(message)
    elif LOG_LEVEL == "warn":
        if level == "crit" or level == "warn":
            print(message)
    elif LOG_LEVEL == "info":
        print(message)
    else:
        pass


def custom_icon(name):
    import os
    if str(name) in os.environ:
        return os.environ[str(name)]
    else:
        return icon_default
