import importlib.util
import re

import nxgir_authors as au
import nxgir_blog as bl
import nxgir_map as mp
import nxgir_web as web
import pytest
from nxgir_web import ApiError, App

ROOT = au.ROOT
_spec = importlib.util.spec_from_file_location(
    "bs", ROOT / "scripts" / "build-site.py"
)
bs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bs)

HY = """# Մխիթար Գոշ

years: մոտ 1130 – 1213
role: վարդապետ
place: gandzak
status: machine

Առաջին
տող։

Երկրորդ։
"""

EN = """# Mkhitar Gosh

years: c. 1130 – 1213
source: Wikipedia

Text.
"""


@pytest.fixture
def folder(tmp_path):
    d = tmp_path / "authors"
    d.mkdir()
    (d / "gosh.hy.md").write_text(HY, "utf-8")
    (d / "gosh.en.md").write_text(EN, "utf-8")
    (d / "README.md").write_text("# not an author\n")
    return d


def test_read(folder):
    a = au.read(folder)["gosh"]
    assert a["places"] == ["gandzak"]
    assert a["status"] == "machine"
    assert a["post"] is None and a["face"] is None
    hy, en = a["versions"]
    assert hy["lang"] == "hy"
    assert hy["name"] == "Մխիթար Գոշ"
    assert hy["text"] == ["Առաջին տող։", "Երկրորդ։"]
    assert hy["source"] == ""
    assert en["years"] == "c. 1130 – 1213"
    assert en["role"] == ""


def test_no_folder(tmp_path):
    assert au.read(tmp_path / "none") == {}


@pytest.mark.parametrize(
    "name, text",
    [
        ("x.hy.md", "no title\n\nText.\n"),
        ("x.hy.md", "# X\n\nyears: 1\n"),
        ("x.hy.md", "# X\n\nage: 1\n\nText.\n"),
        ("x.hy.md", "# X\n\nrole: a\nrole: b\n\nT.\n"),
        ("x.hy.md", "# X\n\nstatus: done\n\nT.\n"),
        ("x.hy.md", "# X\n\nplace: Ani\n\nT.\n"),
        ("x.hy.md", "# X\n\nface: a.gif\n\nT.\n"),
        ("x.de.md", "# X\n\nT.\n"),
        ("X.hy.md", "# X\n\nT.\n"),
    ],
)
def test_bad(tmp_path, name, text):
    (tmp_path / name).write_text(text, "utf-8")
    with pytest.raises(au.AuthorError):
        au.read(tmp_path)


def test_shared_must_agree(folder):
    (folder / "gosh.ru.md").write_text(
        "# Мхитар Гош\n\nplace: ani\n\nТекст.\n",
        "utf-8",
    )
    with pytest.raises(au.AuthorError):
        au.read(folder)


def test_api(folder, tmp_path):
    places = tmp_path / "places.tsv"
    places.write_text(
        "gandzak\tcity\t40.68\t46.36\t94.5\t29.5"
        "\tԳանձակ\tGandzak\tГандзак\t\n",
        "utf-8",
    )
    app = App([], authors=folder, places=places)
    assert web.authors(app) == {
        "books": [],
        "titles": {},
        "authors": ["gosh"],
        "names": {
            "gosh": {
                "hy": "Մխիթար Գոշ",
                "en": "Mkhitar Gosh",
            }
        },
    }
    a = web.author(app, "gosh")
    assert a["places"] == [
        {
            "id": "gandzak",
            "hy": "Գանձակ",
            "en": "Gandzak",
            "ru": "Гандзак",
        }
    ]
    with pytest.raises(ApiError):
        web.author(app, "nobody")
    none = App([], authors=None)
    assert web.authors(none) == {
        "authors": [],
        "names": {},
        "books": [],
        "titles": {},
    }


# the files of authors/ themselves


def library_authors():
    names = web.read_names(web.LIBRARY)
    return {k for k in names if "/" not in k}


def test_files_are_good():
    found = au.read()
    assert found, "authors/ has no author"
    authors = library_authors()
    places = {p["id"] for p in mp.read()}
    posts = {p["slug"] for p in bl.read()}
    for aid, a in found.items():
        assert aid in authors, aid
        langs = [v["lang"] for v in a["versions"]]
        assert langs == list(au.LANGS), aid
        for p in a["places"]:
            assert p in places, (aid, p)
        if a["post"]:
            assert a["post"] in posts, aid
        if a["face"]:
            assert (ROOT / "web" / a["face"]).is_file()
        for v in a["versions"]:
            assert v["years"] and v["role"], aid
            assert v["source"], aid


