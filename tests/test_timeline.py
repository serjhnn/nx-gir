import importlib.util
import re

import nxgir_timeline as tl
import nxgir_web as web
import pytest
from nxgir_web import App

ROOT = tl.ROOT

LINES = [
    "# a comment",
    "",
    "2026-10-18\tStart\t*\tBegins\tThe goals.\t",
    "2026-10-18\tBooks\t\tJohn\tThe Gospel.\t"
    "grabar/john.txt",
    "2026-10-20\tBooks\t\tFolder\t\tgrabar",
    "2026-10-21\tSite\t*\tOnline\t\thttps://nxgir.am",
    "2026-10-22\tBooks\t\tGone\t\tgrabar/mark.txt",
    "next\tSite\t\tLater\tA plan.\t",
]


@pytest.fixture
def path(tmp_path):
    p = tmp_path / "timeline.tsv"
    p.write_text("\n".join(LINES) + "\n", "utf-8")
    return p


@pytest.fixture
def app(tmp_path, path):
    john = tmp_path / "john.txt"
    john.write_text("Ի սկզբանէ\n", encoding="utf-8")
    files = [("grabar/john.txt", 10, john)]
    return App(
        files, tmp_path / "state.json", timeline=path
    )


def test_read(path):
    events = tl.read(path)
    assert [e["title"] for e in events] == [
        "Begins",
        "John",
        "Folder",
        "Online",
        "Gone",
        "Later",
    ]
    assert events[0]["big"] and not events[1]["big"]
    assert events[2]["text"] == ""
    assert [e["title"] for e in tl.news(events)] == [
        "Gone",
        "Online",
        "Folder",
    ]


@pytest.mark.parametrize(
    "line, msg",
    [
        ("2026-10-18\tStart\t*\tA\tB", "fields"),
        ("2026-13-01\tStart\t\tA\tB\t", "bad date"),
        ("2026-10-18\tNews\t\tA\tB\t", "kind"),
        ("2026-10-18\tSite\tx\tA\tB\t", "big"),
        ("2026-10-18\tSite\t\t\tB\t", "title"),
        ("2026-10-01\tSite\t\tA\tB\t", "before"),
        (
            "next\tSite\t\tA\tB\t\n"
            "2026-11-01\tSite\t\tA\tB\t",
            "after a plan",
        ),
    ],
)
def test_read_bad(tmp_path, line, msg):
    p = tmp_path / "t.tsv"
    p.write_text(
        "2026-10-10\tStart\t\tA\tB\t\n" + line + "\n",
        "utf-8",
    )
    with pytest.raises(tl.TimelineError, match=msg):
        tl.read(p)


def test_web_timeline(app):
    t = web.timeline(app)
    assert t["start"] == "2026-10-18"
    assert (t["books"], t["parts"]) == (1, 0)
    to = {e["title"]: e["to"] for e in t["events"]}
    assert to == {
        "Begins": "",
        "John": "read",
        "Folder": "folder",
        "Online": "url",
        # a book not on this shelf: no link
        "Gone": "",
    }
    gone = t["events"][0]
    assert gone["title"] == "Gone" and not gone["link"]
    assert [e["title"] for e in t["next"]] == ["Later"]
    # the newest three on the home page only
    top = web.shelf(app)
    assert [e["title"] for e in top["news"]] == [
        "Gone",
        "Online",
        "Folder",
    ]
    assert web.shelf(app, "grabar")["news"] == []
    assert web.get(app, "/api/timeline", {}) == t


def test_no_timeline(tmp_path):
    a = App([], tmp_path / "s.json", timeline=None)
    t = web.timeline(a)
    assert t["events"] == [] and t["start"] == ""


def test_the_timeline_file():
    # timeline.tsv reads, and its links are on the
    # shelf or addresses
    events = tl.read()
    assert tl.done(events)
    spec = importlib.util.spec_from_file_location(
        "cli", ROOT / "scripts/nxgir-cli.py"
    )
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    a = App(cli.shelf_files())
    bad = [
        e["link"]
        for e in events
        if e["link"] and not web.link_to(a, e["link"])
    ]
    assert bad == []


def test_kinds_match_app_js():
    js = (ROOT / "web/app.js").read_text("utf-8")
    start = js.index("const KINDS = [")
    end = js.index("];", start)
    got = re.findall(r'"([A-Za-z]+)"', js[start:end])
    assert tuple(got) == tl.KINDS
