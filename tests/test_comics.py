import json

import nxgir_blog as bl
import nxgir_comics as cm
import nxgir_web as web
import pytest
from nxgir_web import App

SERIES = """# A story

Intro.

## The comic

![First page](one.jpg)

> Page 1.

![Second page](two.jpg)
"""


@pytest.fixture
def folder(tmp_path):
    d = tmp_path / "comics"
    d.mkdir()
    (d / "2026-11-17-story.en.md").write_text(
        SERIES, "utf-8"
    )
    (d / "2026-11-17-story.hy.md").write_text(
        "# Պատմություն\n\nՆերածություն։\n\n"
        "![Էջ](one.jpg)\n",
        "utf-8",
    )
    (d / "README.md").write_text("# not a series\n")
    (d / "drafts").mkdir()
    (d / "drafts/2026-11-18-draft.en.md").write_text(
        "# Draft\n\n![x](x.jpg)\n", "utf-8"
    )
    return d


def test_read(folder):
    series = cm.read(folder)
    assert [s["slug"] for s in series] == ["story"]
    hy, en = series[0]["versions"]
    assert (hy["lang"], en["lang"]) == ("hy", "en")
    assert [b[0] for b in en["blocks"]] == [
        "p",
        "h",
        "img",
        "cap",
        "img",
    ]
    assert en["blocks"][2] == [
        "img",
        "one.jpg",
        "First page",
    ]


def test_no_pages(folder):
    (folder / "2026-11-19-bare.en.md").write_text(
        "# Bare\n\nNo pictures.\n", "utf-8"
    )
    with pytest.raises(bl.BlogError, match="no pages"):
        cm.read(folder)


def test_web_comics(tmp_path, folder):
    a = App([], tmp_path / "s.json", comics=folder)
    got = web.get(a, "/api/comics", {})
    assert got == {"series": cm.read(folder)}
    none = App([], tmp_path / "s.json", comics=None)
    assert web.comics(none) == {"series": []}


def test_the_comics():
    # comics/ reads, in Armenian first, and every
    # picture is a file of web/img/
    series = cm.read()
    assert series
    for s in series:
        assert s["versions"][0]["lang"] == "hy"
        for v in s["versions"]:
            for b in v["blocks"]:
                if b[0] == "img":
                    assert (
                        web.WEB_DIR / "img" / b[1]
                    ).is_file()
                    assert (
                        web.WEB_DIR / "img" / b[1]
                    ).stat().st_size < 300_000
    json.dumps(series)
