"""Local web reader: `nxgir web`.

A small HTTP server (standard library only) for the
web pages in web/ and a JSON API over the same books,
Grabar helpers and saved state as the terminal reader.

The API is plain functions over an App (tested in
tests/test_web.py); Handler only moves bytes.

  GET  /api/shelf?folder=      one folder of the shelf
  GET  /api/book?name=         a book, cut into words
  GET  /api/word?w=&lang=      abbreviation + meaning
  GET  /api/timeline           the main steps
  GET  /api/blog               the blog posts
  GET  /api/features           what the site can do
  GET  /api/recent?n=          the books read last
  GET  /api/stats              how close to the limits
  GET  /api/library            the Grabar books
  GET  /api/volume?folder=     a book's page: its parts
  POST /api/position           {name, pos, lines}
  POST /api/mark               {name, pos}
  POST /api/forget             {name}: off the list
  POST /api/note               {name, pos, text}
  GET  /api/source?name=       an interpretation as is
  POST /api/save               {name, text, version}
  POST /api/new                {lang, file, text}
                               {name, i, text}
                               {name, i, delete: true}

It is meant for this computer only: it listens on
127.0.0.1, answers only to a local Host name, and
writes only for JSON requests (which a web page from
another site cannot send without asking first). The
only files it changes are the texts in
interpretations/.
"""

import hashlib
import json
import mimetypes
import os
import re
import subprocess
import sys
import tempfile
from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer,
)
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import nxgir_blog as blog_posts
import nxgir_features as feature_list
import nxgir_grabar as grabar
import nxgir_limits as lim
import nxgir_timeline as tl
import nxgir_translations as tr
from nxgir_browse import (
    folder_count,
    folder_exists,
    folder_items,
)
from nxgir_reader import (
    WORD_RE,
    contents,
    layout,
    markdown_line,
    note_start,
    plain_markdown,
    pos_of,
    quote,
    read_text,
    sentence_of,
    sentence_starts,
    sentence_text,
    word_at,
)
from nxgir_state import State

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
# the Library page: authors and short book names
LIBRARY = ROOT / "books" / "LIBRARY.tsv"
HOST = "127.0.0.1"
PORT = 8088
LOCAL_HOSTS = {"127.0.0.1", "localhost", "[::1]"}
# a request body: room for a long interpretation
MAX_BODY = 1024 * 1024
# languages of interpretations/ (folders ru/, en/,
# hy/)
TEXT_LANGS = ("ru", "en", "hy")
# a new text's file name: passage and title in Latin
# letters, e.g. ps-118-33-37-pustota-i-put
SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
LANGS = ("en", "hy")
# a book and its translation: the same path in the
# other folder, e.g. grabar/bible/x.txt and
# ashkharhabar/bible/x.txt, read side by side
PARALLEL = ("grabar", "ashkharhabar")
# the first line of a part of a long book:
# "title · 2/24" (see fetch-digilib.py)
PART_RE = re.compile(r"^(.+) · (\d+)/(\d+)$")
# left out of the translation status: the Bible and the
# short works of Anania Shirakatsi (all but the
# Աշխարհացոյց, 15-)
SHIRAKATSI = "grabar/anania-shirakatsi/"
NOT_COUNTED = ("grabar/bible/",) + tuple(
    SHIRAKATSI + d + "-"
    for d in ("4", "7", "8", "13", "14", "16", "18")
)
# pages load only their own files: no inline scripts
# or styles, nothing from other sites
CSP = (
    "default-src 'self'; img-src 'self' data:;"
    " frame-ancestors 'none'"
)


class ApiError(Exception):
    """An answer other than 200: status and message."""

    def __init__(self, status, msg):
        super().__init__(msg)
        self.status = status


