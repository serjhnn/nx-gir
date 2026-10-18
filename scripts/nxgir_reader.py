"""Interactive reader: word cursor and references.

The top half is the text model (no curses, tested in
tests/test_reader.py). The bottom half draws it.
"""

import curses
import re
import textwrap
from bisect import bisect_left, bisect_right
from typing import NamedTuple

from nxgir_ui import fit, key, prompt, put

# Armenian marks written inside a word: emphasis ՛,
# exclamation ՜, question ՞ and abbreviation ՟.
MARKS = "՛՜՞՟"
LETTERS = r"[^\W\d_]"
WORD_RE = re.compile(
    rf"{LETTERS}+(?:[{MARKS}'’]{LETTERS}*)*"
)
# Marks that don't change which word it is.
STRESS = str.maketrans("", "", "՛՜՞")


def normalize(word):
    """Key for comparing words.

    Ignores case and the stress, exclamation and
    question marks. casefold() also turns the
    ligature և into եւ.
    """
    return word.casefold().translate(STRESS)


class Word(NamedTuple):
    row: int  # wrapped row
    col: int  # column in that row
    text: str
    key: str  # normalize(text)
    line: int  # line in the file, from 0


class Layout(NamedTuple):
    rows: list  # wrapped rows of text
    words: list  # every Word, in reading order
    lines: int  # line count of the file


def layout(text, width):
    """Wrap text to width and find every word."""
    width = max(width, 10)
    lines = text.splitlines()
    rows, words = [], []
    for n, line in enumerate(lines):
        parts = textwrap.wrap(
            line,
            width,
            break_long_words=False,
            break_on_hyphens=False,
        )
        for part in parts or [""]:
            r = len(rows)
            rows.append(part)
            for m in WORD_RE.finditer(part):
                t = m.group()
                words.append(
                    Word(r, m.start(), t, normalize(t), n)
                )
    return Layout(rows, words, len(lines))


def references(words, i):
    """Indexes of every word with the same key as i."""
    key = words[i].key
    return [j for j, w in enumerate(words) if w.key == key]


def find(words, query, start, step=1):
    """Next word after start whose key has query."""
    q = normalize(query)
    n = len(words)
    for k in range(1, n + 1):
        j = (start + k * step) % n
        if q in words[j].key:
            return j
    return None


def vertical(words, i, step):
    """Word on the next (step=1) or previous (-1) row
    that has words, nearest to the current column."""
    rows = [w.row for w in words]
    here = words[i]
    if step > 0:
        j = bisect_right(rows, here.row)
        if j == len(words):
            return i
    else:
        j = bisect_left(rows, here.row) - 1
        if j < 0:
            return i
    row = words[j].row
    lo = bisect_left(rows, row)
    hi = bisect_right(rows, row)

    def dist(k):
        w = words[k]
        end = w.col + len(w.text) - 1
        return max(0, w.col - here.col, here.col - end)

    return min(range(lo, hi), key=dist)


def first_from(words, row):
    """First word on row or after it."""
    rows = [w.row for w in words]
    return min(bisect_left(rows, row), len(words) - 1)


# ---- screen -------------------------------------------

READ_HELP = (
    "w/b word · j/k line · s refs · / find · q back",
    "w/b word · j/k line · s refs · q back",
    "w/b j/k s / q",
)
REFS_HELP = (
    "j/k pick · Enter go · q close",
    "j/k Enter q",
)

KEYS = {
    "w": "next",
    "l": "next",
    curses.KEY_RIGHT: "next",
    "b": "prev",
    "h": "prev",
    curses.KEY_LEFT: "prev",
    "j": "down",
    curses.KEY_DOWN: "down",
    "k": "up",
    curses.KEY_UP: "up",
    " ": "pgdn",
    "\x06": "pgdn",
    curses.KEY_NPAGE: "pgdn",
    "\x02": "pgup",
    curses.KEY_PPAGE: "pgup",
    "g": "first",
    curses.KEY_HOME: "first",
    "G": "last",
    curses.KEY_END: "last",
    "0": "home",
    "^": "home",
    "$": "end",
    "/": "search",
    "n": "hit",
    "N": "hit_back",
    "s": "refs",
    "\n": "enter",
    "\r": "enter",
    curses.KEY_ENTER: "enter",
    "q": "quit",
    "\x1b": "quit",
}


