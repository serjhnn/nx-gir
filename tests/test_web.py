import http.client
import json
import threading

import nxgir_web as web
import pytest
from nxgir_web import ApiError, App


@pytest.fixture
def app(tmp_path):
    books = tmp_path / "books"
    (books / "grabar").mkdir(parents=True)
    john = books / "grabar" / "john.txt"
    john.write_text(
        "Ի սկզբանէ էր Բանն։\nԵւ Բանն էր առ ա՟ծ։\n",
        encoding="utf-8",
    )
    notes = books / "notes.md"
    notes.write_text("# Title\n> **quote**\n")
    secret = tmp_path / "secret.txt"
    secret.write_text("not on the shelf")
    files = [
        ("grabar/john.txt", 50, john),
        ("notes.md", 20, notes),
    ]
    return App(files, tmp_path / "state.json")


def test_split_words_keeps_the_text():
    parts = web.split_words("Ի սկզբանէ, ա՟ծ։")
    assert parts[1::2] == ["Ի", "սկզբանէ", "ա՟ծ"]
    assert parts[::2] == ["", " ", ", ", "։"]
    parts = web.split_words("ա՟ծ։")
    assert parts == ["", "ա՟ծ", "։"]
    assert web.split_words("") == [""]
    line = "  Եւ Բանն էր։ "
    assert "".join(web.split_words(line)) == line


def test_shelf_top_and_folder(app):
    top = web.shelf(app)
    assert top["folder"] == ""
    assert [i["label"] for i in top["items"]] == [
        "grabar/",
        "notes.md",
    ]
    assert top["items"][1]["progress"] is None
    sub = web.shelf(app, "grabar/")
    assert sub["parent"] == ""
    assert [i["name"] for i in sub["items"]] == [
        "grabar/john.txt"
    ]
    with pytest.raises(ApiError) as e:
        web.shelf(app, "nope")
    assert e.value.status == 404


def test_book_words_and_markdown(app):
    b = web.book(app, "grabar/john.txt")
    assert len(b["lines"]) == 2
    assert b["lines"][1][1::2] == [
        "Եւ",
        "Բանն",
        "էր",
        "առ",
        "ա՟ծ",
    ]
    assert b["pos"] is None and b["notes"] == []
    md = web.book(app, "notes.md")
    assert "".join(md["lines"][0]) == "Title"
    assert "".join(md["lines"][1]) == "quote"


def test_only_shelf_books_are_read(app):
    for name in (
        "../secret.txt",
        "grabar/../../secret.txt",
        "/etc/passwd",
        "",
    ):
        with pytest.raises(ApiError) as e:
            web.book(app, name)
        assert e.value.status == 404


def test_word(app):
    w = web.word("ա՟ծ")
    assert any("Աստուած" in t for t in w["abbr"])
    assert w["meaning"] == [] or w["meaning"][-1]
    with pytest.raises(ApiError):
        web.word("  ")
    with pytest.raises(ApiError):
        web.word("ած", lang="fr")


def test_position_round_trip(app):
    name = "grabar/john.txt"
    r = web.post(
        app,
        "/api/position",
        {"name": name, "pos": [1, 2], "lines": 2},
    )
    assert r == {"progress": 100}
    assert web.book(app, name)["pos"] == [1, 2]
    # the terminal reader sees it too
    st = app.state()
    assert st.position(name) == [1, 2]


def test_marks_toggle(app):
    name = "grabar/john.txt"
    body = {"name": name, "pos": [0, 1]}
    r = web.post(app, "/api/mark", body)
    assert r == {"added": True, "marks": [[0, 1]]}
    r = web.post(app, "/api/mark", body)
    assert r == {"added": False, "marks": []}


def test_notes_add_edit_delete(app):
    name = "grabar/john.txt"
    r = web.post(
        app,
        "/api/note",
        {
            "name": name,
            "pos": [0, 0],
            "quote": "Ի սկզբանէ",
            "text": " first ",
        },
    )
    assert r["notes"][0]["text"] == "first"
    r = web.post(
        app,
        "/api/note",
        {"name": name, "i": 0, "text": "edited"},
    )
    assert r["notes"][0]["text"] == "edited"
    r = web.post(
        app,
        "/api/note",
        {"name": name, "i": 0, "delete": True},
    )
    assert r["notes"] == []


