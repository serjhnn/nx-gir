"""Search across the library: nxgir_search.py."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import nxgir_search as srch  # noqa: E402
from nxgir_reader import WORD_RE  # noqa: E402


def test_loose_folds_the_two_spellings():
    assert srch.loose("թագաւոր") == "թագավոր"
    assert srch.loose("Թագավո՛ր") == "թագավոր"
    assert srch.loose("եւ") == "եվ"
    assert srch.loose("և") == "եվ"
    # ու stays
    assert srch.loose("ժողովուրդ") == "ժողովուրդ"
    assert srch.loose("իւր") == srch.loose("յուր")
    assert srch.loose("Եղիշէ") == "եղիշե"
    assert srch.loose("օր") == "որ"
    assert srch.loose("յորժամ") == "հորժամ"
    # յ inside a word stays
    assert srch.loose("Հայոց") == "հայոց"


def test_searched():
    assert srch.searched("grabar/a/b/01.txt")
    assert srch.searched("ashkharhabar/a/b.txt")
    assert not srch.searched("grabar/bible/x.txt")
    assert not srch.searched("ashkharhabar/bible/x.txt")
    assert not srch.searched("data/test/a.txt")
    assert not srch.searched("grabar/a.txt")


def lines_of(entry):
    """{(part, line)} of an entry, deltas undone."""
    out = set()
    for rows in entry.values():
        for p, *ns in rows:
            n = 0
            for i, d in enumerate(ns):
                n = d if i == 0 else n + d
                out.add((p, n))
    return out


def test_index_and_entry():
    idx = srch.build(
        [
            (
                "grabar/x/b/01.txt",
                "Բ · 1/2\nթագաւոր եւ թագաւոր\n\n"
                "Թագաւոր մեծ\n",
            ),
            ("grabar/bible/a.txt", "թագաւոր"),
            ("ashkharhabar/x/b/01.txt", "\nթագավոր\n"),
        ]
    )
    assert idx.parts == [
        "grabar/x/b/01.txt",
        "ashkharhabar/x/b/01.txt",
    ]
    e = idx.entry("թագավոր")
    # each spelling, its lines 1-based, the second
    # as the step from the first
    assert e == {
        "թագավոր": [[1, 2]],
        "թագաւոր": [[0, 2, 2]],
    }
    assert lines_of(e) == {(0, 2), (0, 4), (1, 2)}
    assert idx.entry("ոչինչ") is None


def test_common_words(monkeypatch):
    monkeypatch.setattr(srch, "COMMON", 2)
    idx = srch.build(
        [("grabar/x/b.txt", "եւ\nեւ\nեւ\nայլ")]
    )
    assert idx.entry("եվ") == {"*": 3}
    assert idx.entry("այլ") == {"այլ": [[0, 4]]}


def test_chunk():
    text = "\n".join(str(i) for i in range(1, 251))
    assert srch.chunk(text, 0)[0] == "1"
    assert len(srch.chunk(text, 0)) == srch.CHUNK
    assert srch.chunk(text, 2) == [
        str(i) for i in range(201, 251)
    ]


def test_parts_in_library_order():
    idx = srch.build(
        [
            ("grabar/zed/b/01.txt", "Բուն · 1/2\nա"),
            ("grabar/zed/b/02.txt", "Բուն · 2/2\nա"),
            ("grabar/abc/one.txt", "Մէկ\nա"),
            ("ashkharhabar/zed/b/01.txt", "Բուն · 1/2"),
        ]
    )
    first = {
        "grabar/zed/b/01.txt": "Բուն · 1/2",
        "grabar/zed/b/02.txt": "Բուն · 2/2",
        "grabar/abc/one.txt": "Մէկ",
        "ashkharhabar/zed/b/01.txt": "Բուն · 1/2",
    }
    names = {"zed": "Զեդ", "zed/b": "Գիրքը"}
    got = srch.parts(idx, first, names)
    # zed is in LIBRARY.tsv: first; abc after it
    assert got["authors"] == [
        ["zed", "Զեդ"],
        ["abc", "abc"],
    ]
    assert got["books"] == [
        ["zed/b", "Գիրքը", 0],
        ["abc/one.txt", "Մէկ", 1],
    ]
    # a translation is in the book of its original
    assert got["parts"] == [
        ["grabar/zed/b/01.txt", 0, 1],
        ["grabar/zed/b/02.txt", 0, 2],
        ["grabar/abc/one.txt", 1, 1],
        ["ashkharhabar/zed/b/01.txt", 0, 1],
    ]
    # a book's co-authors (LIBRARY.tsv), so that their
    # names find it
    names["ann"] = "Աննա"
    got = srch.parts(idx, first, names, {"zed/b": ["ann"]})
    assert got["with"] == {"0": [["ann", "Աննա"]]}


def js_function(js, name):
    start = js.index(f"function {name}(")
    return js[start : js.index("\n}\n", start) + 3]


@pytest.mark.skipif(
    not shutil.which("node"), reason="needs Node.js"
)
def test_loose_matches_app_js():
    js = (ROOT / "web/app.js").read_text("utf-8")
    words = set()
    for p in (ROOT / "books" / "grabar").rglob("*.txt"):
        words.update(WORD_RE.findall(p.read_text("utf-8")))
        if len(words) > 60000:
            break
    words = sorted(words) + [
        "իւր",
        "Յորժամ",
        "ւ",
        "ոււ",
        "Եօթն",
        "եաւ",
    ]
    src = (
        js_function(js, "wordKey")
        + js_function(js, "loose")
        + "const ws = JSON.parse(require('fs')"
        ".readFileSync(0, 'utf8'));\n"
        "console.log(JSON.stringify(ws.map(loose)))"
    )
    got = subprocess.run(
        ["node", "-e", src],
        input=json.dumps(words),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    want = [srch.loose(w) for w in words]
    bad = [
        (w, a, b)
        for w, a, b in zip(words, json.loads(got), want)
        if a != b
    ]
    assert bad == []


@pytest.mark.skipif(
    not shutil.which("node"), reason="needs Node.js"
)
def test_name_hits_in_app_js():
    """The search finds authors and books by name:
    each word starts a word of the name, in either
    spelling, and an author by its English or
    Russian name too."""
    js = (ROOT / "web/app.js").read_text("utf-8")
    parts = {
        "authors": [
            ["mkhitar-gosh", "Մխիթար Գոշ"],
            ["yeghishe", "Եղիշէ"],
        ],
        "books": [
            [
                "mkhitar-gosh/1-a",
                "Դատաստանագիրք, Ա խմբ.",
                0,
            ],
            ["yeghishe/1-v", "Վասն Վարդանայ", 1],
        ],
        # a co-author, with no folder, of book 1
        "with": {"1": [["zenob-glak", "Զենոբ Գլակ"]]},
    }
    names = {
        "zenob-glak": {"en": "Zenob Glak"},
        "mkhitar-gosh": {
            "en": "Mkhitar Gosh",
            "ru": "Мхитар Гош",
        },
        "yeghishe": {"en": "Yeghishe", "ru": "Егише"},
    }
    queries = [
        "Գոշ",
        "եղիշե",
        "gosh",
        "Гош",
        "դատաստանագիրք ա",
        "վարդանա",
        "իշխան",
        "glak",
        "Գլակ",
    ]
    src = (
        js_function(js, "wordKey")
        + js_function(js, "loose")
        + js_function(js, "nameFits")
        + js_function(js, "nameHits")
        + "const [qs, parts, names] = JSON.parse("
        "require('fs').readFileSync(0, 'utf8'));\n"
        "console.log(JSON.stringify(qs.map((q) => {"
        " const r = nameHits(q, parts, names);"
        " return [r.authors.map((a) => [a.id,"
        " a.also || null]), r.books.map((b) => b.key)];"
        " })))"
    )
    got = subprocess.run(
        ["node", "-e", src],
        input=json.dumps([queries, parts, names]),
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert json.loads(got) == [
        [[["mkhitar-gosh", None]], []],
        [[["yeghishe", None]], []],
        [[["mkhitar-gosh", "Mkhitar Gosh"]], []],
        [[["mkhitar-gosh", "Мхитар Гош"]], []],
        [[], ["mkhitar-gosh/1-a"]],
        [[], ["yeghishe/1-v"]],
        [[], []],
        # a co-author is an author in the list too
        [[["zenob-glak", "Zenob Glak"]], ["yeghishe/1-v"]],
        [[["zenob-glak", None]], ["yeghishe/1-v"]],
    ]


# -- the API of nxgir web --


@pytest.fixture
def app(tmp_path):
    import nxgir_web as web

    books = tmp_path / "books"
    files = []
    for name, text in [
        (
            "grabar/smbat/b/01.txt",
            "Տարեգիրք · 1/2\nԵւ նստաւ թագաւոր\n",
        ),
        (
            "grabar/smbat/b/02.txt",
            "Տարեգիրք · 2/2\nթագաւորն Հայոց\nթագաւոր\n",
        ),
        ("grabar/bible/x.txt", "թագաւոր\n"),
        (
            "ashkharhabar/smbat/b/01.txt",
            "Տարեգիրք · 1/2\nԵվ նստեց թագավոր\n",
        ),
    ]:
        p = books / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        files.append((name, len(text), p))
    lib = tmp_path / "LIBRARY.tsv"
    lib.write_text("smbat\tՍմբատ\nsmbat/b\tՏարեգիրք\n")
    return web.App(files, tmp_path / "s.json", library=lib)


def test_api_search(app):
    import nxgir_web as web

    got = web.get(app, "/api/search", {"w": ["Թագավոր"]})
    assert got["key"] == "թագավոր"
    assert got["entry"] == {
        "թագավոր": [[2, 2]],
        "թագաւոր": [[0, 2], [1, 3]],
    }
    none = web.get(app, "/api/search", {"w": ["չկայ"]})
    assert none["entry"] is None
    with pytest.raises(web.ApiError):
        web.get(app, "/api/search", {"w": [" "]})


def test_api_search_parts(app):
    import nxgir_web as web

    got = web.get(app, "/api/search-parts", {})
    assert got == {
        "parts": [
            ["grabar/smbat/b/01.txt", 0, 1],
            ["grabar/smbat/b/02.txt", 0, 2],
            ["ashkharhabar/smbat/b/01.txt", 0, 1],
        ],
        "books": [["smbat/b", "Տարեգիրք", 0]],
        "authors": [["smbat", "Սմբատ"]],
        "with": {},
    }


def test_api_lines(app):
    import nxgir_web as web

    got = web.get(
        app,
        "/api/lines",
        {"name": ["grabar/smbat/b/02.txt"], "k": ["0"]},
    )
    assert got["lines"][1] == "թագաւորն Հայոց"
    with pytest.raises(web.ApiError):
        web.get(app, "/api/lines", {"name": ["no.txt"]})
    with pytest.raises(web.ApiError):
        web.get(
            app,
            "/api/lines",
            {"name": ["grabar/smbat/b/02.txt"], "k": ["x"]},
        )
