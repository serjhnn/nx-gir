"""Interactive reader: word cursor and references.

The top half is the text model (no curses, tested in
tests/test_reader.py). The bottom half draws it.
"""

import curses
import re
import textwrap
from bisect import bisect_left, bisect_right
from typing import NamedTuple

from nxgir_ui import (
    THEME_NAMES,
    THEMES,
    fit,
    key,
    prompt,
    put,
    style,
)

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
    lcol: int  # column in that line


class Layout(NamedTuple):
    rows: list  # wrapped rows of text
    words: list  # every Word, in reading order
    lines: list  # lines of the file


def layout(text, width):
    """Wrap text to width and find every word."""
    width = max(width, 10)
    lines = text.splitlines()
    rows, words = [], []
    for n, line in enumerate(lines):
        # wrapping never splits words, so the words of
        # the line come out of the rows in the same order
        lcols = [m.start() for m in WORD_RE.finditer(line)]
        parts = textwrap.wrap(
            line,
            width,
            break_long_words=False,
            break_on_hyphens=False,
        )
        k = 0
        for part in parts or [""]:
            r = len(rows)
            rows.append(part)
            for m in WORD_RE.finditer(part):
                t = m.group()
                words.append(
                    Word(
                        r,
                        m.start(),
                        t,
                        normalize(t),
                        n,
                        lcols[k],
                    )
                )
                k += 1
    return Layout(rows, words, lines)


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


def vertical(words, i, step, indent=None):
    """Word on the next (step=1) or previous (-1) row
    that has words, nearest to the current column.

    indent(row) is where that row starts on screen
    (rows move when lines are centered).
    """
    if indent is None:

        def indent(row):
            return 0

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

    x = indent(here.row) + here.col

    def dist(k):
        w = words[k]
        start = indent(w.row) + w.col
        end = start + len(w.text) - 1
        return max(0, start - x, x - end)

    return min(range(lo, hi), key=dist)


def first_from(words, row):
    """First word on row or after it."""
    rows = [w.row for w in words]
    return min(bisect_left(rows, row), len(words) - 1)


TEXT_MAX = 70  # widest text column, for easy reading
ALIGNS = ("center", "left")


def text_width(box_w):
    """Width to wrap the text to inside a box."""
    return max(min(box_w - 2, TEXT_MAX), 10)


