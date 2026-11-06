#!/usr/bin/env python3
"""Build the published, read-only copy of the web
reader: plain files for GitHub Pages, no server.

    scripts/build-site.py [OUT]      (default: site/)

It holds the pages of web/ and, under data/, the
answers `nxgir web` would give, worked out once with
the same functions (nxgir_web.py):

    data/shelf/<folder>/index.json  /api/shelf
    data/book/<name>.json           /api/book
    data/word/<lang>/<n>.json       /api/word, the
        words of the books that the Grabar helpers
        know, spread over BUCKETS files by bucket()

The test texts of data/ are left out.

static.js tells app.js to read these files. The copy
only reads: no bookmarks, notes or editing, and where
you stopped is kept in the browser. Nothing of the
saved state on this computer goes into it.

.github/workflows/pages.yml runs this on every push
to main and publishes OUT.
"""

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import nxgir_web as web  # noqa: E402

# files the words are spread over, per language;
# as BUCKETS in web/app.js
BUCKETS = 256
# marks a folder this script made, so it may be
# emptied and made again
MARK = ".nxgir-site"


def bucket(w):
    """Which file a word is in: FNV-1a over its code
    points; as bucket() in web/app.js."""
    x = 0x811C9DC5
    for ch in w:
        x = ((x ^ ord(ch)) * 0x01000193) & 0xFFFFFFFF
    return x % BUCKETS


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(
        obj, ensure_ascii=False, separators=(",", ":")
    )
    path.write_text(text, encoding="utf-8")


def folders(files):
    """Every folder on the shelf, "" (the top) too."""
    out = {""}
    for name, _, _ in files:
        parts = name.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            out.add("/".join(parts[:i]))
    return sorted(out)


def pages(out):
    """The pages of web/, told to read the files."""
    for p in web.WEB_DIR.iterdir():
        if p.is_file():
            shutil.copy2(p, out / p.name)
        elif p.is_dir():  # fonts/
            shutil.copytree(
                p, out / p.name, dirs_exist_ok=True
            )
    (out / "static.js").write_text(
        "// the published copy: app.js reads data/\n"
        "window.NXGIR_STATIC = true;\n",
        encoding="utf-8",
    )
    index = out / "index.html"
    html = index.read_text(encoding="utf-8")
    tag = '<script src="app.js"></script>'
    if tag not in html:
        raise SystemExit("index.html: no app.js script")
    html = html.replace(
        tag, '<script src="static.js"></script>\n' + tag
    )
    index.write_text(html, encoding="utf-8")
    # GitHub Pages: serve the files as they are
    (out / ".nojekyll").write_text("")


def build(out, files):
    """Write the site for files [(name, size, path)]
    into out. Returns (books, folders, words)."""
    out = Path(out)
    if out.exists():
        if not (out / MARK).exists():
            raise SystemExit(
                f"{out} exists and was not made by"
                " build-site.py; not touching it"
            )
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / MARK).write_text("")
    pages(out)
    data = out / "data"
    with tempfile.TemporaryDirectory() as tmp:
        # an empty state: positions stay at home
        state = Path(tmp) / "state.json"
        app = web.App(files, state_path=state)
        dirs = folders(files)
        for f in dirs:
            path = data / "shelf" / f / "index.json"
            write_json(path, web.shelf(app, f))
        words = set()
        for name, _, _ in files:
            b = web.book(app, name)
            write_json(data / "book" / f"{name}.json", b)
            for line in b["lines"]:
                words.update(w.strip() for w in line[1::2])
    words.discard("")
    for lang in web.LANGS:
        found = [{} for _ in range(BUCKETS)]
        for w in sorted(words):
            d = web.word(w, lang)
            if d["abbr"] or d["meaning"]:
                found[bucket(w)][w] = [
                    d["abbr"],
                    d["meaning"],
                ]
        for n, part in enumerate(found):
            write_json(
                data / "word" / lang / f"{n}.json", part
            )
    return len(files), len(dirs), len(words)


def shelf_files():
    """The books, as the CLI finds them, without the
    test texts of data/."""
    path = HERE / "nxgir-cli.py"
    spec = importlib.util.spec_from_file_location(
        "nxgir_cli", path
    )
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return [
        f
        for f in cli.shelf_files()
        if not unpublished(f[2], cli.DATA_DIR)
    ]


def unpublished(path, data_dir):
    """True for a file in data/ (test texts)."""
    return (
        Path(path)
        .resolve()
        .is_relative_to(Path(data_dir).resolve())
    )


def size(path):
    n = sum(
        p.stat().st_size
        for p in path.rglob("*")
        if p.is_file()
    )
    return f"{n / 1e6:.1f} MB"


def main(argv):
    out = Path(argv[0]) if argv else ROOT / "site"
    books, dirs, words = build(out, shelf_files())
    print(
        f"{out}: {books} books, {dirs} folders,"
        f" {words} words, {size(out)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
