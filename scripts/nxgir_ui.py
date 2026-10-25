"""Small curses helpers shared by the nx-gir screens."""

import curses
import os
import sys

# Themes: the colors (256-color numbers) for each one.
# text/title/help/rule/mark are foregrounds on bg.
B, U, R = (
    curses.A_BOLD,
    curses.A_UNDERLINE,
    curses.A_REVERSE,
)
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
    # black volcanic glass: pure black (saves battery
    # on OLED phone screens), soft grey text
    "obsidian": dict(
        bg=16,
        text=250,
        title=173,
        help=244,
        rule=238,
        mark=179,
    ),
}
EXTRA = {"title": B, "mark": U}


def roles(pal):
    """{role: (fg, bg, extra attributes)} for a palette.

    cursor is the text color reversed; unlike text it
    is never dimmed, so it stays easy to find.
    """
    out = {
        role: (pal[role], pal["bg"], EXTRA.get(role, 0))
        for role in (
            "text",
            "title",
            "help",
            "rule",
            "mark",
        )
    }
    out["cursor"] = (pal["text"], pal["bg"], R)
    return out


THEMES = {n: roles(p) for n, p in PALETTES.items()}
THEMES["plain"] = None
PLAIN = {
    "text": 0,
    "title": curses.A_BOLD,
    "help": curses.A_DIM,
    "rule": 0,
    "mark": curses.A_UNDERLINE,
    "cursor": curses.A_REVERSE,
}
THEME_NAMES = {
    "sepia": "sepia: old book",
    "night": "night: dark page for the evening",
    "gold": "gold: gold on deep red",
    "paper": "paper: black ink on white",
    "tuff": "tuff: pink Armenian stone",
    "ink": "ink: pale letters on deep blue",
    "obsidian": "obsidian: grey on pure black",
    "plain": "plain: the terminal's colors",
}


# Dim levels: how far the text color moves toward the
# page color (0 = normal).
DIMS = (0.0, 0.35, 0.6)
DIM_NAMES = ("text: normal", "text: dim", "text: dimmer")


def rgb(n):
    """RGB of a 256-color number (16-255)."""
    if n >= 232:
        v = 8 + (n - 232) * 10
        return v, v, v
    n -= 16
    steps = (0, 95, 135, 175, 215, 255)
    return steps[n // 36], steps[n // 6 % 6], steps[n % 6]


def nearest(color):
    """256-color number closest to an RGB color."""

    def dist(n):
        return sum(
            (a - b) ** 2 for a, b in zip(rgb(n), color)
        )

    return min(range(16, 256), key=dist)


def fade(fg, bg, amount):
    """fg moved amount (0-1) of the way toward bg."""
    if not amount:
        return fg
    mix = [
        a + (b - a) * amount
        for a, b in zip(rgb(fg), rgb(bg))
    ]
    n = nearest(mix)
    return fg if n == bg else n


class Style:
    """The current theme: style(role) gives curses
    attributes for that role."""

    def __init__(self):
        self.name = "plain"
        self.wanted = "plain"  # chosen, even if not shown
        self.attrs = dict(PLAIN)
        self.dim = 0  # index into DIMS

    def __call__(self, role):
        return self.attrs[role]

    def use(self, win, name):
        """Switch to theme name; False if the terminal
        lacks the colors (then plain is used)."""
        spec = THEMES.get(name)
        self.wanted = name
        ok = spec is None or self.colors()
        if not ok:
            spec, name = None, "plain"
        self.name = name
        if spec is None:
            self.attrs = dict(PLAIN)
            if self.dim:
                self.attrs["text"] = curses.A_DIM
            win.bkgd(" ", self.attrs["text"])
            return ok
        self.attrs = {}
        for n, (role, (fg, bg, extra)) in enumerate(
            spec.items(), start=1
        ):
            if role == "text":
                fg = fade(fg, bg, DIMS[self.dim])
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

    def next_dim(self, win):
        """Step to the next dim level; message to show."""
        self.dim = (self.dim + 1) % len(DIMS)
        self.use(win, self.name)
        return DIM_NAMES[self.dim]

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


def shorten(path, width):
    """path cut to width from the left, keeping the
    file name: …/new-testament/2-mark.txt."""
    if len(path) <= width:
        return path
    if width < 2:
        return path[:width]
    tail = path[-(width - 1) :]
    cut = tail.find("/")
    if 0 < cut < len(tail) - 1:
        tail = tail[cut:]  # start at a folder
    return "…" + tail


def fit(texts, width):
    """First text that fits width (longest first)."""
    for t in texts:
        if len(t) < width:
            return t
    return texts[-1]


def help_line(items, width):
    """A help line from (keys, what, priority) items.

    Takes items by priority (lowest number first) while
    the line still fits width, and shows them in the
    order given. Priority 0 items are always shown;
    when they don't fit with their words, the keys
    alone are shown.
    """
    ranked = sorted(
        range(len(items)), key=lambda i: items[i][2]
    )
    need = [i for i in ranked if items[i][2] == 0]
    rest = [i for i in ranked if items[i][2] != 0]

    def line(chosen, words):
        parts = []
        for i in sorted(chosen):
            k, what, _ = items[i]
            parts.append(f"{k} {what}" if words else k)
        return (" · " if words else " ").join(parts)

    for words in (True, False):
        chosen = set(need)
        if len(line(chosen, words)) >= width and words:
            continue
        for i in rest:
            if len(line(chosen | {i}, words)) >= width:
                break
            chosen.add(i)
        return line(chosen, words)


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


def confirm(win, question, redraw=None):
    """Ask question at the bottom; True only for y.
    After a resize, redraw() (if given) repaints the
    screen and the question is asked again."""
    while True:
        h, w = win.getmaxyx()
        win.move(h - 1, 0)
        win.clrtoeol()
        put(win, h - 1, 0, f"{question} y/n", style("help"))
        win.refresh()
        ch = key(win)
        if ch == curses.KEY_RESIZE:
            if redraw:
                redraw()
            continue
        return ch in ("y", "Y")


def tail(line, width):
    """line, or …and its end if longer than width."""
    if len(line) <= width:
        return line
    return "…" + line[-(width - 1) :]


def prompt(win, label, text="", redraw=None):
    """Read a line at the bottom, starting with text.
    None on Esc. A long line shows its end. After a
    resize, redraw() (if given) repaints the screen."""
    cursor(True)
    try:
        while True:
            h, w = win.getmaxyx()
            line = tail(label + text, w - 2)
            win.move(h - 1, 0)
            win.clrtoeol()
            put(win, h - 1, 0, line)
            win.move(h - 1, min(len(line), w - 2))
            ch = key(win)
            if ch in ("\n", "\r", curses.KEY_ENTER):
                return text
            if ch == "\x1b":
                return None
            if ch == curses.KEY_RESIZE and redraw:
                redraw()
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