def row_x(box_w, row_len, align):
    """Screen column (in the box) where a row starts.

    The text column is centered in the box; with
    align "center" each row is also centered in it.
    """
    cw = text_width(box_w)
    left = max((box_w - cw) // 2, 1)
    if align == "center":
        return left + max((cw - row_len) // 2, 0)
    return left


def snippet(text, col, n, width):
    """Cut text to width, keeping text[col:col+n] in view.

    Returns (piece, column of the word in piece). Cut
    ends are marked with ….
    """
    if len(text) <= width:
        return text, col
    if n >= width - 2:
        return text[col : col + width], 0
    start = col - (width - n) // 2
    start = max(0, min(start, len(text) - width))
    piece = list(text[start : start + width])
    if start > 0:
        piece[0] = "…"
    if start + width < len(text):
        piece[-1] = "…"
    return "".join(piece), col - start


SIDE_MIN = 90  # auto: panel beside text from this width
MIN_TEXT = 30  # narrowest text column beside a panel
MODES = ("auto", "below", "side")


class Box(NamedTuple):
    y: int
    x: int
    h: int
    w: int


def split(h, w, mode, want):
    """Place the text and the panel on an h x w screen.

    Row 0 is the title, row 1 a rule, the last row help.
    want is the number of rows the panel could fill
    (0 = no panel). Returns (text, panel, side), where
    panel is None without a panel.
    """
    body = max(h - 3, 1)
    if not want:
        return Box(2, 0, body, w), None, False
    pw = max(30, min(w * 2 // 5, 50))
    fits = w - pw - 1 >= MIN_TEXT
    side = fits and (
        mode == "side" or (mode == "auto" and w >= SIDE_MIN)
    )
    if side:
        tw = w - pw - 1  # one column for the │ line
        text = Box(2, 0, body, tw)
        return text, Box(2, tw + 1, body, pw), True
    ph = min(want, max(body // 2, 3), body - 1)
    if ph < 2:
        return Box(2, 0, body, w), None, False
    th = body - ph
    return Box(2, 0, th, w), Box(2 + th, 0, ph, w), False


# ---- screen -------------------------------------------

READ_HELP = (
    "w/b word · j/k line · s refs · / find · q back",
    "w/b word · j/k line · s refs · q back",
    "w/b j/k s / q",
)
THEME_HELP = (
    "j/k try · Enter keep · q cancel",
    "j/k Enter q",
)
PANEL_HELP = (
    "j/k pick · Enter go · p place · q close",
    "j/k pick · Enter go · q close",
    "j/k Enter p q",
)
PANEL_HELPS = {"refs": PANEL_HELP, "theme": THEME_HELP}
ALIGN_NAMES = {
    "center": "text: lines centered",
    "left": "text: lines left-aligned",
}
MODE_NAMES = {
    "auto": f"panel: auto (beside from {SIDE_MIN} columns)",
    "below": "panel: always below",
    "side": "panel: always beside (if it fits)",
}

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
    "p": "place",
    "c": "align",
    "T": "theme",
    "d": "dim",
    "\n": "enter",
    "\r": "enter",
    curses.KEY_ENTER: "enter",
    "q": "quit",
    "\x1b": "quit",
}


class Entry(NamedTuple):
    """One panel row: label, then text with a word
    (text[col:col+n]) kept in view and underlined."""

    label: str
    text: str
    col: int = 0
    n: int = 0
    target: int = -1  # word index to jump to, or -1


class Panel:
    """Information shown beside or below the text.

    Opened by a key: s (references) or T (themes);
    t and e later. kind says which.
    """

    def __init__(self, title, entries, sel=0, kind="refs"):
        self.kind = kind
        self.title = title
        self.entries = entries
        self.sel = sel  # selected entry
        self.top = 0  # first visible entry


def theme_panel():
    """Panel listing the themes, current one selected."""
    names = list(THEMES)
    entries = [
        Entry(f"{n:>2} ", THEME_NAMES[name])
        for n, name in enumerate(names, start=1)
    ]
    sel = names.index(style.name)
    return Panel("themes", entries, sel, kind="theme")


def refs_panel(lay, i):
    """Panel listing every place word i appears."""
    words = lay.words
    idx = references(words, i)
    entries = [
        Entry(
            f"{words[k].line + 1:>4} ",
            lay.lines[words[k].line],
            words[k].lcol,
            len(words[k].text),
            k,
        )
        for k in idx
    ]
    n = len(idx)
    title = f"{words[i].text} · {n} place{'s' * (n != 1)}"
    return Panel(title, entries, idx.index(i))


class Reader:
    def __init__(self, win, text, title):
        self.win = win
        self.text = text
        self.title = title
        self.wrap = None  # width the text is wrapped to
        self.lay = None
        self.cur = 0  # word index under the cursor
        self.top = 0  # first visible row
        self.query = ""
        self.msg = ""
        self.panel = None  # Panel while one is open
        self.saved = 0  # cursor before the panel
        self.mode = "auto"  # panel place, see MODES
        self.align = "center"  # see ALIGNS
        self.saved_theme = style.name  # before T
        self.box_w = 0  # width of the text box

    # -- layout --

    def boxes(self):
        """(text box, panel box or None, side?)."""
        h, w = self.win.getmaxyx()
        want = 0
        if self.panel:
            want = len(self.panel.entries) + 1
        return split(h, w, self.mode, want)

    def relayout(self, box_w):
        """Wrap the text again if the width changed."""
        width = text_width(box_w)
        if width != self.wrap:
            self.wrap = width
            self.lay = layout(self.text, width)
            n = len(self.lay.words)
            self.cur = min(self.cur, max(n - 1, 0))

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
        tb, pb, side = self.boxes()
        self.box_w = tb.w
        self.relayout(tb.w)
        self.follow(tb.h)
        words = self.lay.words
        win.erase()

        put(win, 0, 0, f" {self.title}", style("title"))
        if words:
            info = (
                f"line {words[self.cur].line + 1}"
                f"/{len(self.lay.lines)} "
            )
            put(win, 0, max(w - len(info) - 1, 0), info)
        put(win, 1, 0, "─" * (w - 1), style("rule"))
        self.draw_text(tb)
        if pb:
            if side:
                put(win, 1, tb.w, "┬", style("rule"))
                for y in range(pb.y, pb.y + pb.h):
                    put(win, y, tb.w, "│", style("rule"))
            self.draw_panel(pb, side)

        help_ = READ_HELP
        if self.panel:
            help_ = PANEL_HELPS[self.panel.kind]
        put(
            win,
            h - 1,
            0,
            self.msg or fit(help_, w),
            style("help"),
        )
        self.msg = ""
        win.refresh()

    def draw_text(self, box):
        win = self.win
        right = box.x + box.w
        bottom = self.top + box.h
        for i, text in enumerate(
            self.lay.rows[self.top : bottom]
        ):
            x = box.x + self.indent(self.top + i)
            put(win, box.y + i, x, text, 0, right)
        words = self.lay.words
        if not words:
            return
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
                attr = style("cursor")
            elif self.refs_open() and wd.key == key:
                attr = style("mark")
            if attr:
                y = box.y + wd.row - self.top
                x = box.x + self.indent(wd.row) + wd.col
                put(win, y, x, wd.text, attr, right)

    def indent(self, row):
        """Where a row of text starts in the text box."""
        n = len(self.lay.rows[row])
        return row_x(self.box_w, n, self.align)

    def refs_open(self):
        return (
            bool(self.panel) and self.panel.kind == "refs"
        )

    def draw_panel(self, box, side):
        win = self.win
        p = self.panel
        right = box.x + box.w
        x = box.x + 1
        if side:
            put(
                win,
                box.y,
                x,
                p.title,
                style("title"),
                right,
            )
        else:
            head = f"─ {p.title} "
            put(
                win,
                box.y,
                box.x,
                head.ljust(box.w, "─"),
                style("title"),
            )
        rows = box.h - 1
        if p.sel < p.top:
            p.top = p.sel
        elif p.sel >= p.top + rows:
            p.top = p.sel - rows + 1
        width = box.w - 2
        for i, e in enumerate(
            p.entries[p.top : p.top + rows]
        ):
            y = box.y + 1 + i
            room = max(width - len(e.label), 1)
            text, col = snippet(e.text, e.col, e.n, room)
            line = e.label + text
            if p.top + i == p.sel:
                attr = style("cursor")
                put(
                    win,
                    y,
                    x,
                    line.ljust(width),
                    attr,
                    right,
                )
            else:
                put(win, y, x, line, 0, right)
                if e.n:
                    wx = x + len(e.label) + col
                    word = text[col : col + e.n]
                    put(
                        win,
                        y,
                        wx,
                        word,
                        style("mark"),
                        right,
                    )

    # -- keys --

    def key_text(self, action):
        """Handle a key while reading. False = leave."""
        words = self.lay.words
        rows = self.boxes()[0].h
        total = len(self.lay.rows)
        if action == "quit":
            return False
        if action == "place":
            self.next_mode()
            return True
        if action == "align":
            self.next_align()
            return True
        if action == "dim":
            self.msg = style.next_dim(self.win)
            return True
        if action == "theme":
            self.panel = theme_panel()
            self.saved_theme = style.name
            return True
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
            self.cur = vertical(
                words, self.cur, step, self.indent
            )
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
            self.panel = refs_panel(self.lay, self.cur)
            self.saved = self.cur
        return True

    def next_align(self):
        i = ALIGNS.index(self.align)
        self.align = ALIGNS[(i + 1) % len(ALIGNS)]
        self.msg = ALIGN_NAMES[self.align]

    def next_mode(self):
        i = MODES.index(self.mode)
        self.mode = MODES[(i + 1) % len(MODES)]
        self.msg = MODE_NAMES[self.mode]

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
        """Handle a key while a panel is open."""
        p = self.panel
        n = len(p.entries)
        pb = self.boxes()[1]
        page = max(pb.h - 2, 1) if pb else 1
        moves = {
            "down": 1,
            "next": 1,
            "up": -1,
            "prev": -1,
            "pgdn": page,
            "pgup": -page,
        }
        if action in moves:
            p.sel += moves[action]
        elif action == "first":
            p.sel = 0
        elif action == "last":
            p.sel = n - 1
        elif action == "place":
            self.next_mode()
        elif action == "align":
            self.next_align()
        elif action == "dim":
            self.msg = style.next_dim(self.win)
            return
        elif action == "enter":
            self.panel = None
            if p.kind == "theme":
                self.msg = style.describe()
            return
        elif action in ("quit", "refs", "theme"):
            if p.kind == "theme":
                style.use(self.win, self.saved_theme)
            else:
                self.cur = self.saved
            self.panel = None
            return
        p.sel = max(0, min(p.sel, n - 1))
        if p.kind == "theme":
            # try the selected theme on the page
            name = list(THEMES)[p.sel]
            if not style.use(self.win, name):
                self.msg = (
                    "colors need a 256-color terminal"
                )
            return
        target = p.entries[p.sel].target
        if target >= 0:
            self.cur = target

    def run(self):
        while True:
            self.draw()
            action = KEYS.get(key(self.win))
            if action is None:
                continue
            if self.panel is not None:
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
