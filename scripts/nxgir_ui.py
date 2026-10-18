"""Small curses helpers shared by the nx-gir screens."""

import curses
import os
import sys


def put(win, y, x, text, attr=0, right=None):
    """Write text clipped to the window (or to column
    right, exclusive); ignore errors."""
    h, w = win.getmaxyx()
    end = w - 1 if right is None else min(right, w - 1)
    if not (0 <= y < h) or not (0 <= x < end):
        return
    try:
        win.addnstr(y, x, text, end - x, attr)
    except curses.error:
        pass


def fit(texts, width):
    """First text that fits width (longest first)."""
    for t in texts:
        if len(t) < width:
            return t
    return texts[-1]


def key(win):
    """Next key press, or KEY_RESIZE after a resize.

    A resize can interrupt the wait before curses sees
    the new size, so read it from the terminal.
    """
    try:
        ch = win.get_wch()
    except curses.error:
        ch = curses.KEY_RESIZE
    if ch == curses.KEY_RESIZE:
        try:
            fd = sys.__stdout__.fileno()
            size = os.get_terminal_size(fd)
            new = (size.lines, size.columns)
            if new != win.getmaxyx():
                curses.resizeterm(*new)
        except (OSError, curses.error):
            pass
        win.clear()  # repaint all on next refresh
    return ch


def cursor(visible):
    """Show or hide the cursor if the terminal can."""
    try:
        curses.curs_set(1 if visible else 0)
    except curses.error:
        pass


def prompt(win, label):
    """Read a line at the bottom. None on Esc."""
    h, w = win.getmaxyx()
    text = ""
    cursor(True)
    try:
        while True:
            line = label + text
            win.move(h - 1, 0)
            win.clrtoeol()
            put(win, h - 1, 0, line)
            win.move(h - 1, min(len(line), w - 2))
            ch = key(win)
            if ch in ("\n", "\r", curses.KEY_ENTER):
                return text
            if ch == "\x1b":
                return None
            if ch in (
                curses.KEY_BACKSPACE,
                "\x7f",
                "\b",
            ):
                text = text[:-1]
            elif isinstance(ch, str) and ch.isprintable():
                text += ch
    finally:
        cursor(False)
