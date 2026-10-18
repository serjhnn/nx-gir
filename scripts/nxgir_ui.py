"""Small curses helpers shared by the nx-gir screens."""

import curses
import os
import sys

# Themes: the colors (256-color numbers) for each one.
# text/title/help/rule/mark are foregrounds on bg.
B, U = curses.A_BOLD, curses.A_UNDERLINE
PALETTES = {
    # cream paper, brown ink, red rubrics
    "sepia": dict(
        bg=230,
        text=94,
        title=88,
        help=95,
        rule=137,
        mark=88,
    ),
    # dark brown-black page for reading at night
    "night": dict(
        bg=234,
        text=223,
        title=179,
        help=137,
        rule=95,
        mark=216,
    ),
    # gold on deep red, like the logo
    "gold": dict(
        bg=52,
        text=222,
        title=220,
        help=180,
        rule=136,
        mark=214,
    ),
    # black ink on white paper
    "paper": dict(
        bg=231,
        text=235,
        title=88,
        help=242,
        rule=248,
        mark=124,
    ),
    # pink Armenian tuff stone
    "tuff": dict(
        bg=181,
        text=52,
        title=88,
        help=238,
        rule=138,
        mark=53,
    ),
    # pale letters on deep blue ink
    "ink": dict(
        bg=17,
        text=189,
        title=222,
        help=146,
        rule=60,
        mark=117,
    ),
}
EXTRA = {"title": B, "mark": U}


def roles(pal):
    """{role: (fg, bg, extra attributes)} for a palette."""
    return {
        role: (pal[role], pal["bg"], EXTRA.get(role, 0))
        for role in (
            "text",
            "title",
            "help",
            "rule",
            "mark",
        )
    }


THEMES = {n: roles(p) for n, p in PALETTES.items()}
THEMES["plain"] = None
PLAIN = {
    "text": 0,
    "title": curses.A_BOLD,
    "help": curses.A_DIM,
    "rule": 0,
    "mark": curses.A_UNDERLINE,
}
THEME_NAMES = {
    "sepia": "sepia: old book",
    "night": "night: dark page for the evening",
    "gold": "gold: gold on deep red",
    "paper": "paper: black ink on white",
    "tuff": "tuff: pink Armenian stone",
    "ink": "ink: pale letters on deep blue",
    "plain": "plain: the terminal's colors",
}


class Style:
    """The current theme: style(role) gives curses
    attributes for that role."""

    def __init__(self):
        self.name = "plain"
        self.attrs = dict(PLAIN)

    def __call__(self, role):
        return self.attrs[role]

    def use(self, win, name):
        """Switch to theme name; False if the terminal
        lacks the colors (then plain is used)."""
        spec = THEMES.get(name)
        ok = spec is None or self.colors()
        if not ok:
            spec, name = None, "plain"
        self.name = name
        if spec is None:
            self.attrs = dict(PLAIN)
            win.bkgd(" ", 0)
            return ok
        self.attrs = {}
        for n, (role, (fg, bg, extra)) in enumerate(
            spec.items(), start=1
        ):
            curses.init_pair(n, fg, bg)
            self.attrs[role] = curses.color_pair(n) | extra
        win.bkgd(" ", self.attrs["text"])
        return ok

    @staticmethod
    def colors():
        """True if the terminal has 256 colors."""
        try:
            if not curses.has_colors():
                return False
            curses.start_color()
            curses.use_default_colors()
        except curses.error:
            return False
        return curses.COLORS >= 256

    def next(self, win):
        """Switch to the next theme; message to show."""
        names = list(THEMES)
        i = names.index(self.name)
        want = names[(i + 1) % len(names)]
        if not self.use(win, want):
            return "colors need a 256-color terminal"
        return self.describe()

    def describe(self):
        """'theme 2/7 · night: dark page …'"""
        names = list(THEMES)
        n = names.index(self.name) + 1
        what = THEME_NAMES[self.name]
        return f"theme {n}/{len(names)} · {what}"


style = Style()


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
