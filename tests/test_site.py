import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
path = ROOT / "scripts/build-site.py"
spec = importlib.util.spec_from_file_location("bs", path)
bs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bs)


@pytest.fixture
def files(tmp_path):
    books = tmp_path / "books" / "grabar"
    books.mkdir(parents=True)
    john = books / "john.txt"
    john.write_text(
        "Ի սկզբանէ էր Բանն, ած։\n", encoding="utf-8"
    )
    return [("grabar/john.txt", 1, john)]


def test_build(tmp_path, files):
    out = tmp_path / "site"
    books, dirs, words = bs.build(out, files)
    assert (books, dirs) == (1, 2)
    html = (out / "index.html").read_text("utf-8")
    assert '<script src="static.js">' in html
    assert html.index("static.js") < html.index("app.js")
    # the fonts, in their folder
    assert (out / "fonts.css").is_file()
    assert list((out / "fonts").glob("*.woff2"))
    data = out / "data"
    top = json.loads(
        (data / "shelf/index.json").read_text("utf-8")
    )
    assert top["items"][0]["name"] == "grabar"
    assert not top["editable"]
    book = json.loads(
        (data / "book/grabar/john.txt.json").read_text(
            "utf-8"
        )
    )
    assert book["lines"][0][1] == "Ի"
    assert book["pos"] is None and not book["editable"]
    # ած is an abbreviation: its file has it
    part = data / f"word/en/{bs.bucket('ած')}.json"
    abbr, _ = json.loads(part.read_text("utf-8"))["ած"]
    assert abbr[0] == "ած → Աստուած"
    for lang in ("en", "hy"):
        assert len(
            list((data / "word" / lang).iterdir())
        ) == (bs.BUCKETS)


def test_build_again_and_not_elsewhere(tmp_path, files):
    out = tmp_path / "site"
    bs.build(out, files)
    bs.build(out, files)  # its own folder: made again
    other = tmp_path / "mine"
    other.mkdir()
    with pytest.raises(SystemExit):
        bs.build(other, files)


@pytest.mark.skipif(
    not shutil.which("node"), reason="needs Node.js"
)
def test_bucket_matches_app_js():
    js = (ROOT / "web/app.js").read_text("utf-8")
    start = js.index("function bucket(")
    end = js.index("\n}\n", start) + 3
    words = ["ած", "Բանն", "եւ", "x", "Ա𐀀"]
    src = (
        f"const BUCKETS = {bs.BUCKETS};\n"
        + js[start:end]
        + f"console.log(JSON.stringify("
        f"{json.dumps(words)}.map(bucket)))"
    )
    got = subprocess.run(
        ["node", "-e", src],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert json.loads(got) == [bs.bucket(w) for w in words]


def test_test_texts_left_out(tmp_path):
    data = tmp_path / "data"
    (data / "test").mkdir(parents=True)
    t = data / "test" / "a.txt"
    t.write_text("x")
    b = tmp_path / "books" / "b.txt"
    b.parent.mkdir()
    b.write_text("x")
    assert bs.unpublished(t, data)
    assert not bs.unpublished(b, data)
    names = [n for n, _, _ in bs.shelf_files()]
    assert names
    assert not any(n.startswith("test/") for n in names)
    assert not any(
        n.startswith("interpretations/") for n in names
    )
