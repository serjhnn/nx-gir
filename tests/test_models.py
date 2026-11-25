"""The 3D reconstructions: web/models/models.json and
a module for each model (web/model3d.js)."""

import json
import re
from pathlib import Path

import nxgir_map as nm

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
LIST = WEB / "models" / "models.json"
LANGS = ("hy", "en", "ru")
# no sacred words in what the pages show (CLAUDE.md)
SACRED = re.compile(
    r"\b(god|jesus|christ|lord|holy|surb|israel"
    r"|jerusalem|սուրբ|սբ|աստված|святой|бог)\b",
    re.I,
)


def models():
    return json.loads(LIST.read_text("utf-8"))["models"]


def test_models_list():
    ms = models()
    assert ms
    places = {p["id"] for p in nm.read()}
    kinds = set(nm.KINDS)
    ids = [m["id"] for m in ms]
    assert len(ids) == len(set(ids))
    for m in ms:
        mid = m["id"]
        assert re.fullmatch(r"[a-z0-9-]+", mid)
        assert (WEB / "models" / f"{mid}.js").is_file()
        assert (WEB / m["image"]).is_file()
        assert m["kind"] in kinds
        assert m["place"] in places
        if m.get("book"):
            assert (ROOT / "books" / m["book"]).is_dir()
        for key in ("names", "sub", "about"):
            assert set(m[key]) == set(LANGS), key
        assert m["sources"]
        for s in m["sources"]:
            assert s["url"].startswith("https://")


def test_labels():
    # every name has its place in the model, and
    # every place a name in each language
    for m in models():
        js = (WEB / "models" / f"{m['id']}.js").read_text(
            "utf-8"
        )
        ids = set(
            re.findall(r'\{ id: "([a-z-]+)", at:', js)
        )
        assert ids == set(m["labels"]), m["id"]
        for names in m["labels"].values():
            assert set(names) == set(LANGS)


def test_no_sacred_words():
    for m in models():
        shown = [m["names"], m["sub"], m["about"]]
        shown += list(m["labels"].values())
        text = json.dumps(shown, ensure_ascii=False)
        assert not SACRED.search(text), m["id"]


def test_gltf_files():
    # a model made in Blender: its .gltf and every
    # file it names are there, and it needs nothing
    # the page cannot read
    ok = {"KHR_mesh_quantization", "KHR_texture_transform"}
    for m in models():
        js = (WEB / "models" / f"{m['id']}.js").read_text(
            "utf-8"
        )
        found = re.search(r'gltf: "([^"]+)"', js)
        if not found:
            continue
        path = WEB / found.group(1)
        assert path.is_file()
        g = json.loads(path.read_text("utf-8"))
        assert set(g.get("extensionsRequired", [])) <= ok
        for item in g.get("buffers", []) + g.get(
            "images", []
        ):
            assert not item["uri"].startswith("data:")
            assert (path.parent / item["uri"]).is_file()