@pytest.mark.parametrize(
    "route,body",
    [
        ("/api/position", {"pos": [0, 0], "lines": 1}),
        (
            "/api/position",
            {"name": "notes.md", "pos": [0], "lines": 1},
        ),
        (
            "/api/position",
            {"name": "notes.md", "pos": [-1, 0]},
        ),
        (
            "/api/position",
            {"name": "notes.md", "pos": [0, 0]},
        ),
        ("/api/mark", {"name": "notes.md", "pos": "0"}),
        (
            "/api/note",
            {"name": "notes.md", "pos": [0, 0]},
        ),
        ("/api/note", {"name": "notes.md", "i": 0}),
        ("/api/note", {"name": "notes.md", "i": True}),
        ("/api/nope", {}),
    ],
)
def test_bad_posts(app, route, body):
    with pytest.raises(ApiError):
        web.post(app, route, body)
    assert not app.state_path.exists()


def test_post_wants_an_object(app):
    with pytest.raises(ApiError):
        web.post(app, "/api/mark", [1, 2])


def test_static_file(tmp_path):
    (tmp_path / "index.html").write_text("<p>hi")
    (tmp_path.parent / "out.txt").write_text("x")
    assert web.static_file("/", tmp_path).name == (
        "index.html"
    )
    assert web.static_file("/nope.css", tmp_path) is None
    assert web.static_file("/../out.txt", tmp_path) is None
    assert web.static_file("/%2e%2e/x", tmp_path) is None


def test_local_host():
    for h in (
        "localhost:8080",
        "127.0.0.1:8080",
        "LOCALHOST",
        "[::1]:8080",
    ):
        assert web.local_host(h), h
    for h in (None, "", "evil.example:8080", "10.0.0.2"):
        assert not web.local_host(h), h


@pytest.fixture
def url(app, tmp_path):
    """A running server on a free port."""
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<p>nx-gir")
    srv = web.server(app, port=0, web_dir=site)
    t = threading.Thread(target=srv.serve_forever)
    t.start()
    yield srv.server_address[1]
    srv.shutdown()
    srv.server_close()


def request(port, method, path, body=None, **headers):
    c = http.client.HTTPConnection("127.0.0.1", port)
    c.request(method, path, body=body, headers=headers)
    r = c.getresponse()
    data = r.read()
    c.close()
    return r, data


def test_http_get(url):
    r, data = request(url, "GET", "/")
    assert r.status == 200 and data == b"<p>nx-gir"
    assert "text/html" in r.getheader("Content-Type")
    r, data = request(
        url, "GET", "/api/shelf?folder=grabar"
    )
    assert r.status == 200
    items = json.loads(data)["items"]
    assert items[0]["name"] == "grabar/john.txt"
    r, data = request(url, "GET", "/api/book?name=x")
    assert r.status == 404
    assert json.loads(data)["error"]


def test_http_post(url):
    body = json.dumps(
        {"name": "notes.md", "pos": [0, 0]}
    ).encode()
    r, data = request(
        url,
        "POST",
        "/api/mark",
        body,
        **{"Content-Type": "application/json"},
    )
    assert r.status == 200
    assert json.loads(data)["added"] is True
    # a form post, as another site's page could send
    r, _ = request(
        url,
        "POST",
        "/api/mark",
        body,
        **{"Content-Type": "text/plain"},
    )
    assert r.status == 415


def test_http_foreign_host(url):
    r, _ = request(
        url, "GET", "/api/shelf", Host="evil.example"
    )
    assert r.status == 403
    r, _ = request(url, "GET", "/", Host="evil.example")
    assert r.status == 403


def test_http_security_headers(url):
    r, _ = request(url, "GET", "/")
    csp = r.getheader("Content-Security-Policy")
    assert "default-src 'self'" in csp
    r, _ = request(url, "GET", "/api/shelf")
    assert r.getheader("Content-Security-Policy")


def test_web_dir_has_the_pages():
    for name in ("index.html", "app.js", "style.css"):
        assert web.static_file("/" + name), name
    html = web.static_file("/").read_text()
    # the page works under the CSP: no inline code
    assert "<script>" not in html
    assert "style=" not in html
