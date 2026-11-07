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
    (d / "2026-10-07-hello.md").write_text(POST, "utf-8")
    (d / "2026-11-01-later.md").write_text(
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
    assert hello["title"] == "Hello"
    assert hello["blocks"] == [
        ["p", "First line, same paragraph."],
        ["h", "A heading"],
        ["p", "Second."],
    ]


def test_no_folder(tmp_path):
    assert bl.read(tmp_path / "none") == []


@pytest.mark.parametrize(
    "name, text, msg",
    [
        ("welcome.md", "# A\n\nB\n", "YYYY"),
        ("2026-13-01-a.md", "# A\n\nB\n", "bad date"),
        ("2026-10-01-a.md", "A\n\nB\n", "title"),
        ("2026-10-01-a.md", "# A\n", "no title"),
        ("2026-10-01-hello.md", "# A\n\nB\n", "two"),
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
