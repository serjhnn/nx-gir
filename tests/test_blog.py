import json

import nxgir_blog as bl
import nxgir_web as web
import pytest
from nxgir_web import App

POST = """# Hello

First line,
same paragraph.

## A heading
Second.
"""


@pytest.fixture
def folder(tmp_path):
    d = tmp_path / "blog"
    d.mkdir()
    (d / "2026-10-07-hello.en.md").write_text(POST, "utf-8")
    (d / "2026-10-07-hello.hy.md").write_text(
        "# Բարև\n\nԱռաջին։\n", "utf-8"
    )
    (d / "2026-11-01-later.en.md").write_text(
        "# Later\n\nText.\n", "utf-8"
    )
    (d / "README.md").write_text("# not a post\n")
    return d


def test_read(folder):
    posts = bl.read(folder)
    assert [p["slug"] for p in posts] == [
        "later",
        "hello",
    ]
    hello = posts[1]
    assert hello["date"] == "2026-10-07"
    # Armenian first, as in LANGS
    hy, en = hello["versions"]
    assert hy == {
        "lang": "hy",
        "title": "Բարև",
        "blocks": [["p", "Առաջին։"]],
    }
    assert en["title"] == "Hello"
    assert en["blocks"] == [
        ["p", "First line, same paragraph."],
        ["h", "A heading"],
        ["p", "Second."],
    ]


def test_no_folder(tmp_path):
    assert bl.read(tmp_path / "none") == []


@pytest.mark.parametrize(
    "name, text, msg",
    [
        ("welcome.en.md", "# A\n\nB\n", "YYYY"),
        ("2026-10-01-a.md", "# A\n\nB\n", "LANG"),
        ("2026-10-01-a.de.md", "# A\n\nB\n", "lang"),
        ("2026-13-01-a.en.md", "# A\n\nB\n", "date"),
        ("2026-10-01-a.en.md", "A\n\nB\n", "title"),
        ("2026-10-01-a.en.md", "# A\n", "no title"),
        ("2026-10-01-hello.ru.md", "# A\n\nB\n", "two"),
    ],
)
def test_read_bad(folder, name, text, msg):
    (folder / name).write_text(text, "utf-8")
    with pytest.raises(bl.BlogError, match=msg):
        bl.read(folder)


def test_web_blog(tmp_path, folder):
    a = App([], tmp_path / "s.json", blog=folder)
    b = web.get(a, "/api/blog", {})
    assert b == {"posts": bl.read(folder)}
    none = App([], tmp_path / "s.json", blog=None)
    assert web.blog(none) == {"posts": []}


def test_the_blog():
    # blog/ reads, and opens with the welcome, in
    # Armenian and English
    posts = bl.read()
    assert posts[-1]["slug"] == "welcome"
    assert posts[-1]["date"] == "2026-11-07"
    langs = [v["lang"] for v in posts[-1]["versions"]]
    assert langs == ["hy", "en"]
    json.dumps(posts)