class App:
    """The books and the state file the API works on.
    files is [(name, size, path)], as shelf_files()
    in nxgir-cli.py gives it."""

    def __init__(
        self,
        files,
        state_path=None,
        notes=None,
        timeline=tl.TIMELINE,
        library=LIBRARY,
        blog=blog_posts.BLOG,
        features=feature_list.FEATURES,
        translations=tr.TRANSLATIONS,
    ):
        self.files = list(files)
        self.paths = {n: p for n, _, p in self.files}
        self.state_path = state_path
        # (folder, shelf prefix) of the texts that
        # can be edited: interpretations/
        self.notes = notes
        # timeline.tsv, or None for no events
        self.timeline = timeline
        # LIBRARY.tsv, or None for no names
        self.library = library
        # blog/, or None for no posts
        self.blog = blog
        # features/, or None for an empty page
        self.features = features
        # TRANSLATIONS.tsv, or None for no credits
        self.translations = translations

    def events(self):
        """The events of the timeline, oldest first,
        their links checked (link_to())."""
        if not self.timeline:
            return []
        out = []
        for e in tl.read(self.timeline):
            e["to"] = link_to(self, e["link"])
            if not e["to"]:
                e["link"] = ""
            out.append(e)
        return out

    def state(self):
        """The state, read fresh: the terminal reader
        may have changed it since the last request."""
        return State.load(self.state_path)

    def path(self, name):
        """Path of a book on the shelf. Only names on
        the shelf are known, so a name can't reach
        other files (no ../)."""
        if name not in self.paths:
            raise ApiError(404, f"no such book: {name}")
        return self.paths[name]

    def parallel(self, name):
        """The other versions of a book on the shelf:
        its path in the other PARALLEL folders."""
        top, _, rest = name.partition("/")
        if top not in PARALLEL or not rest:
            return []
        return [
            f"{other}/{rest}"
            for other in PARALLEL
            if other != top
            and f"{other}/{rest}" in self.paths
        ]

    def editable(self, name):
        """True for a .md text in interpretations/:
        the only files the web reader may change."""
        if not self.notes or name not in self.paths:
            return False
        root, prefix = self.notes
        path = Path(self.paths[name]).resolve()
        return (
            name.startswith(prefix)
            and path.suffix == ".md"
            and path.is_relative_to(Path(root).resolve())
        )

    def in_notes(self, folder):
        """True for interpretations/ or a folder in it,
        where new texts can be made."""
        if not self.notes:
            return False
        top = self.notes[1].rstrip("/")
        return folder == top or folder.startswith(top + "/")

    def resize(self, name):
        """Update a book's size after it was saved."""
        self.files = [
            (
                n,
                Path(p).stat().st_size
                if n == name
                else size,
                p,
            )
            for n, size, p in self.files
        ]

    def add(self, name, path):
        """Put a new text on the shelf, in order."""
        self.paths[name] = path
        self.files.append((name, path.stat().st_size, path))
        prefix = self.notes[1]
        rest = [
            f
            for f in self.files
            if not f[0].startswith(prefix)
        ]
        texts = sorted(
            f for f in self.files if f[0].startswith(prefix)
        )
        self.files = rest + texts


def split_words(line):
    """The line as [gap, word, gap, word, ..., gap]:
    words at odd places, the same words the terminal
    reader steps through (WORD_RE)."""
    parts, end = [], 0
    for m in WORD_RE.finditer(line):
        parts += [line[end : m.start()], m.group()]
        end = m.end()
    parts.append(line[end:])
    return parts


def shelf_crumbs(app, folder):
    """The folders above one, as [{label, folder}], and
    its own label: the names in LIBRARY.tsv under
    grabar/ and ashkharhabar/, else the folder's name."""
    names = read_names(app.library)
    parts = folder.split("/") if folder else []
    labels = []
    for i, part in enumerate(parts):
        key = "/".join(parts[1 : i + 1])
        known = parts[0] in PARALLEL and key in names
        labels.append(names[key] if known else part)
    crumbs = []
    for i in range(len(parts) - 1):
        at = "/".join(parts[: i + 1])
        to = "#/f/" + at
        if parts[0] in PARALLEL and i >= 1:
            # a book's page, or an author's if it is
            # Bible-like
            if i >= 2 or flat_author(
                app, parts[0], parts[1]
            ):
                to = "#/b/" + at
        crumbs.append(
            {"label": labels[i], "folder": at, "to": to}
        )
    return crumbs, labels[-1] if labels else ""


