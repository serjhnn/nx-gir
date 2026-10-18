"""Full-screen file list (curses).

Vim-style keys. Linux and Termux only.
"""

import curses
import locale
import os

import nxgir_reader
from nxgir_state import State
from nxgir_ui import (
    DIMS,
    THEMES,
    cursor,
    fit,
    key,
    prompt,
    put,
    style,
)

LIST_HELP = (
    "↑↓/jk move · g/G ends · / search · "
    "Enter open · q quit",
    "j/k move · / search · Enter open · q quit",
    "j/k / Enter q",
)


def human_size(n):
    """Byte count as a short string: 512 B, 3.4 KB."""
    for unit in ("B", "KB", "MB"):
        if n < 1024 or unit == "MB":
            if unit == "B":
                return f"{n} B"
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def key_name(ch):
    """Map a key press to one action name."""
    keys = {
        curses.KEY_UP: "up",
        "k": "up",
        curses.KEY_DOWN: "down",
        "j": "down",
        curses.KEY_PPAGE: "pgup",
        "\x02": "pgup",
        "b": "pgup",
        curses.KEY_NPAGE: "pgdn",
        "\x06": "pgdn",
        " ": "pgdn",
        curses.KEY_HOME: "top",
        "g": "top",
        curses.KEY_END: "bottom",
        "G": "bottom",
        "/": "search",
        "n": "next",
        "N": "prev",
        "\n": "enter",
        "\r": "enter",
        curses.KEY_ENTER: "enter",
        curses.KEY_RIGHT: "enter",
        "l": "enter",
        "q": "quit",
        "T": "theme",
        "d": "dim",
        "\x1b": "quit",
        curses.KEY_LEFT: "back",
        "h": "back",
        curses.KEY_RESIZE: "resize",
    }
    return keys.get(ch)


def find(items, query, start, step):
    """Index of the next item containing query."""
    q = query.casefold()
    n = len(items)
    for i in range(1, n + 1):
        j = (start + i * step) % n
        if q in items[j].casefold():
            return j
    return None


class Pane:
    """Cursor and scroll state shared by both views."""

    def __init__(self, count):
        self.count = count
        self.pos = 0
        self.top = 0
        self.query = ""
        self.msg = ""

    def move(self, action, page):
        last = max(self.count - 1, 0)
        step = {
            "up": -1,
            "down": 1,
            "pgup": -page,
            "pgdn": page,
        }
        if action in step:
            self.pos += step[action]
        elif action == "top":
            self.pos = 0
        elif action == "bottom":
            self.pos = last
        self.pos = max(0, min(self.pos, last))

    def scroll(self, rows):
        """Keep pos inside the visible rows."""
        if self.pos < self.top:
            self.top = self.pos
        elif self.pos >= self.top + rows:
            self.top = self.pos - rows + 1
        self.top = max(0, self.top)

    def search(self, win, items, action):
        if action == "search":
            q = prompt(win, "/")
            if not q:
                return
            self.query = q
            start, step = self.pos, 1
        elif not self.query:
            return
        else:
            start = self.pos
            step = 1 if action == "next" else -1
        hit = find(items, self.query, start, step)
        if hit is None:
            self.msg = f"not found: {self.query}"
        else:
            self.pos = hit


def list_view(win, files, title, state):
    """Pick a file from files: [(name, size, path)]."""
    pane = Pane(len(files))
    names = [name for name, _, _ in files]
    while True:
        h, w = win.getmaxyx()
        rows = max(h - 4, 1)
        pane.scroll(rows)
        win.erase()
        head = f" {title}"
        count = f"{len(files)} files "
        put(win, 0, 0, head, style("title"))
        put(win, 0, max(w - len(count) - 1, 0), count)
        put(win, 1, 0, "─" * (w - 1), style("rule"))
        if not files:
            put(win, 2, 1, "no files")
        shown = files[pane.top : pane.top + rows]
        for i, (name, size, _) in enumerate(shown):
            idx = pane.top + i
            sz = human_size(size)
            pct = state.progress(name)
            if pct is not None:
                sz = f"{pct:>3}%  {sz:>8}"
            left = f" {name}"
            gap = w - 1 - len(left) - len(sz) - 1
            line = left + " " * max(gap, 1) + sz + " "
            attr = style("cursor") if idx == pane.pos else 0
            put(win, 2 + i, 0, line.ljust(w - 1), attr)
        put(
            win,
            h - 1,
            0,
            pane.msg or fit(LIST_HELP, w),
            style("help"),
        )
        pane.msg = ""
        win.refresh()

        action = key_name(key(win))
        if action == "quit":
            state.settings.update(
                theme=style.wanted, dim=style.dim
            )
            state.save()
            return
        if action in ("search", "next", "prev"):
            pane.search(win, names, action)
        elif action == "theme":
            pane.msg = style.next(win)
        elif action == "dim":
            pane.msg = style.next_dim(win)
        elif action == "enter" and files:
            name, _, path = files[pane.pos]
            nxgir_reader.read(win, path, name, state)
        elif action not in (
            None,
            "back",
            "resize",
            "theme",
            "dim",
        ):
            pane.move(action, rows)


def browse(files, title):
    """Open the file list full-screen."""
    locale.setlocale(locale.LC_ALL, "")

    def main(win):
        curses.set_escdelay(25)
        cursor(False)
        win.keypad(True)
        state = State.load()
        st = state.settings
        if st.get("dim") in range(len(DIMS)):
            style.dim = st["dim"]
        theme = os.environ.get("NXGIR_THEME") or st["theme"]
        if theme not in THEMES:
            theme = "sepia"
        style.use(win, theme)
        list_view(win, files, title, state)

    curses.wrapper(main)