class Reader:
    def __init__(self, win, text, title):
        self.win = win
        self.text = text
        self.title = title
        self.width = None
        self.lay = None
        self.cur = 0  # word index under the cursor
        self.top = 0  # first visible row
        self.query = ""
        self.msg = ""
        self.refs = None  # word indexes, panel open
        self.sel = 0  # selected reference
        self.ptop = 0  # first visible reference
        self.saved = 0  # cursor before the panel

    # -- layout --

    def sizes(self):
        """(text rows, panel rows) for this screen."""
        h, _ = self.win.getmaxyx()
        body = max(h - 3, 1)
        if self.refs is None:
            return body, 0
        panel = min(len(self.refs) + 1, body * 2 // 5)
        panel = max(panel, min(3, body - 1))
        return max(body - panel, 1), panel

    def follow(self, rows):
        """Scroll so the cursor row is visible."""
        words = self.lay.words
        total = len(self.lay.rows)
        if words:
            r = words[self.cur].row
            off = 1 if rows > 4 else 0
            if r < self.top + off:
                self.top = r - off
            elif r > self.top + rows - 1 - off:
                self.top = r - rows + 1 + off
        self.top = max(0, min(self.top, total - rows))

    # -- drawing --

    def draw(self):
        win = self.win
        h, w = win.getmaxyx()
        if w != self.width:
            self.width = w
            self.lay = layout(self.text, w - 2)
            n = len(self.lay.words)
            self.cur = min(self.cur, max(n - 1, 0))
        rows, panel = self.sizes()
        self.follow(rows)
        words = self.lay.words
        win.erase()

        put(win, 0, 0, f" {self.title}", curses.A_BOLD)
        if words:
            info = (
                f"line {words[self.cur].line + 1}"
                f"/{self.lay.lines} "
            )
            put(win, 0, max(w - len(info) - 1, 0), info)
        put(win, 1, 0, "─" * (w - 1))

        bottom = self.top + rows
        for i, text in enumerate(
            self.lay.rows[self.top : bottom]
        ):
            put(win, 2 + i, 1, text)
        if words:
            key = words[self.cur].key
            lo = first_from(words, self.top)
            for k in range(lo, len(words)):
                wd = words[k]
                if wd.row >= bottom:
                    break
                if wd.row < self.top:
                    continue
                attr = 0
                if k == self.cur:
                    attr = curses.A_REVERSE
                elif (
                    self.refs is not None and wd.key == key
                ):
                    attr = curses.A_UNDERLINE
                if attr:
                    y = 2 + wd.row - self.top
                    put(win, y, 1 + wd.col, wd.text, attr)

        if panel:
            self.draw_panel(2 + rows, panel, w)
        help_ = fit(
            REFS_HELP if self.refs else READ_HELP, w
        )
        put(win, h - 1, 0, self.msg or help_, curses.A_DIM)
        self.msg = ""
        win.refresh()

    def draw_panel(self, y, height, w):
        words = self.lay.words
        word = words[self.saved].text
        n = len(self.refs)
        head = f"─ {word} · {n} place{'s' * (n != 1)} "
        put(self.win, y, 0, head.ljust(w - 1, "─"))
        rows = height - 1
        if self.sel < self.ptop:
            self.ptop = self.sel
        elif self.sel >= self.ptop + rows:
            self.ptop = self.sel - rows + 1
        shown = self.refs[self.ptop : self.ptop + rows]
        for i, k in enumerate(shown):
            wd = words[k]
            num = f"{wd.line + 1:>4}  "
            line = num + self.lay.rows[wd.row]
            yy = y + 1 + i
            if self.ptop + i == self.sel:
                put(
                    self.win,
                    yy,
                    1,
                    line.ljust(w - 2),
                    curses.A_REVERSE,
                )
            else:
                put(self.win, yy, 1, line)
                x = 1 + len(num) + wd.col
                put(
                    self.win,
                    yy,
                    x,
                    wd.text,
                    curses.A_UNDERLINE,
                )

    # -- keys --

    def key_text(self, action):
        """Handle a key while reading. False = leave."""
        words = self.lay.words
        rows, _ = self.sizes()
        total = len(self.lay.rows)
        if action == "quit":
            return False
        if not words:
            step = {"down": 1, "up": -1}.get(action, 0)
            if action == "pgdn":
                step = rows - 1
            elif action == "pgup":
                step = 1 - rows
            self.top = max(
                0, min(self.top + step, total - rows)
            )
            return True
        last = len(words) - 1
        here = words[self.cur]
        if action == "next":
            self.cur = min(self.cur + 1, last)
        elif action == "prev":
            self.cur = max(self.cur - 1, 0)
        elif action in ("down", "up"):
            step = 1 if action == "down" else -1
            self.cur = vertical(words, self.cur, step)
        elif action == "first":
            self.cur = 0
        elif action == "last":
            self.cur = last
        elif action == "home":
            self.cur = first_from(words, here.row)
        elif action == "end":
            nxt = first_from(words, here.row + 1)
            if words[nxt].row > here.row:
                nxt -= 1
            self.cur = nxt
        elif action in ("pgdn", "pgup"):
            step = rows - 1
            if action == "pgup":
                step = -step
            top = max(0, min(self.top + step, total - rows))
            if top == self.top:
                self.cur = last if step > 0 else 0
            else:
                self.top = top
                self.cur = first_from(words, top)
        elif action in ("search", "hit", "hit_back"):
            self.search(action)
        elif action == "refs":
            self.refs = references(words, self.cur)
            self.sel = self.refs.index(self.cur)
            self.ptop = 0
            self.saved = self.cur
        return True

    def search(self, action):
        if action == "search":
            q = prompt(self.win, "/")
            if not q:
                return
            self.query = q
        if not self.query:
            return
        step = -1 if action == "hit_back" else 1
        hit = find(
            self.lay.words, self.query, self.cur, step
        )
        if hit is None:
            self.msg = f"not found: {self.query}"
        else:
            self.cur = hit

    def key_panel(self, action):
        """Handle a key in the references panel."""
        n = len(self.refs)
        _, panel = self.sizes()
        page = max(panel - 2, 1)
        moves = {
            "down": 1,
            "next": 1,
            "up": -1,
            "prev": -1,
            "pgdn": page,
            "pgup": -page,
        }
        if action in moves:
            self.sel += moves[action]
        elif action == "first":
            self.sel = 0
        elif action == "last":
            self.sel = n - 1
        elif action == "enter":
            self.refs = None
            return
        elif action in ("quit", "refs"):
            self.cur = self.saved
            self.refs = None
            return
        self.sel = max(0, min(self.sel, n - 1))
        self.cur = self.refs[self.sel]

    def run(self):
        while True:
            self.draw()
            action = KEYS.get(key(self.win))
            if action is None:
                continue
            if self.refs is not None:
                self.key_panel(action)
            elif not self.key_text(action):
                return


def read_text(path):
    """File contents as text; never raises."""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(
            encoding="utf-8", errors="replace"
        )
    except OSError as e:
        return f"cannot open file: {e}"


def read(win, path, title):
    """Open path in the reader until q."""
    Reader(win, read_text(path), title).run()
