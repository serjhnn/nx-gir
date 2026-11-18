import nxgir_blog as bl
import nxgir_comics as comics
import nxgir_map as nm
import pytest

LINES = [
    "# a comment",
    "",
    "ani\tcity\t40.51\t43.57\t25\t37.5\tԱնի\tAni\tАни\t",
    "duin\tcity\t40.01\t44.58\t\t\tԴուին\tDuin\tДуин\t",
]


@pytest.fixture
def path(tmp_path):
    p = tmp_path / "places.tsv"
    p.write_text("\n".join(LINES) + "\n", "utf-8")
    return p


def test_read(path):
    ani, duin = nm.read(path)
    assert ani["pinned"] and (ani["x"], ani["y"]) == (
        25.0,
        37.5,
    )
    assert not duin["pinned"]
    assert (duin["x"], duin["y"]) == nm.project(
        40.01, 44.58
    )


@pytest.mark.parametrize(
    "line",
    [
        "x\tcity\t40\t44",
        "Ani\tcity\t40.5\t43.5\t\t\ta\tb\tc\t",
        "ani\ttown\t40.5\t43.5\t\t\ta\tb\tc\t",
        "ani\tcity\tnorth\t43.5\t\t\ta\tb\tc\t",
        "ani\tcity\t40.5\t43.5\t25\t\ta\tb\tc\t",
        "ani\tcity\t40.5\t43.5\t\t\ta\t\tc\t",
        "ani\tcity\t50\t43.5\t\t\ta\tb\tc\t",
        "ani\tcity\t40.5\t43.5\t101\t50\ta\tb\tc\t",
    ],
)
def test_bad_line(tmp_path, line):
    p = tmp_path / "places.tsv"
    p.write_text(line + "\n", "utf-8")
    with pytest.raises(nm.MapError):
        nm.read(p)


def test_twice(tmp_path):
    p = tmp_path / "places.tsv"
    p.write_text(LINES[2] + "\n" + LINES[2] + "\n", "utf-8")
    with pytest.raises(nm.MapError, match="twice"):
        nm.read(p)


def test_control_is_close():
    # the fit is rough: art, not a projection
    for lat, lon, x, y in nm.CONTROL:
        px, py = nm.project(lat, lon)
        assert abs(px - x) < nm.TOLERANCE
        assert abs(py - y) < nm.TOLERANCE


def test_places_file():
    places = nm.read()
    ids = [p["id"] for p in places]
    assert len(places) >= 15
    assert nm.IMAGE.is_file()
    for p in places:
        # every place stands on a painted spot
        assert p["pinned"], p["id"]
    assert "masis" in ids and "ararat" not in ids


def test_posts_name_known_places():
    ids = {p["id"] for p in nm.read()}
    posts = bl.read() + comics.read()
    named = [pid for s in posts for pid in s["places"]]
    assert named, "no post names a place yet"
    for pid in named:
        assert pid in ids, pid


def test_place_line(tmp_path):
    d = tmp_path / "blog"
    d.mkdir()
    (d / "2026-11-01-a.en.md").write_text(
        "# A\n\ntheme: site\nplace: ani, duin\n"
        "place: ani, bjni\n\nText.\n",
        "utf-8",
    )
    (d / "2026-11-01-a.hy.md").write_text(
        "# Ա\n\nplace: ani, duin, bjni\n\nՏեքստ։\n",
        "utf-8",
    )
    (d / "2026-11-02-b.en.md").write_text(
        "# B\n\nText.\n", "utf-8"
    )
    b, a = bl.read(d)
    assert a["places"] == ["ani", "duin", "bjni"]
    assert a["theme"] == "site" and b["places"] == []
    # the lines are not shown
    en = a["versions"][1]
    assert en["blocks"] == [["p", "Text."]]


@pytest.mark.parametrize(
    "meta", ["place: Ani", "place: ani,", "place: a b"]
)
def test_bad_place_line(tmp_path, meta):
    d = tmp_path / "blog"
    d.mkdir()
    (d / "2026-11-01-a.en.md").write_text(
        f"# A\n\n{meta}\n\nText.\n", "utf-8"
    )
    with pytest.raises(bl.BlogError):
        bl.read(d)


def test_two_place_lists(tmp_path):
    d = tmp_path / "blog"
    d.mkdir()
    (d / "2026-11-01-a.en.md").write_text(
        "# A\n\nplace: ani\n\nText.\n", "utf-8"
    )
    (d / "2026-11-01-a.hy.md").write_text(
        "# Ա\n\nplace: duin\n\nՏեքստ։\n", "utf-8"
    )
    with pytest.raises(bl.BlogError, match="two place"):
        bl.read(d)


def post(slug, date, places, title="T", blocks=None):
    blocks = blocks or [
        ["img", "a.jpg", "alt"],
        ["p", "Lead text."],
    ]
    return {
        "slug": slug,
        "date": date,
        "places": places,
        "versions": [
            {"lang": "en", "title": title, "blocks": blocks}
        ],
    }


def test_build(path):
    places = nm.read(path)
    out = nm.build(
        places,
        [post("old", "2026-11-01", ["ani"])],
        [post("new", "2026-11-05", ["ani", "duin"])],
    )
    ani, duin = out["places"]
    assert out["image"] == "img/map/base.webp"
    assert ani["names"]["hy"] == "Անի"
    # newest first, the type kept
    assert [s["slug"] for s in ani["stories"]] == [
        "new",
        "old",
    ]
    assert [s["type"] for s in ani["stories"]] == [
        "comics",
        "blog",
    ]
    v = ani["stories"][0]["versions"][0]
    assert (v["cover"], v["lead"]) == (
        "a.jpg",
        "Lead text.",
    )
    assert [s["slug"] for s in duin["stories"]] == ["new"]


def test_build_unknown_place(path):
    with pytest.raises(nm.MapError, match="nowhere"):
        nm.build(
            nm.read(path),
            [post("p", "2026-11-01", ["nowhere"])],
        )


def test_lead():
    assert nm.lead([["h", "H"]]) == ""
    long = " ".join(["word"] * 100)
    cut = nm.lead([["p", long]])
    assert cut.endswith("…") and len(cut) <= nm.LEAD + 1
    assert not cut.endswith(" …")


def test_api(tmp_path):
    from nxgir_web import App, get

    app = App([], tmp_path / "state.json")
    data = get(app, "/api/map", {})
    ids = {p["id"] for p in data["places"]}
    assert "bjni" in ids and data["kinds"] == list(nm.KINDS)
    off = App([], tmp_path / "state.json", places=None)
    assert get(off, "/api/map", {})["places"] == []


def test_kinds_match_app():
    js = (nm.ROOT / "web/app.js").read_text("utf-8")
    ui = js.split("const MAP_UI = {")[1].split("};")[0]
    for lang in ("hy", "en", "ru"):
        block = ui.split(f"  {lang}: {{")[1]
        block = block.split("kinds: {")[1].split("}")[0]
        for k in nm.KINDS:
            name = nm.KIND_NAMES[lang][k]
            assert f'{k}: "{name}"' in block, (lang, k)
    assert set(nm.KIND_NAMES) == {"hy", "en", "ru"}
    for names in nm.KIND_NAMES.values():
        assert set(names) == set(nm.KINDS)
