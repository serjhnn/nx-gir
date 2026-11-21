import re

import nxgir_authors as au
import nxgir_blog as bl
import nxgir_map as mp
import nxgir_web as web
import pytest
from nxgir_web import ApiError, App

ROOT = au.ROOT

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
    assert web.authors(app) == {"authors": ["gosh"]}
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
    assert web.authors(none) == {"authors": []}


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
