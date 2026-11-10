import json

import nxgir_blog as bl
import nxgir_features as ft
import nxgir_web as web
import pytest
from nxgir_web import App

PAGE = """# Features

What it can do.

## Lookup
Tap a word,
see it.

## Themes
Light and dark.
"""


@pytest.fixture
def folder(tmp_path):
    d = tmp_path / "features"
    d.mkdir()
    (d / "features.en.md").write_text(PAGE, "utf-8")
    (d / "features.hy.md").write_text(
        "# Հնարավորություններ\n\n## Բառ\nՀպեք։\n",
        "utf-8",
    )
    (d / "README.md").write_text("# not a page\n")
    # a draft: not read
    (d / "drafts").mkdir()
    (d / "drafts/features.ru.md").write_text(
        "# Возможности\n\nЧерновик.\n", "utf-8"
    )
    return d


def test_read(folder):
    # Armenian first, as in LANGS
    hy, en = ft.read(folder)
    assert hy == {
        "lang": "hy",
        "title": "Հնարավորություններ",
        "blocks": [["h", "Բառ"], ["p", "Հպեք։"]],
    }
    assert en["title"] == "Features"
    assert en["blocks"] == [
        ["p", "What it can do."],
        ["h", "Lookup"],
        ["p", "Tap a word, see it."],
        ["h", "Themes"],
        ["p", "Light and dark."],
    ]


def test_no_folder(tmp_path):
    assert ft.read(tmp_path / "none") == []


@pytest.mark.parametrize(
    "name, text, msg",
    [
        ("feature.ru.md", "# A\n\nB\n", "LANG"),
        ("features.de.md", "# A\n\nB\n", "lang"),
        ("features.ru.md", "A\n\nB\n", "title"),
    ],
)
def test_read_bad(folder, name, text, msg):
    (folder / name).write_text(text, "utf-8")
    with pytest.raises(bl.BlogError, match=msg):
        ft.read(folder)


def test_web_features(tmp_path, folder):
    a = App([], tmp_path / "s.json", features=folder)
    got = web.get(a, "/api/features", {})
    assert got == {"versions": ft.read(folder)}
    none = App([], tmp_path / "s.json", features=None)
    assert web.features(none) == {"versions": []}


def test_the_features():
    # features/ reads, in English at least, and
    # every version has features in it
    vs = ft.read()
    assert "en" in [v["lang"] for v in vs]
    for v in vs:
        kinds = [k for k, _ in v["blocks"]]
        assert kinds.count("h") >= 3
    json.dumps(vs)