def shelf(app, folder=""):
    """One folder: its sub-folders and books."""
    folder = folder.strip("/")
    if not folder_exists(app.files, folder):
        raise ApiError(404, f"no such folder: {folder}")
    st = app.state()
    items = []
    for item in folder_items(app.files, folder):
        if item.label == "..":
            continue
        row = {
            "label": item.label,
            "name": item.name,
            "folder": item.folder,
            "size": item.size,
        }
        if item.folder:
            row["unit"] = item.unit
        else:
            row["progress"] = st.progress(item.name)
        items.append(row)
    count, unit = folder_count(app.files, folder)
    crumbs, title = shelf_crumbs(app, folder)
    return {
        "folder": folder,
        "title": title,
        "crumbs": crumbs,
        "parent": folder.rpartition("/")[0],
        "count": count,
        "unit": unit,
        "items": items,
        "editable": app.in_notes(folder),
        "status": [] if folder else status(app),
        "news": [] if folder else tl.news(app.events()),
    }


def link_to(app, link):
    """What a timeline link opens: "read" for a book
    on the shelf, "folder" for a folder, "url" for
    an https:// address, "" for nothing (a book left
    out of this shelf, e.g. on the published copy)."""
    if link.startswith("https://"):
        return "url"
    if link in app.paths:
        return "read"
    if link and folder_exists(app.files, link):
        return "folder"
    return ""


def timeline(app):
    """The Timeline page: the events, newest first,
    the plans apart, and counts for its top: the
    Grabar books and the parts translated."""
    events = app.events()
    done = tl.done(events)
    books = 0
    if folder_exists(app.files, PARALLEL[0]):
        books = folder_count(app.files, PARALLEL[0])[0]
    return {
        "start": done[0]["date"] if done else "",
        "books": books,
        "parts": sum(b["done"] for b in status(app)),
        "events": done[::-1],
        "next": events[len(done) :],
    }


def blog(app):
    """The Blog page: the posts, newest first
    (nxgir_blog.py)."""
    if not app.blog:
        return {"posts": []}
    return {"posts": blog_posts.read(app.blog)}


def features(app):
    """The Features page: what the site can do, in
    each language it is written in
    (nxgir_features.py)."""
    if not app.features:
        return {"versions": []}
    return {"versions": feature_list.read(app.features)}


def stats(app, root=lim.ROOT):
    """The Statistics page: how close the repository
    at root is to its limits (nxgir_limits.py). The
    site is not built here: its size and build time
    are the last recorded in notes/limits.tsv."""
    try:
        m = lim.measure(root)
    except (OSError, subprocess.CalledProcessError):
        raise ApiError(500, "cannot measure: no git?")
    return lim.stats(m, lim.history(lim.HISTORY))


def first_line(path):
    """The first line of a file, read alone."""
    with open(path, encoding="utf-8") as f:
        return f.readline().strip()


def status(app):
    """How much of each long book in grabar/ is
    translated: its parts with a translation at the
    same path in the other PARALLEL folders. The
    Bible and short works are left out (NOT_COUNTED),
    and so are
    the books with no part translated. "name" is
    "author • book" from LIBRARY.tsv (or the
    folder and the title)."""
    top = PARALLEL[0] + "/"
    names = read_names(app.library)
    books = {}
    for name, _, path in app.files:
        if not name.startswith(top) or name.startswith(
            NOT_COUNTED
        ):
            continue
        m = PART_RE.match(first_line(path))
        if not m:
            continue
        folder = name.rpartition("/")[0]
        key = folder[len(top) :]
        who = key.partition("/")[0]
        short = names.get(key) or m.group(1)
        b = books.setdefault(
            folder,
            {
                "title": m.group(1),
                "name": names.get(who, who) + " • " + short,
                "folder": folder,
                "parts": int(m.group(3)),
                "done": 0,
                "first": "",
            },
        )
        if app.parallel(name):
            b["done"] += 1
            b["first"] = b["first"] or name
    return [b for b in books.values() if b["done"]]


