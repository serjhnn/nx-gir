import importlib.util
import json
import re
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
    tsv = tmp_path / "timeline.tsv"
    tsv.write_text(
        "2026-10-18\tBooks\t*\tJohn\t\tgrabar/john.txt\n",
        encoding="utf-8",
    )
    books, dirs, words = bs.build(out, files, tsv)
    assert (books, dirs) == (1, 2)
    html = (out / "index.html").read_text("utf-8")
    assert '<script src="static.js?v=' in html
    assert html.index("static.js") < html.index("app.js")
    # each file with the hash of its content, so a
    # browser never mixes old and new ones
    for name in bs.VERSIONED:
        m = re.search(
            rf'"{re.escape(name)}\?v=([0-9a-f]{{10}})"',
            html,
        )
        assert m, name
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
    # the timeline, and its newest on the top page
    # the titles, for the list of readings
    titles = json.loads(
        (data / "titles.json").read_text("utf-8")
    )
    assert titles == {
        "grabar/john.txt": "Ի սկզբանէ էր Բանն, ած։"
    }
    # the Library page: john.txt has no author
    lib = json.loads(
        (data / "library.json").read_text("utf-8")
    )
    assert lib == {"authors": []}
    # the blog, from blog/
    blog = json.loads(
        (data / "blog.json").read_text("utf-8")
    )
    assert blog["posts"][-1]["slug"] == "welcome"
    # the Features page, from features/
    feats = json.loads(
        (data / "features.json").read_text("utf-8")
    )
    assert "en" in [v["lang"] for v in feats["versions"]]
    tl = json.loads(
        (data / "timeline.json").read_text("utf-8")
    )
    assert tl["events"][0]["to"] == "read"
    # the Statistics page, with this site's size
    st = json.loads(
        (data / "stats.json").read_text("utf-8")
    )
    got = {x["key"]: x for x in st["limits"]}
    assert 0 < got["site"]["value"]
    assert got["site"]["since"] == ""
    # git as recorded in notes/limits.tsv
    assert got["git"]["since"]
    assert st["words"] == words
    assert top["news"][0]["title"] == "John"
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


def test_pages_count_visits(tmp_path):
    # with a GoatCounter code static.js says where
    # to count; without one, nothing is counted
    on = tmp_path / "on"
    on.mkdir()
    bs.pages(on, counter="nxgir")
    js = (on / "static.js").read_text("utf-8")
    # the build, which app.js puts after data/
    assert re.search(r'NXGIR_BUILD = "[0-9a-f]+"', js)
    assert "https://nxgir.goatcounter.com/count" in js
    off = tmp_path / "off"
    off.mkdir()
    bs.pages(off, counter="")
    js = (off / "static.js").read_text("utf-8")
    assert "NXGIR_COUNT" not in js


def test_searchable(tmp_path, files):
    # search engines see no #/ pages: each book is a
    # plain page too, in the sitemap
    out = tmp_path / "site"
    bs.build(out, files)
    page = out / "read/grabar/john.html"
    html = page.read_text("utf-8")
    assert "<p>Ի սկզբանէ էր Բանն, ած։</p>" not in html
    assert "<h1>Ի սկզբանէ էր Բանն, ած։</h1>" in html
    assert 'href="./#/read/grabar/john.txt"' in html
    canon = bs.SITE + "/read/grabar/john.html"
    assert f'rel="canonical" href="{canon}"' in html
    assert "style.css?v=" in html
    sm = (out / "sitemap.xml").read_text("utf-8")
    assert f"<loc>{canon}</loc>" in sm
    robots = (out / "robots.txt").read_text("utf-8")
    assert f"Sitemap: {bs.SITE}/sitemap.xml" in robots
    index = (out / "index.html").read_text("utf-8")
    assert '<a href="read/grabar/john.html">' in index
    # its own words, which app.js replaces, and
    # the list among them
    about = index.index('id="about"')
    noscript = index.index("<noscript>")
    assert about < noscript < index.index("</main>")
    assert "Grabar (Classical Armenian)" in index
    assert '<header class="bar" data-nosnippet>' in index
    # the blog posts, each language on its own
    # page, with their dates
    post = out / "blog/welcome.en.html"
    html = post.read_text("utf-8")
    assert '<html lang="en">' in html
    assert 'href="./#/blog/welcome/en"' in html
    assert (
        '<h1>Welcome to the <span class="nxgir">'
        "nxGir</span> blog</h1>"
    ) in html
    assert "<h2>The idea</h2>" in html
    # the other languages are named
    assert 'hreflang="hy"' in html
    assert 'hreflang="en"' in html
    canon = bs.SITE + "/blog/welcome.en.html"
    assert (
        f"<url><loc>{canon}</loc>"
        "<lastmod>2026-11-07</lastmod></url>"
    ) in sm
    assert '<a href="blog/welcome.en.html">' in index
    assert (out / "blog/welcome.hy.html").exists()
    # the Features page as a plain page too
    feat = (out / "features.en.html").read_text("utf-8")
    assert 'href="./#/features/en"' in feat
    assert "<h1>Features</h1>" in feat
    assert f"{bs.SITE}/features.en.html" in sm
    assert '<a href="features.en.html">' in index


