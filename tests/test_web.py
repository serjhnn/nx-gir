import http.client
import json
import re
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


def test_parallel(tmp_path):
    files = []
    for top in ("grabar", "ashkharhabar"):
        for name in ("ps.txt", "only-" + top + ".txt"):
            p = tmp_path / top / name
            p.parent.mkdir(exist_ok=True)
            p.write_text("Սաղմոս\n")
            files.append((f"{top}/{name}", 7, p))
    app = App(files, tmp_path / "state.json")
    ps = web.book(app, "grabar/ps.txt")
    assert ps["parallel"] == ["ashkharhabar/ps.txt"]
    back = web.book(app, "ashkharhabar/ps.txt")
    assert back["parallel"] == ["grabar/ps.txt"]
    one = "grabar/only-grabar.txt"
    assert web.book(app, one)["parallel"] == []
    assert app.parallel("grabar") == []
    assert app.parallel("notes/grabar/ps.txt") == []


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
    body = {"name": name, "pos": [1, 1]}
    r = web.post(app, "/api/mark", body)
    assert r["added"] is True
    # word 1 of line 1 is the 6th word of the book
    assert r["marks"] == [{"pos": [1, 1], "at": 5}]
    assert web.book(app, name)["marks"] == r["marks"]
    r = web.post(app, "/api/mark", body)
    assert r["added"] is False and r["marks"] == []


def test_book_position_and_sentences(app):
    name = "grabar/john.txt"
    b = web.book(app, name)
    assert b["at"] is None
    # two sentences, one per line
    assert b["starts"] == [0, 4]
    web.post(
        app,
        "/api/position",
        {"name": name, "pos": [1, 3], "lines": 2},
    )
    assert web.book(app, name)["at"] == 7


def test_notes_add_edit_delete(app):
    name = "grabar/john.txt"
    # a word in the middle of the second sentence
    r = web.post(
        app,
        "/api/note",
        {"name": name, "pos": [1, 2], "text": " hi "},
    )
    (n,) = r["notes"]
    assert n["text"] == "hi"
    # kept at the sentence's first word, like the
    # terminal reader does it
    assert n["pos"] == [1, 0] and n["at"] == 4
    assert n["quote"] == "Եւ Բանն էր առ ա՟ծ"
    assert app.state().notes(name)[0]["pos"] == [1, 0]
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


def test_fonts_are_there():
    css = web.static_file("/fonts.css").read_text()
    urls = re.findall(r'url\("([^"]+)"\)', css)
    assert urls
    for u in urls:
        assert web.static_file("/" + u), u
    html = web.static_file("/").read_text()
    assert html.index("fonts.css") < html.index("style.css")


def test_fonts_match_app_js():
    js = web.static_file("/app.js").read_text()
    names = re.search(
        r"const FONTS = \[([^\]]*)\]", js
    ).group(1)
    fonts = re.findall(r'"(\w+)"', names)
    assert fonts[0] == "noto"  # the default: no CSS
    css = web.static_file("/style.css").read_text()
    for f in fonts[1:]:
        assert f'[data-font="{f}"]' in css, f


def js_key(w):
    """wordKey() in web/app.js."""
    return (
        w.lower()
        .translate(str.maketrans("", "", "՛՜՞"))
        .replace("և", "եւ")
    )


def test_js_word_key_matches_normalize():
    from nxgir_reader import WORD_RE, normalize

    root = web.ROOT
    words = set()
    for d in ("books", "data", "interpretations"):
        for p in (root / d).rglob("*"):
            if p.suffix in (".txt", ".md"):
                text = p.read_text(encoding="utf-8")
                words.update(WORD_RE.findall(text))
    assert words
    bad = [w for w in words if js_key(w) != normalize(w)]
    assert bad == []
    assert "wordKey" in web.static_file(
        "/app.js"
    ).read_text(encoding="utf-8")


# -- editing interpretations --


@pytest.fixture
def notes_app(tmp_path):
    books = tmp_path / "books"
    books.mkdir()
    book = books / "john.txt"
    book.write_text("Ի սկզբանէ էր Բանն։\n")
    notes = tmp_path / "interpretations"
    (notes / "ru").mkdir(parents=True)
    ps = notes / "ru" / "ps-1.md"
    ps.write_text("# Пс 1\n\nТекст.\n", encoding="utf-8")
    txt = notes / "ru" / "plain.txt"
    txt.write_text("not markdown")
    files = [
        ("john.txt", 1, book),
        ("interpretations/ru/plain.txt", 1, txt),
        ("interpretations/ru/ps-1.md", 1, ps),
    ]
    return App(
        files,
        tmp_path / "state.json",
        notes=(notes, "interpretations/"),
    )