def read_names(path):
    """LIBRARY.tsv as {path: name}, in its order;
    lines starting with # are comments."""
    names = {}
    if not path:
        return names
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip() or line[0] == "#":
                continue
            key, tab, name = line.partition("\t")
            if not tab or not key or not name.strip():
                raise ValueError(
                    f"{path}:{n}: not path<TAB>name"
                )
            names[key.strip("/")] = name.strip()
    return names


def library(app):
    """The Library page: the books in grabar/ by
    author (the folder under grabar/). A book is a
    folder of parts ("title · n/N") or a single
    file; its name is the short one in LIBRARY.tsv,
    or its title. "done" counts the parts with a
    translation (PARALLEL)."""
    top = PARALLEL[0] + "/"
    names = read_names(app.library)
    authors = {}
    for name, _, path in app.files:
        rest = name[len(top) :]
        if not name.startswith(top) or "/" not in rest:
            continue
        who = rest.partition("/")[0]
        line = first_line(path)
        m = PART_RE.match(line)
        key = rest.rpartition("/")[0] if m else rest
        a = authors.setdefault(
            who,
            {
                "name": names.get(who, who),
                "folder": top + who,
                "books": {},
            },
        )
        title = m.group(1) if m else line
        b = a["books"].setdefault(
            key,
            {
                "name": names.get(key) or title or key,
                "title": title or key,
                "first": name,
                "parts": 0,
                "done": 0,
            },
        )
        b["parts"] += 1
        if app.parallel(name):
            b["done"] += 1
    order = list(names)

    def place(who):
        if who in names:
            return (0, order.index(who), who)
        return (1, 0, who)

    out = []
    for who in sorted(authors, key=place):
        a = authors[who]
        a["books"] = list(a["books"].values())
        out.append(a)
    return {"authors": out}


def flat_author(app, top, who):
    """True if no book of an author is in parts, as in
    the Bible: the author's folder is a page."""
    return not any(
        PART_RE.match(first_line(p))
        for n, _, p in app.files
        if n.startswith(f"{top}/{who}/")
    )


def up_links(app, folder):
    """The links above a book's folder: the Library,
    and its author (a page of its own only when all
    the author's books are single files, as in the
    Bible), as [{label, to}]."""
    top, _, key = folder.partition("/")
    who = key.partition("/")[0]
    up = [{"label": "Գրադարան", "to": "#/library"}]
    if "/" not in key:
        return up
    names = read_names(app.library)
    flat = flat_author(app, top, who)
    to = f"#/b/{top}/{who}" if flat else "#/library"
    up.append({"label": names.get(who, who), "to": to})
    return up


def volume(app, folder):
    """The page of a book: a folder under grabar/ or
    ashkharhabar/ at least two levels deep. {folder,
    book (its short name in LIBRARY.tsv, or its title,
    or the folder's name), title, up (links to the
    Library and the author), total, done (parts with a
    translation), groups}: groups are [{label, parts}],
    one per sub-folder (label "" for the folder's own
    files), each part {name, n, title (its first
    heading, or the book's name for a single file),
    translated, progress, seen}."""
    folder = folder.strip("/")
    top, _, key = folder.partition("/")
    if top not in PARALLEL or not key:
        raise ApiError(404, f"no such book: {folder}")
    prefix = folder + "/"
    mine = [
        (n, p)
        for n, _, p in app.files
        if n.startswith(prefix)
    ]
    if not mine:
        raise ApiError(404, f"no such book: {folder}")
    names = read_names(app.library)
    st = app.state()
    groups = {}
    book_name = ""
    for name, path in mine:
        sub = name[len(prefix) :].rpartition("/")[0]
        line = first_line(path)
        m = PART_RE.match(line)
        if m:
            book_name = book_name or m.group(1)
            heads = [
                x
                for x in contents(
                    book_text(app, name).splitlines()
                )
                if not x.get("start")
            ]
            n = int(m.group(2))
            title = heads[0]["title"] if heads else ""
        else:
            file_key = name.partition("/")[2]
            n = len(groups.get(sub, ())) + 1
            title = names.get(file_key) or line
        row = {
            "name": name,
            "n": n,
            "title": title,
            "translated": bool(app.parallel(name)),
            "progress": st.progress(name),
            "seen": st.books.get(name, {}).get("seen", 0),
        }
        groups.setdefault(sub, []).append(row)
    out = []
    for sub in sorted(groups):
        label = (
            names.get(f"{key}/{sub}", sub) if sub else ""
        )
        rows = sorted(groups[sub], key=lambda r: r["n"])
        out.append({"label": label, "parts": rows})
    rows = [r for g in out for r in g["parts"]]
    up = up_links(app, folder)
    return {
        "folder": folder,
        "book": names.get(key)
        or book_name
        or folder.rpartition("/")[2],
        "title": book_name or names.get(key) or key,
        "up": up,
        "total": len(rows),
        "done": sum(r["translated"] for r in rows),
        "groups": out,
    }