def test_site_author_api():
    a = web.author(App([]), "mkhitar-gosh")
    assert a["post"]["slug"] == "mkhitar-gosh"
    assert {p["id"] for p in a["places"]} >= {"gandzak"}


def test_ui_langs_match():
    js = (ROOT / "web" / "app.js").read_text("utf-8")
    block = js.split("const AUTHOR_UI = {", 1)[1]
    block = block.split("\n};", 1)[0]
    keys = re.findall(r"^  (\w+): \{", block, re.M)
    assert tuple(keys) == au.LANGS


# the book cards: authors/<author>/<book>.LANG.md

BOOK = """# Դատաստանագիրք

written: 1184
kind: օրենսգիրք
place: gandzak

Տեքստ։
"""


def test_read_books(folder):
    (folder / "gosh").mkdir()
    (folder / "gosh" / "1-law.hy.md").write_text(
        BOOK, "utf-8"
    )
    # the authors are read as before
    assert set(au.read(folder)) == {"gosh"}
    b = au.read_books(folder)["gosh/1-law"]
    assert b["places"] == ["gandzak"]
    assert b["status"] == "machine"
    assert "face" not in b
    (v,) = b["versions"]
    assert v["written"] == "1184"
    assert v["kind"] == "օրենսգիրք"
    assert v["source"] == ""
    app = App([], authors=folder)
    assert web.authors(app)["books"] == ["gosh/1-law"]
    # the search finds a book by its card's title
    t = web.authors(app)["titles"]["gosh/1-law"]
    assert set(t) == {"hy"}
    assert web.book_info(app, "gosh/1-law")["id"] == (
        "gosh/1-law"
    )
    with pytest.raises(ApiError):
        web.book_info(app, "gosh/2-none")


@pytest.mark.parametrize(
    "text",
    [
        # an author's fields, not a book's
        "# X\n\nyears: 1\n\nT.\n",
        "# X\n\nface: a.jpg\n\nT.\n",
        "# X\n\nwritten: 1\nwritten: 2\n\nT.\n",
    ],
)
def test_bad_book(tmp_path, text):
    (tmp_path / "x").mkdir()
    (tmp_path / "x" / "b.hy.md").write_text(text, "utf-8")
    with pytest.raises(au.AuthorError):
        au.read_books(tmp_path)


def test_book_files_are_good():
    """Every book card is a book of LIBRARY.tsv's
    authors in books/grabar/, in all three
    languages, with its places and post."""
    found = au.read_books()
    assert found, "authors/ has no book card"
    grabar = ROOT / "books" / "grabar"
    places = {p["id"] for p in mp.read()}
    posts = {p["slug"] for p in bl.read()}
    authors = library_authors()
    for bid, b in found.items():
        assert bid.split("/")[0] in authors, bid
        path = grabar / bid
        assert (
            path.is_dir()
            or path.with_suffix(".txt").is_file()
        ), bid
        langs = [v["lang"] for v in b["versions"]]
        assert langs == list(au.LANGS), bid
        for p in b["places"]:
            assert p in places, (bid, p)
        if b["post"]:
            assert b["post"] in posts, bid
        for v in b["versions"]:
            assert v["written"] and v["kind"], bid
            assert v["source"], bid


def test_book_cards():
    """/api/book-cards: every book card, once, in
    the language asked, with where it opens."""
    files = bs.shelf_files()
    app = App(files)
    ids = set(au.read_books())
    for lang in au.LANGS:
        cards = web.book_cards(app, lang)["books"]
        assert {c["id"] for c in cards} == ids
        assert len(cards) == len(ids)
        for c in cards:
            assert c["lang"] == lang
            assert c["name"] and c["lead"]
            assert c["to"].startswith(("#/b/", "#/read/"))
            assert c["authors"]
    js = (ROOT / "web" / "app.js").read_text("utf-8")
    block = js.split("const CARDS_UI = {", 1)[1]
    block = block.split("\n};", 1)[0]
    keys = re.findall(r"^  (\w+): \{", block, re.M)
    assert tuple(keys) == au.LANGS


def test_groups_and_centuries():
    """Every book card has a kind of GROUPS (else add
    a word to it); its century, when it has one, is
    read from the English card."""
    assert au.group_of("A Chronicle") == "history"
    assert au.group_of("a poem on the sky") == "poetry"
    assert au.group_of("nothing like it") is None
    assert au.century_of("late 12th century") == 12
    assert au.century_of("finished in 1407") == 15
    assert au.century_of("the 570s") == 6
    assert au.century_of("unknown") is None
    for bid, b in au.read_books().items():
        (en,) = [
            v for v in b["versions"] if v["lang"] == "en"
        ]
        assert au.group_of(en["kind"]), (bid, en["kind"])