def test_licensed():
    credit = {
        "text": "Թարգմանությունը՝ <Նախագիր>",
        "license": "CC BY-SA 4.0",
        "url": "https://example.org/by-sa/",
    }
    head, text = bs.licensed(credit, "<p>x</p>")
    assert head == (
        '<link rel="license"'
        ' href="https://example.org/by-sa/">\n'
    )
    assert text.startswith('<p class="tr-credit">')
    assert "&lt;Նախագիր&gt;" in text
    assert text.endswith("<p>x</p>")
    assert bs.licensed(None, "<p>x</p>") == (
        "",
        "<p>x</p>",
    )


def test_describe():
    lines = ["Title", "", "one two", "three four"]
    assert bs.describe(lines) == "one two three four"
    assert bs.describe(lines, 10) == "one two…"


def test_build_volumes(tmp_path):
    # a page for each folder in a book's folder
    d = tmp_path / "books/grabar/ann/1-book"
    d.mkdir(parents=True)
    one = d / "01.txt"
    one.write_text("Գիրք · 1/1\n\nտող\n", encoding="utf-8")
    files = [("grabar/ann/1-book/01.txt", 9, one)]
    out = tmp_path / "site"
    bs.build(out, files, None)
    data = out / "data"
    got = json.loads(
        (data / "volume/grabar/ann/1-book.json").read_text(
            "utf-8"
        )
    )
    assert got["groups"][0]["parts"][0]["n"] == 1
    # not for the top, or a folder of authors
    assert not (data / "volume/grabar.json").exists()


def test_offline_zip(tmp_path, files):
    import zipfile

    out = tmp_path / "site"
    tsv = tmp_path / "timeline.tsv"
    tsv.write_text(
        "2026-10-18\tBooks\t*\tJohn\t\tgrabar/john.txt\n",
        encoding="utf-8",
    )
    bs.build(out, files, tsv)
    # the published pages offer it, and tell its size
    js = (out / "static.js").read_text("utf-8")
    assert f'NXGIR_DOWNLOAD = "{bs.ZIP}"' in js
    info = json.loads(
        (out / "download.json").read_text("utf-8")
    )
    assert info["file"] == bs.ZIP
    assert info["bytes"] == (out / bs.ZIP).stat().st_size
    names = zipfile.ZipFile(out / bs.ZIP).namelist()
    top = "nxgir-site/"
    for n in ("index.html", "app.js", "serve.py"):
        assert top + n in names
    assert top + "README.txt" in names
    assert top + "data/book/grabar/john.txt.json" in names
    # not in it: itself, the pages for search engines
    # and the size file
    assert not any(
        n.startswith(top + "read/") or "download.json" in n
        for n in names
    )
    assert top + bs.ZIP not in names
    assert top + "sitemap.xml" not in names
    # its static.js has no link to the zip and no
    # visit counter
    z = zipfile.ZipFile(out / bs.ZIP)
    inner = z.read(top + "static.js").decode("utf-8")
    assert "NXGIR_STATIC = true" in inner
    assert "NXGIR_BUILD" in inner
    assert "NXGIR_DOWNLOAD" not in inner
    assert "NXGIR_COUNT" not in inner


def test_service_worker(tmp_path, files):
    import zipfile

    out = tmp_path / "site"
    tsv = tmp_path / "timeline.tsv"
    tsv.write_text(
        "2026-10-18\tBooks\t*\tJohn\t\tgrabar/john.txt\n",
        encoding="utf-8",
    )
    bs.build(out, files, tsv)
    js = (out / "static.js").read_text("utf-8")
    build = re.search(r'NXGIR_BUILD = "(\w+)"', js).group(1)
    assert 'NXGIR_SW = "sw.js"' in js
    # the worker names this build, so a new build is
    # a new cache
    sw = (out / "sw.js").read_text("utf-8")
    assert f'const BUILD = "{build}";' in sw
    assert 'BUILD = "dev"' not in sw
    # the list of what "Save for offline" keeps
    info = json.loads(
        (out / "offline.json").read_text("utf-8")
    )
    assert info["build"] == build
    paths = [p for p, _ in info["files"]]
    assert "app.js" in paths
    assert "data/book/grabar/john.txt.json" in paths
    assert "data/stats.json" in paths
    assert not any(
        p.startswith(("read/", "blog/", "sw.js"))
        or p.endswith((".zip", ".xml"))
        for p in paths
    )
    for p, n in info["files"]:
        assert (out / p).stat().st_size == n
    # the app can be installed
    assert (out / "manifest.webmanifest").is_file()
    manifest = json.loads(
        (out / "manifest.webmanifest").read_text("utf-8")
    )
    for icon in manifest["icons"]:
        assert (out / icon["src"]).is_file()
    html = (out / "index.html").read_text("utf-8")
    assert 'rel="manifest"' in html
    # not in the offline zip: no worker, no list
    z = zipfile.ZipFile(out / bs.ZIP)
    names = z.namelist()
    assert not any(
        n.endswith(("sw.js", "offline.json")) for n in names
    )
    inner = z.read("nxgir-site/static.js").decode("utf-8")
    assert "NXGIR_SW" not in inner