def book_title(app, name):
    """A book's title: its first line, without a
    Markdown heading mark."""
    try:
        line = first_line(app.path(name))
    except OSError:
        line = ""
    return line.lstrip("#").strip() or name


def recent(app, n=0):
    """The books read last, newest first ("seen" is
    when, in seconds): n of them, or all for 0.
    Only books on the shelf."""
    st = app.state()
    items = []
    for name, b in st.books.items():
        if (
            name not in app.paths
            or "pos" not in b
            or st.hidden(name)
        ):
            continue
        items.append(
            {
                "name": name,
                "title": book_title(app, name),
                "progress": st.progress(name),
                "seen": b.get("seen", 0),
            }
        )
    items.sort(key=lambda x: -x["seen"])
    return {"items": items[:n] if n > 0 else items}


def book_text(app, name):
    """The text the reader shows: Markdown marks
    taken out of .md files."""
    path = app.path(name)
    text = read_text(path)
    if path.suffix.lower() == ".md":
        text = plain_markdown(text)
    return text


def book_words(app, name):
    """Layout of a book, unwrapped: its words in the
    same order as split_words() gives them, line by
    line, so a word's index is the same in the page."""
    return layout(book_text(app, name), 10**9)


def places(app, name, st, lay=None):
    """Bookmarks and notes, each with "at": the index
    of its word (of a note: the first word of its
    sentence), as the terminal reader finds them."""
    lay = lay or book_words(app, name)
    words = lay.words
    marks, notes = [], []
    if words:
        starts = sentence_starts(lay)
        marks = [
            {"pos": m, "at": word_at(words, m)}
            for m in st.marks(name)
        ]
        notes = [
            dict(n, at=note_start(lay, starts, n))
            for n in st.notes(name)
        ]
    return {"marks": marks, "notes": notes}


def md_format(app, name):
    """What the Markdown marks of a .md book said, for
    the lines that had any: {line: {"h": heading
    level, "q": a quote, "spans": [[start, end, "b"
    or "i"]]}}, places counted in the shown text."""
    path = app.path(name)
    if path.suffix.lower() != ".md":
        return {}
    out = {}
    for n, line in enumerate(read_text(path).splitlines()):
        m = markdown_line(line)
        if m.heading or m.quote or m.spans:
            out[n] = {
                "h": m.heading,
                "q": m.quote,
                "spans": m.spans,
            }
    return out


def book(app, name):
    """A book's lines, cut into words, with where it
    was left ("at": its word), the first word of every
    sentence, its bookmarks and notes, its contents
    (the chapters and sermons in it), the folders above
    it and its own name (shelf_crumbs()), for a .md
    book its bold, italic, headings and quotes, and
    for one of our translations who made and
    reviewed it and its license (credit), and for
    a part of a long book the parts beside it
    (parts())."""
    text = book_text(app, name)
    lay = layout(text, 10**9)
    st = app.state()
    pos = st.position(name)
    at = None
    if pos and lay.words:
        at = word_at(lay.words, pos)
    crumbs, label = shelf_crumbs(app, name)
    return {
        "name": name,
        "crumbs": crumbs,
        "label": label,
        "lines": [
            split_words(line) for line in text.splitlines()
        ],
        "pos": pos,
        "at": at,
        "starts": sentence_starts(lay),
        "editable": app.editable(name),
        "parallel": app.parallel(name),
        "format": md_format(app, name),
        "contents": contents(text.splitlines()),
        "credit": credit(app, name),
        "parts": parts(app, name),
        **places(app, name, st, lay),
    }


