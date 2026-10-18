"""Full-screen file list and text viewer (curses).

Vim-style keys. Linux and Termux only.
"""

import curses
import locale
import textwrap

LIST_HELP = (
    "↑↓/jk move · g/G ends · / search · Enter open · q quit"
)
VIEW_HELP = (
    "↑↓/jk scroll · space/b page · g/G ends · "
    "/ search · q back"
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


def put(win, y, x, text, attr=0):
    """Write text clipped to the window, ignore errors."""
    h, w = win.getmaxyx()
    if not (0 <= y < h) or x >= w:
        return
    try:
        win.addnstr(y, x, text, w - x - 1, attr)
    except curses.error:
        pass


def prompt(win, label):
    """Read a line at the bottom. None on Esc."""
    h, w = win.getmaxyx()
    text = ""
    curses.curs_set(1)
    try:
        while True:
            line = label + text
            win.move(h - 1, 0)
            win.clrtoeol()
            put(win, h - 1, 0, line)
            win.move(h - 1, min(len(line), w - 2))
            ch = win.get_wch()
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
        curses.curs_set(0)


def key_name(ch):
    """Map a get_wch() result to one action name."""
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


def list_view(win, files, title):
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
        put(win, 0, 0, head, curses.A_BOLD)
        put(win, 0, max(w - len(count) - 1, 0), count)
        put(win, 1, 0, "─" * (w - 1))
        if not files:
            put(win, 2, 1, "no files")
        shown = files[pane.top : pane.top + rows]
        for i, (name, size, _) in enumerate(shown):
            idx = pane.top + i
            sz = human_size(size)
            left = f" {name}"
            gap = w - 1 - len(left) - len(sz) - 1
            line = left + " " * max(gap, 1) + sz + " "
            attr = (
                curses.A_REVERSE if idx == pane.pos else 0
            )
            put(win, 2 + i, 0, line.ljust(w - 1), attr)
        put(
            win,
            h - 1,
            0,
            pane.msg or LIST_HELP,
            curses.A_DIM,
        )
        pane.msg = ""
        win.refresh()

        action = key_name(win.get_wch())
        if action == "quit":
            return
        if action in ("search", "next", "prev"):
            pane.search(win, names, action)
        elif action == "enter" and files:
            name, _, path = files[pane.pos]
            text_view(win, path, name)
        elif action not in (None, "back", "resize"):
            pane.move(action, rows)


def wrap(text, width):
    """Wrap text to width, keeping blank lines."""
    width = max(width, 10)
    out = []
    for para in text.splitlines():
        out.extend(textwrap.wrap(para, width) or [""])
    return out


def text_view(win, path, title):
    """Scroll through a text file."""
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(
            encoding="utf-8", errors="replace"
        )
    except OSError as e:
        text = f"cannot open file: {e}"
    pane = Pane(0)
    width = None
    while True:
        h, w = win.getmaxyx()
        rows = max(h - 3, 1)
        if w != width:
            width = w
            lines = wrap(text, w - 2)
            pane.count = len(lines)
        # pos is the first visible line in this view
        pane.pos = min(pane.pos, max(len(lines) - rows, 0))
        win.erase()
        pct = 100
        if len(lines) > rows:
            pct = 100 * pane.pos // (len(lines) - rows)
        info = f"{pct}% "
        put(win, 0, 0, f" {title}", curses.A_BOLD)
        put(win, 0, max(w - len(info) - 1, 0), info)
        put(win, 1, 0, "─" * (w - 1))
        for i in range(rows):
            n = pane.pos + i
            if n >= len(lines):
                break
            attr = 0
            q = pane.query.casefold()
            if q and q in lines[n].casefold():
                attr = curses.A_BOLD
            put(win, 2 + i, 1, lines[n], attr)
        put(
            win,
            h - 1,
            0,
            pane.msg or VIEW_HELP,
            curses.A_DIM,
        )
        pane.msg = ""
        win.refresh()

        action = key_name(win.get_wch())
        if action in ("quit", "back"):
            return
        if action in ("search", "next", "prev"):
            pane.search(win, lines, action)
        elif action == "bottom":
            pane.pos = max(len(lines) - rows, 0)
        elif action not in (None, "enter", "resize"):
            pane.move(action, rows)


def browse(files, title):
    """Open the file list full-screen."""
    locale.setlocale(locale.LC_ALL, "")

    def main(win):
        curses.set_escdelay(25)
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        win.keypad(True)
        list_view(win, files, title)

    curses.wrapper(main)
