import ctypes
from contextlib import contextmanager
from logging import StreamHandler

from py_tools.common import LINUX, WINDOWS
from py_tools.consts.colors import *

__author__ = 'gusatenko'

COLORS_LINUX = {
    BLACK: 30,
    DARK_BLUE: 34,
    DARK_GREEN: 32,
    DARK_CYAN: 36,
    DARK_RED: 91,
    DARK_MAGENTA: 35,
    DARK_YELLOW: 33,
    GREY: 37,
    DARK_GREY: 90,
    BLUE: 94,
    GREEN: 92,
    CYAN: 96,
    RED: 31,
    MAGENTA: 95,
    YELLOW: 93,
    WHITE: 97,
}


@contextmanager
def color_switch_linux(color, stream):
    code = COLORS_LINUX[color]
    stream.write('\33[0;{}m'.format(code))
    try:
        yield
    finally:
        stream.write('\33[m')


COLORS_WINDOWS = {
    BLACK: 0,
    DARK_BLUE: 1,
    DARK_GREEN: 2,
    DARK_CYAN: 3,
    DARK_RED: 4,
    DARK_MAGENTA: 5,
    DARK_YELLOW: 6,
    GREY: 7,
    DARK_GREY: 8,
    BLUE: 9,
    GREEN: 10,
    CYAN: 11,
    RED: 12,
    MAGENTA: 13,
    YELLOW: 14,
    WHITE: 15,
}


@contextmanager
def color_switch_windows(color, handle, bg_color=None):
    code = COLORS_WINDOWS[color]
    if bg_color:
        code += COLORS_WINDOWS[bg_color] * 16
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, code)
    try:
        yield
    finally:
        code = COLORS_WINDOWS[GREY]
        ctypes.windll.kernel32.SetConsoleTextAttribute(handle, code)


# Constant from the Windows API
STD_OUTPUT_HANDLE = -11


class ColoredStreamHandler(StreamHandler):
    DEFAULT_COLOR = GREY

    def __init__(self, color=None, stream=None):
        self.color = color or self.DEFAULT_COLOR
        super().__init__(stream=stream)
        self.stdout_handle = None
        if WINDOWS:
            self.stdout_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def level_to_color(self, levelno):
        if levelno >= 40:
            return RED
        elif levelno >= 30:
            return DARK_RED
        else:
            return self.color

    if WINDOWS:

        def emit(self, record):
            with color_switch_windows(
                self.level_to_color(record.levelno), self.stdout_handle
            ):
                super().emit(record)

    elif LINUX:

        def emit(self, record):
            with color_switch_linux(self.level_to_color(record.levelno), self.stream):
                super().emit(record)
