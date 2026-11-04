"""Local web reader: `nxgir web`.

A small HTTP server (standard library only) for the
web pages in web/ and a JSON API over the same books,
Grabar helpers and saved state as the terminal reader.

The API is plain functions over an App (tested in
tests/test_web.py); Handler only moves bytes.

  GET  /api/shelf?folder=      one folder of the shelf
  GET  /api/book?name=         a book, cut into words
  GET  /api/word?w=&lang=      abbreviation + meaning
  POST /api/position           {name, pos, lines}
  POST /api/mark               {name, pos}
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
import sys
import tempfile
from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer,
)
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import nxgir_grabar as grabar
from nxgir_browse import folder_exists, folder_items
from nxgir_reader import (
    WORD_RE,
    layout,
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

    def __init__(self, files, state_path=None, notes=None):
        self.files = list(files)
        self.paths = {n: p for n, _, p in self.files}
        self.state_path = state_path
        # (folder, shelf prefix) of the texts that
        # can be edited: interpretations/
        self.notes = notes

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
        if not item.folder:
            row["progress"] = st.progress(item.name)
        items.append(row)
    return {
        "folder": folder,
        "parent": folder.rpartition("/")[0],
        "items": items,
        "editable": app.in_notes(folder),
    }


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


def book(app, name):
    """A book's lines, cut into words, with where it
    was left ("at": its word), the first word of every
    sentence, its bookmarks and notes."""
    text = book_text(app, name)
    lay = layout(text, 10**9)
    st = app.state()
    pos = st.position(name)
    at = None
    if pos and lay.words:
        at = word_at(lay.words, pos)
    return {
        "name": name,
        "lines": [
            split_words(line) for line in text.splitlines()
        ],
        "pos": pos,
        "at": at,
        "starts": sentence_starts(lay),
        "editable": app.editable(name),
        **places(app, name, st, lay),
    }


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
    raise ApiError(404, f"no such page: {route}")


POSTS = {
    "/api/position": set_position,
    "/api/mark": toggle_mark,
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