def parts(app, name):
    """For a part of a long book ("title · n/N" on
    its first line): {book (its short name in
    LIBRARY.tsv, or its title), folder, n, total,
    prev, next}, prev and next the parts n-1 and n+1 in
    the same folder as {name, n, title} (title: its
    first heading in contents(), or ""), or None.
    For any other book None."""
    m = PART_RE.match(first_line(app.path(name)))
    if not m:
        return None
    folder = name.rpartition("/")[0]
    by_n = {}
    for other, _, path in app.files:
        if other.rpartition("/")[0] != folder:
            continue
        o = PART_RE.match(first_line(path))
        if o and o.group(1) == m.group(1):
            by_n.setdefault(int(o.group(2)), other)
    n = int(m.group(2))

    def side(k):
        if k not in by_n:
            return None
        lines = book_text(app, by_n[k]).splitlines()
        heads = [
            h for h in contents(lines) if not h.get("start")
        ]
        return {
            "name": by_n[k],
            "n": k,
            "title": heads[0]["title"] if heads else "",
        }

    # its short name in LIBRARY.tsv, for grabar/ and
    # its translations alike
    key = folder.partition("/")[2]
    short = read_names(app.library).get(key)
    return {
        "book": short or m.group(1),
        "folder": folder,
        "up": up_links(app, folder),
        "n": n,
        "total": int(m.group(3)),
        "prev": side(n - 1),
        "next": side(n + 1),
    }


def credit(app, name):
    """Who made and reviewed a translation, and its
    license (nxgir_translations.credit()); None for
    a book not in TRANSLATIONS.tsv."""
    table = tr.read(app.translations)
    return tr.credit(table, name)


def word(w, lang="en"):
    """What a word may stand for and what it means:
    the same lines as the reader's word panel."""
    w = w.strip()
    if not w:
        raise ApiError(400, "no word")
    if lang not in LANGS:
        raise ApiError(400, f"no such language: {lang}")
    return {
        "word": w,
        "abbr": grabar.explain(w),
        "meaning": grabar.define(w, lang=lang),
    }


def pos_arg(body):
    """body["pos"] checked: [line, n], both >= 0."""
    pos = body.get("pos")
    ok = (
        isinstance(pos, list)
        and len(pos) == 2
        and all(type(x) is int and x >= 0 for x in pos)
    )
    if not ok:
        raise ApiError(400, "pos must be [line, n]")
    return pos


def text_arg(body, key):
    t = body.get(key, "")
    if not isinstance(t, str):
        raise ApiError(400, f"{key} must be text")
    return t


def saved(st):
    if not st.save():
        raise ApiError(500, "cannot save the state")


def set_position(app, body):
    name = text_arg(body, "name")
    app.path(name)
    pos = pos_arg(body)
    lines = body.get("lines")
    if type(lines) is not int or lines < 1:
        raise ApiError(400, "lines must be a number")
    st = app.state()
    st.set_position(name, pos, lines)
    saved(st)
    return {"progress": st.progress(name)}


def forget(app, body):
    """Take a book off the list of readings."""
    name = text_arg(body, "name")
    app.path(name)
    st = app.state()
    st.hide(name)
    saved(st)
    return {"ok": True}


def toggle_mark(app, body):
    name = text_arg(body, "name")
    app.path(name)
    pos = pos_arg(body)
    st = app.state()
    added = st.toggle_mark(name, pos)
    saved(st)
    return {"added": added, **places(app, name, st)}


