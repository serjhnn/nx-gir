"""Full-screen file list (curses).

Vim-style keys. Linux and Termux only.
"""

import curses
import locale
import os
from typing import NamedTuple

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
    shorten,
    style,
)

LIST_HELP = (
    "j/k move · Enter open · h back · / search · q quit",
    "j/k move · Enter open · h back · q quit",
    "j/k Enter h / q",
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
        curses.KEY_BACKSPACE: "back",
        "\x7f": "back",
        "\b": "back",
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


class Item(NamedTuple):
    """One row of the bookshelf."""

    label: str  # what is shown
    name: str  # book name, or folder path ("" = top)
    folder: bool
    size: int  # bytes, or books inside for a folder
    path: object = None  # Path of a book


def parent(folder):
    """The folder above: "a/b" -> "a", "a" -> ""."""
    return folder.rpartition("/")[0]


def folder_items(files, folder):
    """Rows for one folder of files [(name, size, path)]:
    ".." (below the top), then folders, then books."""
    prefix = f"{folder}/" if folder else ""
    counts = {}
    books = []
    for name, size, path in files:
        if not name.startswith(prefix):
            continue
        rest = name[len(prefix) :]
        sub, slash, _ = rest.partition("/")
        if slash:
            counts[sub] = counts.get(sub, 0) + 1
        else:
            books.append(
                Item(rest, name, False, size, path)
            )
    items = [
        Item(f"{d}/", prefix + d, True, n)
        for d, n in sorted(counts.items())
    ]
    if folder:
        up = Item("..", parent(folder), True, 0)
        items.insert(0, up)
    return items + books


def folder_exists(files, folder):
    return not folder or any(
        name.startswith(f"{folder}/")
        for name, _, _ in files
    )


def item_line(item, state, w):
    """The text of one row, w columns wide."""
    if item.label == "..":
        right = "up"
    elif item.folder:
        n = item.size
        right = f"{n} book{'s' * (n != 1)}"
    else:
        right = human_size(item.size)
        pct = state.progress(item.name)
        if pct is not None:
            right = f"{pct:>3}%  {right:>8}"
    room = w - len(right) - 4
    left = f" {shorten(item.label, room)}"
    gap = w - 1 - len(left) - len(right) - 1
    return left + " " * max(gap, 1) + right + " "


class Shelf:
    """Which folder is open and where the cursor is."""

    def __init__(self, files, folder=""):
        self.files = files
        self.names = [name for name, _, _ in files]
        self.pane = Pane(0)
        self.places = {}  # folder -> cursor row
        self.open(
            folder if folder_exists(files, folder) else ""
        )

    def open(self, folder, select=None):
        """Show folder; put the cursor on item name
        select, or where it was last time."""
        self.places[getattr(self, "folder", "")] = (
            self.pane.pos
        )
        self.folder = folder
        self.items = folder_items(self.files, folder)
        self.pane.count = len(self.items)
        self.pane.top = 0
        # first visit: the first entry under ".."
        pos = self.places.get(folder, 1 if folder else 0)
        for i, item in enumerate(self.items):
            if item.name == select and item.label != "..":
                pos = i
        self.pane.pos = min(
            pos, max(len(self.items) - 1, 0)
        )

    def up(self):
        if self.folder:
            self.open(
                parent(self.folder), select=self.folder
            )

    def search(self, win, action):
        """Find a book in any folder by name."""
        pane = self.pane
        if action == "search":
            q = prompt(win, "/")
            if not q:
                return
            pane.query = q
        elif not pane.query:
            return
        step = -1 if action == "prev" else 1
        cur = self.items[pane.pos] if self.items else None
        start = -1 if step > 0 else len(self.names)
        if cur and not cur.folder:
            start = self.names.index(cur.name)
        hit = find(self.names, pane.query, start, step)
        if hit is None:
            pane.msg = f"not found: {pane.query}"
            return
        name = self.names[hit]
        self.open(parent(name), select=name)


def list_view(win, files, title, state):
    """Browse files [(name, size, path)] by folder."""
    shelf = Shelf(files, state.settings.get("shelf", ""))
    pane = shelf.pane
    while True:
        h, w = win.getmaxyx()
        rows = max(h - 4, 1)
        pane.scroll(rows)
        win.erase()
        where = title
        if shelf.folder:
            where = f"{title}/{shelf.folder}"
        n = sum(
            i.size if i.folder else 1
            for i in shelf.items
            if i.label != ".."
        )
        count = f"{n} book{'s' * (n != 1)} "
        room = w - len(count) - 3
        put(
            win,
            0,
            0,
            f" {shorten(where, room)}",
            style("title"),
        )
        put(win, 0, max(w - len(count) - 1, 0), count)
        put(win, 1, 0, "─" * (w - 1), style("rule"))
        if not shelf.items:
            put(win, 2, 1, "no books")
        shown = shelf.items[pane.top : pane.top + rows]
        for i, item in enumerate(shown):
            line = item_line(item, state, w)
            attr = 0
            if pane.top + i == pane.pos:
                attr = style("cursor")
            elif item.folder:
                attr = style("title")
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
                theme=style.wanted,
                dim=style.dim,
                shelf=shelf.folder,
            )
            state.save()
            return
        item = (
            shelf.items[pane.pos] if shelf.items else None
        )
        if action in ("search", "next", "prev"):
            shelf.search(win, action)
        elif action == "theme":
            pane.msg = style.next(win)
        elif action == "dim":
            pane.msg = style.next_dim(win)
        elif action == "back":
            shelf.up()
        elif action == "enter" and item:
            if item.label == "..":
                shelf.up()
            elif item.folder:
                shelf.open(item.name)
            else:
                nxgir_reader.read(
                    win, item.path, item.name, state
                )
        elif action not in (None, "resize", "enter"):
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
