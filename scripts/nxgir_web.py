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
  POST /api/note               {name, pos, quote, text}
                               {name, i, text}
                               {name, i, delete: true}

It is meant for this computer only: it listens on
127.0.0.1, answers only to a local Host name, and
writes only for JSON requests (which a web page from
another site cannot send without asking first).
"""

import json
import mimetypes
import sys
from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer,
)
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import nxgir_grabar as grabar
from nxgir_browse import folder_exists, folder_items
from nxgir_reader import WORD_RE, plain_markdown, read_text
from nxgir_state import State

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
HOST = "127.0.0.1"
PORT = 8080
LOCAL_HOSTS = {"127.0.0.1", "localhost", "[::1]"}
MAX_BODY = 64 * 1024
LANGS = ("en", "hy")


class ApiError(Exception):
    """An answer other than 200: status and message."""

    def __init__(self, status, msg):
        super().__init__(msg)
        self.status = status


class App:
    """The books and the state file the API works on.
    files is [(name, size, path)], as shelf_files()
    in nxgir-cli.py gives it."""

    def __init__(self, files, state_path=None):
        self.files = list(files)
        self.paths = {n: p for n, _, p in self.files}
        self.state_path = state_path

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
    }


def book(app, name):
    """A book's lines, cut into words, with where it
    was left, its bookmarks and notes."""
    path = app.path(name)
    text = read_text(path)
    if path.suffix.lower() == ".md":
        text = plain_markdown(text)
    st = app.state()
    return {
        "name": name,
        "lines": [
            split_words(line) for line in text.splitlines()
        ],
        "pos": st.position(name),
        "marks": st.marks(name),
        "notes": st.notes(name),
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
    return {"added": added, "marks": st.marks(name)}


def note(app, body):
    """Add a note (no "i"), or edit or delete note i."""
    name = text_arg(body, "name")
    app.path(name)
    st = app.state()
    if "i" not in body:
        pos = pos_arg(body)
        text = text_arg(body, "text").strip()
        if not text:
            raise ApiError(400, "empty note")
        quote = text_arg(body, "quote")
        st.add_note(name, pos, quote, text)
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
    return {"notes": st.notes(name)}


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
    raise ApiError(404, f"no such page: {route}")


POSTS = {
    "/api/position": set_position,
    "/api/mark": toggle_mark,
    "/api/note": note,
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


def serve(files, host=HOST, port=PORT):
    """Serve until Ctrl-C. Returns an exit code."""
    try:
        srv = server(App(files), host, port)
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
