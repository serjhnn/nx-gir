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
    # a draft: not read
    (d / "drafts").mkdir()
    (d / "drafts/2026-10-07-hello.ru.md").write_text(
        "# Привет\n\nЧерновик.\n", "utf-8"
    )
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
    # blog/ reads, and opens with the welcome
    posts = bl.read()
    assert posts[-1]["slug"] == "welcome"
    assert posts[-1]["date"] == "2026-11-07"
    json.dumps(posts)


def test_picture(tmp_path):
    title, blocks = bl.parse(
        "# T\n\nText.\n\n![A cat](cat.jpg)\n", "t"
    )
    assert blocks == [
        ["p", "Text."],
        ["img", "cat.jpg", "A cat"],
    ]


def test_note_under_picture():
    _, blocks = bl.parse(
        "# T\n\n![A](a.jpg)\n\n> One\n> two\n\nText\n",
        "t",
    )
    assert blocks[1] == ["cap", "One two"]
    assert blocks[2] == ["p", "Text"]


def test_pictures_exist():
    for post in bl.read():
        for v in post["versions"]:
            for b in v["blocks"]:
                if b[0] == "img":
                    assert (
                        bl.ROOT / "web/img" / b[1]
                    ).is_file()


def test_theme(folder):
    (folder / "2026-11-01-later.en.md").write_text(
        "# Later\n\ntheme: books\n\nText.\n", "utf-8"
    )
    posts = {p["slug"]: p for p in bl.read(folder)}
    assert posts["later"]["theme"] == "books"
    assert posts["hello"]["theme"] is None
    # the theme line is not part of the text
    blocks = posts["later"]["versions"][0]["blocks"]
    assert blocks == [["p", "Text."]]


def test_theme_one_version_is_enough(folder):
    (folder / "2026-10-07-hello.hy.md").write_text(
        "# Բարև\n\ntheme: site\n\nԱռաջին։\n", "utf-8"
    )
    posts = {p["slug"]: p for p in bl.read(folder)}
    assert posts["hello"]["theme"] == "site"


def test_theme_bad(folder):
    (folder / "2026-10-07-hello.hy.md").write_text(
        "# Բարև\n\ntheme: site\n\nԱռաջին։\n", "utf-8"
    )
    (folder / "2026-10-07-hello.en.md").write_text(
        "# Hello\n\ntheme: books\n\nText.\n", "utf-8"
    )
    with pytest.raises(bl.BlogError, match="two themes"):
        bl.read(folder)
    (folder / "2026-10-07-hello.en.md").write_text(
        "# Hello\n\ntheme: cats\n\nText.\n", "utf-8"
    )
    with pytest.raises(bl.BlogError, match="theme"):
        bl.read(folder)


def test_posts_have_themes():
    for post in bl.read():
        assert post["theme"] in bl.THEMES, post["slug"]


def test_themes_match_app():
    js = (bl.ROOT / "web/app.js").read_text("utf-8")
    block = js.split("const BLOG_THEMES = {")[1]
    block = block.split("};")[0]
    for t in bl.THEMES:
        assert f"  {t}: " in block
    assert block.count("hy:") == len(bl.THEMES)