def test_only_interpretations_are_editable(notes_app):
    a = notes_app
    assert a.editable("interpretations/ru/ps-1.md")
    assert not a.editable("john.txt")
    assert not a.editable("interpretations/ru/plain.txt")
    assert not a.editable("interpretations/ru/nope.md")
    assert web.book(a, "interpretations/ru/ps-1.md")[
        "editable"
    ]
    assert not web.book(a, "john.txt")["editable"]
    assert web.shelf(a, "interpretations")["editable"]
    assert web.shelf(a, "interpretations/ru")["editable"]
    assert not web.shelf(a)["editable"]
    for name in ("john.txt", "../x.md"):
        with pytest.raises(ApiError):
            web.source(a, name)
        with pytest.raises(ApiError):
            web.post(
                a,
                "/api/save",
                {"name": name, "text": "x", "version": ""},
            )
    # no notes folder given: nothing is editable
    plain = App(a.files, a.state_path)
    assert not plain.editable("interpretations/ru/ps-1.md")


def test_save_exactly_as_given(notes_app):
    name = "interpretations/ru/ps-1.md"
    src = web.source(notes_app, name)
    assert src["text"] == "# Пс 1\n\nТекст.\n"
    # kept as is: spaces, no final newline, \r\n
    text = "# Пс 1  \n\n  Новый текст.\r\nконец"
    r = web.post(
        notes_app,
        "/api/save",
        {
            "name": name,
            "text": text,
            "version": src["version"],
        },
    )
    path = notes_app.path(name)
    assert path.read_bytes() == text.encode("utf-8")
    assert (
        r["version"]
        == web.source(notes_app, name)["version"]
    )
    size = dict((n, s) for n, s, _ in notes_app.files)
    assert size[name] == len(text.encode("utf-8"))
    # no temporary files left behind
    assert sorted(
        p.name for p in path.parent.iterdir()
    ) == [
        "plain.txt",
        "ps-1.md",
    ]


def test_save_refuses_a_changed_file(notes_app):
    name = "interpretations/ru/ps-1.md"
    src = web.source(notes_app, name)
    path = notes_app.path(name)
    path.write_text("changed elsewhere", encoding="utf-8")
    with pytest.raises(ApiError) as e:
        web.post(
            notes_app,
            "/api/save",
            {
                "name": name,
                "text": "mine",
                "version": src["version"],
            },
        )
    assert e.value.status == 409
    assert path.read_text() == "changed elsewhere"


def test_new_text(notes_app):
    a = notes_app
    r = web.post(
        a,
        "/api/new",
        {"lang": "en", "file": "ps-118-a", "text": "# A\n"},
    )
    name = "interpretations/en/ps-118-a.md"
    assert r == {"name": name}
    assert a.path(name).read_text() == "# A\n"
    assert a.editable(name)
    # on the shelf, in order, after the books
    assert [n for n, _, _ in a.files] == [
        "john.txt",
        name,
        "interpretations/ru/plain.txt",
        "interpretations/ru/ps-1.md",
    ]
    items = web.shelf(a, "interpretations")["items"]
    assert [i["label"] for i in items] == ["en/", "ru/"]
    # never replaces a file
    with pytest.raises(ApiError) as e:
        web.post(
            a,
            "/api/new",
            {"lang": "en", "file": "ps-118-a", "text": ""},
        )
    assert e.value.status == 409
    assert a.path(name).read_text() == "# A\n"


@pytest.mark.parametrize(
    "body",
    [
        {"lang": "fr", "file": "a", "text": ""},
        {"lang": "ru", "file": "../x", "text": ""},
        {"lang": "ru", "file": "a/b", "text": ""},
        {"lang": "ru", "file": "Ps 1", "text": ""},
        {"lang": "ru", "file": "", "text": ""},
        {"lang": "ru", "file": "-a", "text": ""},
        {"lang": "ru", "file": "a", "text": 5},
    ],
)
def test_new_text_bad(notes_app, body):
    with pytest.raises(ApiError):
        web.post(notes_app, "/api/new", body)
    assert not (notes_app.notes[0] / "ru" / "a.md").exists()


def test_new_text_in_armenian(notes_app):
    r = web.post(
        notes_app,
        "/api/new",
        {
            "lang": "hy",
            "file": "ps-1",
            "text": "# Սաղմոս Ա\n",
        },
    )
    name = "interpretations/hy/ps-1.md"
    assert r == {"name": name}
    path = notes_app.path(name)
    assert path.read_text(encoding="utf-8") == (
        "# Սաղմոս Ա\n"
    )
    assert notes_app.editable(name)


def test_book_format(app):
    md = web.book(app, "notes.md")
    # notes.md is "# Title\n> **quote**\n"
    assert md["format"] == {
        0: {"h": 1, "q": False, "spans": []},
        1: {"h": 0, "q": True, "spans": [[0, 5, "b"]]},
    }
    line = "".join(md["lines"][1])
    assert line[0:5] == "quote"
    assert web.book(app, "grabar/john.txt")["format"] == {}
