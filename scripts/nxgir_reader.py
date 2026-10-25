"""Interactive reader: word cursor and references.

The top half is the text model (no curses, tested in
tests/test_reader.py). The bottom half draws it.
"""

import curses
import re
import textwrap
from bisect import bisect_left, bisect_right
from typing import NamedTuple

import nxgir_grabar as grabar
from nxgir_ui import (
    THEME_NAMES,
    THEMES,
    confirm,
    help_line,
    key,
    prompt,
    put,
    shorten,
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


def pos_of(words, i):
    """Saved position of word i: [line, n], the n-th
    word of its line in the file."""
    line = words[i].line
    n = 0
    while i - n - 1 >= 0 and words[i - n - 1].line == line:
        n += 1
    return [line, n]


def word_at(words, pos):
    """Index of the word at a saved [line, n]. If the
    file changed, the nearest word that still exists."""
    if not words:
        return 0
    line, n = pos
    lines = [w.line for w in words]
    lo = bisect_left(lines, line)
    if lo == len(words):
        return len(words) - 1
    if words[lo].line != line:
        return lo  # line gone or empty: next word
    hi = bisect_right(lines, line)
    return min(lo + max(n, 0), hi - 1)


# the end of a sentence: the full stop ։ (: is often
# typed for it); in Grabar . is a middle stop
SENTENCE_END = "։:"


def sentence_starts(lay):
    """Index of the first word of every sentence.

    A sentence ends at ։, and at a line with no words
    (an empty line after a heading); it may run over
    several lines. Word indexes do not depend on the
    width, so neither do these.
    """
    words, lines = lay.words, lay.lines
    out = []
    for i, w in enumerate(words):
        if i == 0:
            out.append(0)
            continue
        p = words[i - 1]
        end = p.lcol + len(p.text)
        if w.line == p.line:
            gap = lines[w.line][end : w.lcol]
        elif w.line - p.line > 1:
            out.append(i)
            continue
        else:
            gap = (
                lines[p.line][end:]
                + lines[w.line][: w.lcol]
            )
        if any(c in gap for c in SENTENCE_END):
            out.append(i)
    return out


def sentence_of(starts, i, n):
    """(first, last + 1): the words of the sentence
    with word i, of n words."""
    k = bisect_right(starts, i) - 1
    hi = starts[k + 1] if k + 1 < len(starts) else n
    return starts[k], hi


def sentence_text(lay, lo, hi):
    """The text of words lo..hi-1, lines joined."""
    a, b = lay.words[lo], lay.words[hi - 1]
    parts = []
    for n in range(a.line, b.line + 1):
        line = lay.lines[n]
        start = a.lcol if n == a.line else 0
        end = b.lcol + len(b.text) if n == b.line else None
        parts.append(line[start:end].strip())
    return " ".join(p for p in parts if p)


def quote(text, width=50):
    """The start of text, cut at a space with …"""
    if len(text) <= width:
        return text
    cut = text[: width - 1]
    if " " in cut:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,.") + "…"


def note_start(lay, starts, note):
    """First word of the sentence a note belongs to.

    Found by its saved position; if the book changed
    and that sentence no longer starts with the note's
    quote, the sentence that does (else the one at
    the position)."""
    words = lay.words
    n = len(words)
    i = word_at(words, note["pos"])
    lo, hi = sentence_of(starts, i, n)
    stem = note.get("quote", "").removesuffix("…")
    if sentence_text(lay, lo, hi).startswith(stem):
        return lo
    ends = starts[1:] + [n]
    for s, e in zip(starts, ends):
        if sentence_text(lay, s, e).startswith(stem):
            return s
    return lo


def first_from(words, row):
    """First word on row or after it."""
    rows = [w.row for w in words]
    return min(bisect_left(rows, row), len(words) - 1)


TEXT_MAX = 70  # widest text column, for easy reading
# empty space left and right of the text, as a part
# of the width, in the order z steps through them
# (first = default)
MARGINS = (0.10, 0.15, 0.20, 0.05, 0.0)
MARGIN_NAMES = {
    0.10: "margins: normal",
    0.15: "margins: wide",
    0.20: "margins: widest",
    0.05: "margins: narrow",
    0.0: "margins: none",
}
ALIGNS = ("center", "left")
# empty screen rows between lines of text, in the
# order L steps through them (first = default)
SPACINGS = (1, 2, 0)
SPACING_NAMES = {
    0: "line spacing: single",
    1: "line spacing: double",
    2: "line spacing: triple",
}


def visible_rows(height, gap):
    """Text rows that fit in height screen rows when
    each is followed by gap empty rows (the last
    row's gap may be cut off)."""
    return max((height + gap) // (gap + 1), 1)


def margin(box_w, size=MARGINS[0]):
    """Columns kept empty at each side of the text."""
    return max(round(box_w * size), 1)


def text_max(size=MARGINS[0]):
    """Widest text column: TEXT_MAX at the default
    margins, narrower with wider margins and wider
    with narrower ones, so z shows on wide screens."""
    part = (1 - 2 * size) / (1 - 2 * MARGINS[0])
    return round(TEXT_MAX * part)


def text_width(box_w, size=MARGINS[0]):
    """Width to wrap the text to inside a box."""
    room = box_w - 2 * margin(box_w, size)
    return max(min(room, text_max(size)), 10)


def row_x(box_w, row_len, align, size=MARGINS[0]):
    """Screen column (in the box) where a row starts.

    The text column is centered in the box, with at
    least margin() free on each side; with align
    "center" each row is also centered in it.
    """
    cw = text_width(box_w, size)
    left = max((box_w - cw) // 2, margin(box_w, size))
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

# help lines: (keys, what, priority), in the order
# shown; help_line() shows as many as fit, lowest
# priority number first (0 = always)
LOOKS = (
    ("z", "margins", 2),
    ("L", "spacing", 2),
    ("c", "align", 2),
)
READ_HELP = (
    ("w/b", "word", 0),
    ("j/k", "line", 0),
    ("s", "refs", 0),
    ("a", "meaning", 2),
    ("A", "hy meaning", 2),
    ("/", "find", 1),
    ("z", "margins", 3),
    ("L", "spacing", 3),
    ("c", "align", 3),
    ("m", "mark", 4),
    ("M", "marks", 4),
    ("o/O", "notes", 4),
    ("T", "theme", 4),
    ("d", "dim", 4),
    ("p", "place", 5),
    ("q", "back", 0),
)
THEME_HELP = (
    ("j/k", "try", 0),
    ("Enter", "keep", 0),
    ("q", "cancel", 0),
)
PANEL_HELP = (
    ("j/k", "pick", 0),
    ("Enter", "go", 0),
    ("p", "place", 1),
    *LOOKS,
    ("q", "close", 0),
)
MARKS_HELP = (
    ("j/k", "pick", 0),
    ("Enter", "go", 0),
    ("x", "delete", 0),
    ("p", "place", 1),
    *LOOKS,
    ("q", "close", 0),
)
NOTES_HELP = (
    ("j/k", "pick", 0),
    ("Enter", "go", 0),
    ("e", "edit", 1),
    ("x", "delete", 0),
    ("p", "place", 1),
    *LOOKS,
    ("q", "close", 0),
)
ABBR_HELP = (
    ("j/k", "scroll", 0),
    ("a/A", "en/hy", 1),
    ("p", "place", 1),
    *LOOKS,
    ("q", "close", 0),
)
PANEL_HELPS = {
    "refs": PANEL_HELP,
    "abbr": ABBR_HELP,
    "theme": THEME_HELP,
    "marks": MARKS_HELP,
    "notes": NOTES_HELP,
}
# the language of the meaning a key shows
LANGS = {"abbr": "en", "abbr_hy": "hy"}
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
    "a": "abbr",
    "A": "abbr_hy",
    "p": "place",
    "c": "align",
    "L": "spacing",
    "z": "margin",
    "T": "theme",
    "d": "dim",
    "m": "mark",
    "M": "marks",
    "x": "delete",
    "o": "notes",
    "O": "note_add",
    "e": "edit",
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
    item: int = -1  # the note of a notes panel row


class Panel:
    """Information shown beside or below the text.

    Opened by a key: s (references), a or A
    (abbreviation or meaning, in English or
    Armenian), T (themes), M (bookmarks) or o
    (notes); t and e later. kind says which.
    A panel of text has its lines in text; they are
    wrapped to the panel's width when drawn. A panel
    with build makes its entries for a width with
    build(width).
    """

    def __init__(self, title, entries, sel=0, kind="refs"):
        self.kind = kind
        self.lang = "en"  # of a meaning panel
        self.title = title
        self.entries = entries
        self.sel = sel  # selected entry
        self.top = 0  # first visible entry
        self.text = None  # lines to wrap, or None
        self.build = None  # entries for a width, or None
        self.wrapped = 0  # width they are wrapped to

    def wrap(self, width):
        """Wrap text to width, if it is not yet."""
        if self.wrapped == width:
            return
        if self.build:
            item = self.entries[self.sel].item
            self.entries = self.build(width)
            self.wrapped = width
            self.sel = self.first(item)
            return
        if self.text is None:
            return
        lines = wrap_lines(self.text, width)
        self.entries = [Entry("", x) for x in lines]
        self.wrapped = width
        self.sel = min(self.sel, len(lines) - 1)

    def first(self, item):
        """First entry of a note (rows of one note share
        an item)."""
        for k, e in enumerate(self.entries):
            if e.item == item:
                return k
        return 0

    def rows_of(self, k):
        """(first, last + 1) entries of entry k's note."""
        item = self.entries[k].item
        if item < 0:
            return k, k + 1
        lo = self.first(item)
        hi = lo
        while (
            hi < len(self.entries)
            and self.entries[hi].item == item
        ):
            hi += 1
        return lo, hi

    def step(self, n):
        """Move the selection n rows, or n notes in a
        notes panel."""
        if self.build is None:
            self.sel += n
            return
        for _ in range(abs(n)):
            lo, hi = self.rows_of(self.sel)
            if n > 0 and hi < len(self.entries):
                self.sel = hi
            elif n < 0 and lo > 0:
                self.sel = self.rows_of(lo - 1)[0]


def theme_panel():
    """Panel listing the themes, current one selected."""
    names = list(THEMES)
    entries = [
        Entry(f"{n:>2} ", THEME_NAMES[name])
        for n, name in enumerate(names, start=1)
    ]
    sel = names.index(style.name)
    return Panel("themes", entries, sel, kind="theme")


def marks_panel(lay, marks, cur):
    """Panel listing bookmarks ([line, n] each); the
    one at or before word cur is selected."""
    words = lay.words
    idx = [word_at(words, m) for m in marks]
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
    sel = 0
    for n, k in enumerate(idx):
        if k <= cur:
            sel = n
    n = len(idx)
    title = f"bookmarks · {n}"
    return Panel(title, entries, sel, kind="marks")


def notes_panel(lay, starts, notes, cur, width=40):
    """Panel listing the notes of a book: for each, the
    line and its sentence, then the note. The last
    note at or before word cur is selected."""
    words = lay.words
    n = len(words)
    at = [note_start(lay, starts, x) for x in notes]

    def build(width):
        out = []
        for k, (note, s) in enumerate(zip(notes, at)):
            lo, hi = sentence_of(starts, s, n)
            label = f"{words[s].line + 1:>4} "
            text = sentence_text(lay, lo, hi)
            out.append(Entry(label, text, 0, 0, s, k))
            for t in textwrap.wrap(
                note["text"], max(width - 5, 8)
            ) or [""]:
                out.append(Entry("     ", t, 0, 0, s, k))
        return out

    here = sentence_of(starts, cur, n)[0] if n else 0
    item = 0
    for k, s in enumerate(at):
        if s <= here:
            item = k
    title = f"notes · {len(notes)}"
    p = Panel(title, build(width), kind="notes")
    p.build = build
    p.wrapped = width
    p.sel = p.first(item)
    return p


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


def wrap_lines(lines, width):
    """lines cut at spaces to fit width; the rest of
    a line keeps its indent, two more."""
    out = []
    for line in lines:
        body = line.lstrip(" ")
        pad = " " * (len(line) - len(body) + 2)
        out += textwrap.wrap(
            line,
            max(width, 8),
            subsequent_indent=pad,
            break_on_hyphens=False,
        ) or [""]
    return out


def abbr_panel(word, table=None, vocab=None, lang="en"):
    """Panel with what word may abbreviate or, if it
    is no abbreviation, what it means in English or
    (lang "hy") Armenian; None if it is in no list.
    With no Armenian meaning, the English one."""
    lines = grabar.explain(word, table)
    if not lines:
        lines = grabar.define(word, vocab, lang)
    if not lines and lang == "hy":
        en = grabar.define(word)
        if en:
            lines = ["no Armenian meaning; English:", *en]
    if not lines:
        return None
    entries = [Entry("", line) for line in lines]
    title = word if lang == "en" else f"{word} · hy"
    p = Panel(title, entries, kind="abbr")
    p.lang = lang
    p.text = lines
    return p


class Reader:
    def __init__(self, win, text, title, state=None):
        self.win = win
        self.text = text
        self.title = title
        self.state = state  # nxgir_state.State or None
        self.start = None  # saved [line, n] to open at
        if state:
            self.start = state.position(title)
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
        self.spacing = SPACINGS[0]  # empty rows per line
        self.margin = MARGINS[0]  # see MARGINS
        if state:
            st = state.settings
            if st.get("mode") in MODES:
                self.mode = st["mode"]
            if st.get("align") in ALIGNS:
                self.align = st["align"]
            if st.get("spacing") in SPACINGS:
                self.spacing = st["spacing"]
            if st.get("margin") in MARGINS:
                self.margin = st["margin"]
        self.saved_theme = style.name  # before T
        self.box_w = 0  # width of the text box
        self.starts = None  # see sentence_starts()
        self.noted = set()  # sentences with notes
        self.adding = None  # sentence getting a note

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
        width = text_width(box_w, self.margin)
        if width != self.wrap:
            self.wrap = width
            self.lay = layout(self.text, width)
            n = len(self.lay.words)
            if self.start is not None:
                self.cur = word_at(
                    self.lay.words, self.start
                )
                self.start = None
            self.cur = min(self.cur, max(n - 1, 0))
            if self.starts is None:
                self.starts = sentence_starts(self.lay)
                self.load_notes()

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
        self.follow(self.rows(tb))
        words = self.lay.words
        win.erase()

        if words:
            star = "* " if self.marked() else ""
            if self.sentence()[0] in self.noted:
                star = "• " + star
            info = (
                f"{star}line {words[self.cur].line + 1}"
                f"/{len(self.lay.lines)} "
            )
            put(win, 0, max(w - len(info) - 1, 0), info)
        room = w - len(info) - 3 if words else w - 2
        title = shorten(self.title, room)
        put(win, 0, 0, f" {title}", style("title"))
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
            self.msg or help_line(help_, w),
            style("help"),
        )
        self.msg = ""
        win.refresh()

    def rows(self, box):
        """Text rows that fit in the text box."""
        return visible_rows(box.h, self.spacing)

    def draw_text(self, box):
        win = self.win
        right = box.x + box.w
        step = self.spacing + 1  # screen rows per line
        bottom = self.top + self.rows(box)
        for i, text in enumerate(
            self.lay.rows[self.top : bottom]
        ):
            x = box.x + self.indent(self.top + i)
            put(win, box.y + i * step, x, text, 0, right)
        words = self.lay.words
        if not words:
            return
        for k in self.noted:
            row = words[k].row
            if self.top <= row < bottom:
                y = box.y + (row - self.top) * step
                x = box.x + max(self.indent(row) - 2, 0)
                put(win, y, x, "•", style("mark"), right)
        key = words[self.cur].key
        lit = self.lit()
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
            elif lit[0] <= k < lit[1]:
                attr = style("mark")
            if attr:
                y = box.y + (wd.row - self.top) * step
                x = box.x + self.indent(wd.row) + wd.col
                put(win, y, x, wd.text, attr, right)

    def indent(self, row):
        """Where a row of text starts in the text box."""
        n = len(self.lay.rows[row])
        return row_x(self.box_w, n, self.align, self.margin)

    def sentence(self, i=None):
        """(first, last + 1) words of the sentence with
        word i (default: the cursor)."""
        i = self.cur if i is None else i
        return sentence_of(
            self.starts, i, len(self.lay.words)
        )

    def lit(self):
        """Words to underline as one sentence: the one
        getting a note, or the selected note's."""
        if self.adding:
            return self.adding
        p = self.panel
        if p and p.kind == "notes":
            return self.sentence(p.entries[p.sel].target)
        return 0, 0

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
        p.wrap(box.w - 2)
        # all rows of the selected note are shown
        lo, hi = p.rows_of(p.sel)
        if lo < p.top:
            p.top = lo
        elif hi > p.top + rows:
            p.top = min(lo, hi - rows)
        width = box.w - 2
        for i, e in enumerate(
            p.entries[p.top : p.top + rows]
        ):
            y = box.y + 1 + i
            room = max(width - len(e.label), 1)
            text, col = snippet(e.text, e.col, e.n, room)
            line = e.label + text
            if lo <= p.top + i < hi:
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
        rows = self.rows(self.boxes()[0])
        total = len(self.lay.rows)
        if action == "quit":
            self.remember()
            return False
        if action == "mark":
            self.toggle_mark()
            return True
        if action == "marks":
            self.open_marks()
            return True
        if action == "notes":
            self.open_notes()
            return True
        if action == "note_add":
            self.add_note()
            return True
        if action == "place":
            self.next_mode()
            return True
        if action == "align":
            self.next_align()
            return True
        if action == "spacing":
            self.next_spacing()
            return True
        if action == "margin":
            self.next_margin()
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
        elif action in ("abbr", "abbr_hy"):
            self.saved = self.cur
            self.open_abbr(LANGS[action])
        return True

    def next_spacing(self):
        i = SPACINGS.index(self.spacing)
        self.spacing = SPACINGS[(i + 1) % len(SPACINGS)]
        self.msg = SPACING_NAMES[self.spacing]

    def next_margin(self):
        i = MARGINS.index(self.margin)
        self.margin = MARGINS[(i + 1) % len(MARGINS)]
        self.msg = MARGIN_NAMES[self.margin]

    def next_align(self):
        i = ALIGNS.index(self.align)
        self.align = ALIGNS[(i + 1) % len(ALIGNS)]
        self.msg = ALIGN_NAMES[self.align]

    def next_mode(self):
        i = MODES.index(self.mode)
        self.mode = MODES[(i + 1) % len(MODES)]
        self.msg = MODE_NAMES[self.mode]

    def open_abbr(self, lang):
        """Meaning panel for the word at self.saved."""
        word = self.lay.words[self.saved].text
        self.panel = abbr_panel(word, lang=lang)
        if not self.panel:
            self.msg = f"not found: {word}"

    def search(self, action):
        if action == "search":
            q = prompt(self.win, "/", redraw=self.draw)
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
            p.step(moves[action])
        elif action == "first":
            p.sel = 0
        elif action == "last":
            p.sel = p.rows_of(n - 1)[0]
        elif action == "place":
            self.next_mode()
        elif action == "align":
            self.next_align()
        elif action == "spacing":
            self.next_spacing()
        elif action == "margin":
            self.next_margin()
        elif action == "dim":
            self.msg = style.next_dim(self.win)
            return
        elif action == "delete" and p.kind == "marks":
            self.delete_mark()
            return
        elif action == "delete" and p.kind == "notes":
            self.delete_note()
            return
        elif action == "edit" and p.kind == "notes":
            self.edit_note()
            return
        elif (
            p.kind == "abbr"
            and action in LANGS
            and LANGS[action] != p.lang
        ):
            # the same word in the other language
            self.open_abbr(LANGS[action])
            if not self.panel:
                self.panel = p
            return
        elif action == "enter":
            self.panel = None
            if p.kind == "theme":
                self.msg = style.describe()
            return
        elif action in (
            "quit",
            "refs",
            "abbr",
            "abbr_hy",
            "theme",
            "marks",
            "notes",
        ):
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

    # -- saved state --

    def remember(self):
        """Save position and settings (if saving)."""
        st = self.state
        if not st or not self.lay:
            return
        words = self.lay.words
        if words:
            pos = pos_of(words, self.cur)
            st.set_position(
                self.title, pos, len(self.lay.lines)
            )
        st.settings.update(
            mode=self.mode,
            align=self.align,
            spacing=self.spacing,
            margin=self.margin,
            theme=style.wanted,
            dim=style.dim,
        )
        st.save()

    def marked(self):
        """True if the word under the cursor is
        bookmarked."""
        if not self.state:
            return False
        pos = pos_of(self.lay.words, self.cur)
        return pos in self.state.marks(self.title)

    def toggle_mark(self):
        words = self.lay.words
        if not self.state or not words:
            return
        pos = pos_of(words, self.cur)
        added = self.state.toggle_mark(self.title, pos)
        self.state.save()
        word = words[self.cur].text
        what = "added" if added else "removed"
        self.msg = (
            f"bookmark {what} · {word}, line {pos[0] + 1}"
        )

    def open_marks(self):
        marks = (
            self.state.marks(self.title)
            if self.state
            else []
        )
        if not marks:
            self.msg = "no bookmarks yet · m adds one"
            return
        self.panel = marks_panel(self.lay, marks, self.cur)
        self.saved = self.cur
        self.cur = self.panel.entries[self.panel.sel].target

    def delete_mark(self):
        p = self.panel
        marks = self.state.marks(self.title)
        self.state.toggle_mark(self.title, marks[p.sel])
        self.state.save()
        marks = self.state.marks(self.title)
        if not marks:
            self.cur = self.saved
            self.panel = None
            self.msg = "bookmark deleted · none left"
            return
        sel = min(p.sel, len(marks) - 1)
        self.panel = marks_panel(self.lay, marks, self.cur)
        self.panel.sel = sel
        self.cur = self.panel.entries[sel].target
        self.msg = "bookmark deleted"

    # -- notes --

    def notes(self):
        if not self.state:
            return []
        return self.state.notes(self.title)

    def load_notes(self):
        """Find the sentences that have notes."""
        self.noted = {
            note_start(self.lay, self.starts, x)
            for x in self.notes()
        }

    def add_note(self):
        words = self.lay.words
        if not self.state or not words:
            self.msg = "notes need a saved state"
            return
        lo, hi = self.sentence()
        self.adding = (lo, hi)
        self.draw()
        text = prompt(self.win, "note: ", redraw=self.draw)
        self.adding = None
        text = (text or "").strip()
        if not text:
            self.msg = "no note added"
            return
        q = quote(sentence_text(self.lay, lo, hi))
        pos = pos_of(words, lo)
        self.state.add_note(self.title, pos, q, text)
        self.state.save()
        self.load_notes()
        self.msg = f"note added · line {pos[0] + 1}"

    def show_notes(self, item=None):
        """Open (or rebuild) the notes panel; None if
        there are no notes."""
        notes = self.notes()
        if not notes:
            return None
        pb = self.boxes()[1]
        width = pb.w - 2 if pb else 40
        p = notes_panel(
            self.lay, self.starts, notes, self.cur, width
        )
        if item is not None:
            p.sel = p.first(min(item, len(notes) - 1))
        self.panel = p
        self.cur = p.entries[p.sel].target
        return p

    def open_notes(self):
        self.saved = self.cur
        if not self.show_notes():
            self.msg = "no notes yet · O adds one"

    def edit_note(self):
        p = self.panel
        item = p.entries[p.sel].item
        old = self.notes()[item]["text"]
        text = prompt(self.win, "note: ", old, self.draw)
        text = (text or "").strip()
        if not text or text == old:
            self.msg = "note not changed"
            return
        self.state.edit_note(self.title, item, text)
        self.state.save()
        self.show_notes(item)
        self.msg = "note changed"

    def delete_note(self):
        p = self.panel
        item = p.entries[p.sel].item
        if not confirm(
            self.win, "delete this note?", self.draw
        ):
            self.msg = "note kept"
            return
        self.state.delete_note(self.title, item)
        self.state.save()
        self.load_notes()
        if not self.show_notes(item):
            self.cur = self.saved
            self.panel = None
            self.msg = "note deleted · none left"
            return
        self.msg = "note deleted"

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


def read(win, path, title, state=None):
    """Open path in the reader until q. With a State,
    the position, bookmarks and settings are saved."""
    Reader(win, read_text(path), title, state).run()