def note(app, body):
    """Add a note to the sentence of the word at
    "pos" (no "i"), or edit or delete note i: the
    i-th of notes()."""
    name = text_arg(body, "name")
    lay = book_words(app, name)
    st = app.state()
    if "i" not in body:
        pos = pos_arg(body)
        text = text_arg(body, "text").strip()
        if not text:
            raise ApiError(400, "empty note")
        words = lay.words
        if not words:
            raise ApiError(400, "no words to note")
        starts = sentence_starts(lay)
        i = word_at(words, pos)
        lo, hi = sentence_of(starts, i, len(words))
        q = quote(sentence_text(lay, lo, hi))
        st.add_note(name, pos_of(words, lo), q, text)
    else:
        i = body["i"]
        n = len(st.notes(name))
        if type(i) is not int or not 0 <= i < n:
            raise ApiError(404, f"no such note: {i}")
        if body.get("delete") is True:
            st.delete_note(name, i)
        else:
            text = text_arg(body, "text").strip()
            if not text:
                raise ApiError(400, "empty note")
            st.edit_note(name, i, text)
    saved(st)
    return places(app, name, st, lay)


# -- editing interpretations --


def version(data):
    """A short fingerprint of a file's bytes: saving
    is refused if the file changed since it was read."""
    return hashlib.sha256(data).hexdigest()[:16]


def write_file(path, text):
    """Write text atomically (a crash leaves the old
    file or the new one, never half of it)."""
    fd, tmp = tempfile.mkstemp(
        dir=path.parent, prefix=".nxgir-"
    )
    try:
        with os.fdopen(
            fd, "w", encoding="utf-8", newline=""
        ) as f:
            f.write(text)
        os.replace(tmp, path)
    except OSError as e:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise ApiError(500, f"cannot save: {e}")


def editable_path(app, name):
    if not app.editable(name):
        raise ApiError(403, f"not editable: {name}")
    return Path(app.path(name))


def source(app, name):
    """The text of an interpretation as it is in the
    file (Markdown marks kept), to edit."""
    path = editable_path(app, name)
    data = path.read_bytes()
    return {
        "name": name,
        "text": data.decode("utf-8", errors="replace"),
        "version": version(data),
    }


def save_text(app, body):
    """Save an edited interpretation exactly as
    given, if the file is still the version that was
    read: {name, text, version}."""
    name = text_arg(body, "name")
    path = editable_path(app, name)
    text = text_arg(body, "text")
    if version(path.read_bytes()) != body.get("version"):
        raise ApiError(
            409,
            "the file changed since it was opened",
        )
    write_file(path, text)
    app.resize(name)
    return {"version": version(path.read_bytes())}


