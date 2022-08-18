from enum import Enum


class Mode(Enum):
    SHORT_BREAK = 0
    LONG_BREAK = 1
    POMODORO = 2


class Status(Enum):
    RUNNING = 0
    STOPPED = 1


SHORT_BREAK = 300 # 5 minutes
LONG_BREAK = 900 # 15 minutes
POMODORO = 1500 # 25 minutes