def new_text(app, body):
    """Make a new interpretation: {lang: ru, en or hy,
    file: a name like ps-118-33-37-pustota-i-put,
    text}. Never replaces a file."""
    if not app.notes:
        raise ApiError(403, "no interpretations folder")
    lang = text_arg(body, "lang")
    if lang not in TEXT_LANGS:
        raise ApiError(400, f"no such language: {lang}")
    slug = text_arg(body, "file").removesuffix(".md")
    if not SLUG_RE.fullmatch(slug):
        raise ApiError(
            400,
            "use small Latin letters, digits and -",
        )
    root, prefix = app.notes
    path = Path(root) / lang / f"{slug}.md"
    name = f"{prefix}{lang}/{slug}.md"
    if path.exists() or name in app.paths:
        raise ApiError(409, f"already there: {name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    write_file(path, text_arg(body, "text"))
    app.add(name, path)
    return {"name": name}


def get(app, route, query):
    """Answer a GET /api/... request."""

    def arg(k, default=""):
        return query.get(k, [default])[0]

    if route == "/api/shelf":
        return shelf(app, arg("folder"))
    if route == "/api/book":
        return book(app, arg("name"))
    if route == "/api/word":
        return word(arg("w"), arg("lang", "en"))
    if route == "/api/source":
        return source(app, arg("name"))
    if route == "/api/timeline":
        return timeline(app)
    if route == "/api/blog":
        return blog(app)
    if route == "/api/features":
        return features(app)
    if route == "/api/recent":
        n = arg("n", "0")
        if not n.isdigit():
            raise ApiError(400, "n must be a number")
        return recent(app, int(n))
    if route == "/api/stats":
        return stats(app)
    if route == "/api/library":
        return library(app)
    if route == "/api/volume":
        return volume(app, arg("folder"))
    raise ApiError(404, f"no such page: {route}")


POSTS = {
    "/api/position": set_position,
    "/api/mark": toggle_mark,
    "/api/forget": forget,
    "/api/note": note,
    "/api/save": save_text,
    "/api/new": new_text,
}


def post(app, route, body):
    """Answer a POST /api/... request."""
    if route not in POSTS:
        raise ApiError(404, f"no such page: {route}")
    if not isinstance(body, dict):
        raise ApiError(400, "send a JSON object")
    return POSTS[route](app, body)


def static_file(route, web_dir=WEB_DIR):
    """Path of a file in web/ for a route ("/" is
    index.html), or None. Nothing outside web/."""
    rel = route.lstrip("/") or "index.html"
    root = Path(web_dir).resolve()
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        return None
    return path if path.is_file() else None


def local_host(host):
    """True for a Host header naming this computer.
    Stops other sites reaching the server through a
    name that points here (DNS rebinding)."""
    name = (host or "").strip().lower()
    if name.startswith("["):
        name = name.partition("]")[0] + "]"
    else:
        name = name.rpartition(":")[0] or name
    return name in LOCAL_HOSTS


class Handler(BaseHTTPRequestHandler):
    app = None  # set by serve()
    web_dir = WEB_DIR

    def log_message(self, fmt, *args):
        pass

    def send(self, status, data, ctype):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(data))
        self.send_header("Cache-Control", "no-store")
        self.send_header(
            "X-Content-Type-Options", "nosniff"
        )
        self.send_header("Content-Security-Policy", CSP)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    def send_json(self, status, obj):
        data = json.dumps(obj, ensure_ascii=False)
        self.send(
            status,
            data.encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def answer(self, fn):
        """Run fn and send its result as JSON."""
        if not local_host(self.headers.get("Host")):
            self.send_json(403, {"error": "not local"})
            return
        try:
            self.send_json(200, fn())
        except ApiError as e:
            self.send_json(e.status, {"error": str(e)})

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path.startswith("/api/"):
            query = parse_qs(url.query)
            self.answer(
                lambda: get(self.app, url.path, query)
            )
            return
        if not local_host(self.headers.get("Host")):
            self.send_json(403, {"error": "not local"})
            return
        path = static_file(url.path, self.web_dir)
        if path is None:
            self.send(
                404,
                b"not found\n",
                "text/plain; charset=utf-8",
            )
            return
        ctype = mimetypes.guess_type(path.name)[0]
        ctype = ctype or "application/octet-stream"
        if ctype.startswith("text/") or ctype in (
            "application/javascript",
            "application/json",
        ):
            ctype += "; charset=utf-8"
        self.send(200, path.read_bytes(), ctype)

    do_HEAD = do_GET

    def do_POST(self):
        url = urlsplit(self.path)
        self.answer(
            lambda: post(self.app, url.path, self.body())
        )

    def body(self):
        """The request's JSON body."""
        ctype = self.headers.get("Content-Type", "")
        if ctype.split(";")[0].strip() != (
            "application/json"
        ):
            raise ApiError(415, "send application/json")
        try:
            n = int(self.headers.get("Content-Length"))
        except (TypeError, ValueError):
            raise ApiError(411, "no Content-Length")
        if not 0 <= n <= MAX_BODY:
            raise ApiError(413, "request too large")
        try:
            return json.loads(self.rfile.read(n))
        except ValueError:
            raise ApiError(400, "not JSON")


def server(app, host=HOST, port=PORT, web_dir=WEB_DIR):
    """A server for app (not started yet)."""
    handler = type(
        "AppHandler",
        (Handler,),
        {"app": app, "web_dir": web_dir},
    )
    return ThreadingHTTPServer((host, port), handler)


def serve(files, host=HOST, port=PORT, notes=None):
    """Serve until Ctrl-C. Returns an exit code.
    notes: (folder, shelf prefix) of the texts that
    can be edited."""
    app = App(files, notes=notes)
    try:
        srv = server(app, host, port)
    except OSError as e:
        print(
            f"cannot listen on {host}:{port}: {e}",
            file=sys.stderr,
        )
        return 1
    name = "localhost" if host == HOST else host
    print(f"nx-gir web: http://{name}:{port}/")
    print("Ctrl-C stops it.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        srv.server_close()
    return 0
